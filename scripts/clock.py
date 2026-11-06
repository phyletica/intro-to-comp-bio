"""Fit a molecular clock to a tree of SARS-CoV-2 genomes.

This script reads the maximum likelihood tree that IQ-TREE estimated from our
SARS-CoV-2 genomes, calculates how far each genome is from the root of the
tree, and fits a straight line (a molecular clock) to those distances versus
the date each genome was collected. It prints the estimated rate of evolution
and date of the common ancestor, and saves a plot of the fit.

This is the same analysis we did in Capstone Project 2, but in a plain Python
script instead of a marimo notebook, so that we can run it from the command
line (e.g., `pixi run python scripts/clock.py`).

IQ-TREE writes its (unrooted) tree with the first genome in the alignment (the
Wuhan reference genome) next to the root, which is the same rooting we used in
Capstone Project 2.
"""

import datetime
import math

import matplotlib.pyplot as plt
from scipy.stats import linregress

# --------------------------------------------------------------------------- #
# Functions
# --------------------------------------------------------------------------- #

def parse_newick(newick):
    """Convert a Newick tree string into a list of nodes in postorder.

    This is the same function we used in the phylogenetics exercise and
    Capstone Project 2.

    Args:
        newick (str): A tree in Newick format, such as "((A:0.1,B:0.2):0.3,C:0.4);".

    Returns:
        list[dict]: One dictionary per node, with the keys "name" (str),
            "children" (list of the indices of the node's children), and
            "length" (float, the length of the branch to the node's parent, or
            None for the root). Children always come before their parents, so
            the root is the last node.
    """
    newick = newick.strip()
    if newick.endswith(";"):
        newick = newick[:-1]
    nodes = []
    position = 0

    def read_name_and_length():
        nonlocal position
        start = position
        while position < len(newick) and newick[position] not in ":,()":
            position += 1
        name = newick[start:position].strip()
        length = None
        if position < len(newick) and newick[position] == ":":
            position += 1
            start = position
            while position < len(newick) and newick[position] not in ",()":
                position += 1
            length = float(newick[start:position])
        return name, length

    def read_subtree():
        nonlocal position
        children = []
        if newick[position] == "(":
            position += 1
            while True:
                children.append(read_subtree())
                if newick[position] == ",":
                    position += 1
                elif newick[position] == ")":
                    position += 1
                    break
                else:
                    raise ValueError(f"Unexpected character at position {position}")
        name, length = read_name_and_length()
        nodes.append({"name": name, "children": children, "length": length})
        return len(nodes) - 1

    read_subtree()
    nodes[-1]["length"] = None
    return nodes


def root_to_tip_distances(tree):
    """Calculate the distance from the root of a tree to each of its tips.

    Returns:
        dict[str, float]: Maps the name of each tip to the sum of the branch
            lengths on the path from the root to that tip.
    """
    parents = [None] * len(tree)
    for index, node in enumerate(tree):
        for child in node["children"]:
            parents[child] = index
    distances = [0.0] * len(tree)
    for index in reversed(range(len(tree) - 1)):
        distances[index] = distances[parents[index]] + tree[index]["length"]
    tip_distances = {}
    for index, node in enumerate(tree):
        if len(node["children"]) == 0:
            tip_distances[node["name"]] = distances[index]
    return tip_distances


def date_to_year(date):
    """Convert a date like "2021-07-24" (or "2021-07") to a decimal year.

    If the day is missing, the middle of the month is used.
    """
    parts = date.split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = 15
    if len(parts) > 2:
        day = int(parts[2])
    day_of_year = datetime.date(year, month, day).timetuple().tm_yday
    days_in_year = 365
    if datetime.date(year, 12, 31).timetuple().tm_yday == 366:
        days_in_year = 366
    return year + (day_of_year - 0.5) / days_in_year


def year_to_date(decimal_year):
    """Convert a decimal year (like 2021.5) back into a date (like "2021-07-02")."""
    year = int(math.floor(decimal_year))
    start = datetime.date(year, 1, 1)
    days_in_year = (datetime.date(year + 1, 1, 1) - start).days
    day = int((decimal_year - year) * days_in_year)
    return (start + datetime.timedelta(days = day)).isoformat()


def fit_clock(years, substitutions):
    """Fit a molecular clock (a straight line) to substitutions versus time.

    Returns:
        tuple[float, float, float]: The rate (substitutions per year), the year
            at which the line reaches zero substitutions (the date of the
            ancestor), and the R-squared of the fit.
    """
    fit = linregress(years, substitutions)
    rate = fit.slope
    ancestor_year = -fit.intercept / fit.slope
    r_squared = fit.rvalue ** 2
    return float(rate), float(ancestor_year), float(r_squared)


def plot_clock(years, substitutions, lineages, rate, ancestor_year, title = ""):
    """Plot substitutions versus year, colored by lineage, with a fitted clock.

    This is the same function we used in Capstone Project 2.

    Returns:
        matplotlib.figure.Figure: The figure.
    """
    # A color for each lineage (matplotlib knows many colors by name)
    lineage_colors = {
        "Wuhan": "black",
        "B.1": "gray",
        "Alpha": "tab:blue",
        "Gamma": "tab:green",
        "Delta": "tab:orange",
        "Omicron": "tab:red",
    }

    # Step 1: Make a figure (the whole image) and axes (where we draw the data)
    figure, axes = plt.subplots(figsize = (8, 5))

    # Step 2a: Draw the points, one lineage at a time
    for lineage, color in lineage_colors.items():
        lineage_years = []
        lineage_substitutions = []
        for year, subs, genome_lineage in zip(years, substitutions, lineages):
            if genome_lineage == lineage:
                lineage_years.append(year)
                lineage_substitutions.append(subs)
        if len(lineage_years) == 0:
            continue
        axes.scatter(lineage_years, lineage_substitutions, color = color, s = 50,
                     edgecolor = "white", label = lineage, zorder = 3)

    # Step 2b: Draw the fitted line, from the ancestor to the latest genome
    line_years = [ancestor_year, max(years)]
    line_substitutions = [0.0, rate * (max(years) - ancestor_year)]
    axes.plot(line_years, line_substitutions, color = "black", linestyle = "--",
              label = f"Clock: {rate:.1f} substitutions per year")

    # Step 2c: Mark the date of the ancestor, where the line reaches zero
    axes.scatter([ancestor_year], [0], color = "gold", marker = "*", s = 300,
                 edgecolor = "black", zorder = 4,
                 label = f"Ancestor: {year_to_date(ancestor_year)}")

    # Step 3: Label everything
    axes.set_xlabel("Year the genome was collected")
    axes.set_ylabel("Substitutions from the root")
    axes.set_title(title)
    axes.legend(loc = "upper left")
    axes.grid(alpha = 0.3)

    # Step 4: Return the figure
    figure.tight_layout()
    return figure

if __name__ == "__main__":
    # ----------------------------------------------------------------------- #
    # Settings
    # ----------------------------------------------------------------------- #
    
    # The tree estimated by IQ-TREE, and where to save the plot
    tree_path = "results/tree.treefile"
    figure_path = "results/clock.png"
    
    # The number of sites in the alignment, to convert distances from
    # substitutions per site to substitutions per genome
    genome_length = 29903
    
    # Lineages to leave out of the clock (e.g., ["Omicron"])
    excluded_lineages = []

    # ----------------------------------------------------------------------- #
    # The analysis
    # ----------------------------------------------------------------------- #
    
    # Read the tree estimated by IQ-TREE
    with open(tree_path) as tree_file:
        tree = parse_newick(tree_file.read())
    
    # Each tip's name is the genome's description line from the FASTA file,
    # with four parts separated by "|": the lineage's common name, its Pango
    # lineage, its GenBank accession number, and the date it was collected
    # (e.g., "Delta|B.1.617.2|OL524349.1|2021-07-24")
    distances = root_to_tip_distances(tree)
    years = []
    substitutions = []
    lineages = []
    for name, distance in distances.items():
        lineage, pango_lineage, accession, date = name.split("|")
        if lineage in excluded_lineages:
            continue
        years.append(date_to_year(date))
        substitutions.append(distance * genome_length)
        lineages.append(lineage)
    
    # Fit the clock
    rate, ancestor_year, r_squared = fit_clock(years, substitutions)
    
    # Report the results
    title = f"Molecular clock fit to {len(years)} genomes"
    if len(excluded_lineages) > 0:
        title += f" (without {', '.join(excluded_lineages)})"
    print(title)
    print(f"  Rate: {rate:.1f} substitutions per genome per year "
          + f"({rate / genome_length:.2e} per site per year)")
    print(f"  Date of the ancestor: {year_to_date(ancestor_year)} ({ancestor_year:.2f})")
    print(f"  R-squared: {r_squared:.2f}")
    
    # Plot the clock and save the plot
    figure = plot_clock(years, substitutions, lineages, rate, ancestor_year, title = title)
    figure.savefig(figure_path, dpi = 150)
    print(f"  Saved the plot to {figure_path}")
