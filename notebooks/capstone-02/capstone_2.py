# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.0",
#     "matplotlib",
#     "numpy",
#     "scipy",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    # These imports are available to every cell and function in the notebook
    import collections
    import datetime
    import math
    import random

    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.linalg import expm
    from scipy.optimize import minimize_scalar
    from scipy.stats import linregress

    # The four DNA bases
    BASES = "ACGT"


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Capstone Project 2: Dating the ancestor of SARS-CoV-2

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The objective

    In the phylogenetics exercise, you used likelihood to choose among trees and to
    reconstruct the genomes of ancestors of SARS-CoV-2 lineages.
    In this project, you will answer two new questions:

    1.  **Does a simpler method, *parsimony*, agree with likelihood about the tree?**
    2.  **How fast does SARS-CoV-2 evolve, and when did the common ancestor of the
        genomes we've been working with live?**

    To answer them, you will:

    1.  Write ***Fitch's algorithm***, which counts the fewest substitutions a tree
        needs to explain the data, and use it to compare trees
    2.  Calculate how far (evolutionarily) each genome is from the root of a tree of
        all 24 genomes
    3.  Fit a ***molecular clock*** to those distances and the dates the genomes
        were sampled, to estimate the rate of evolution and the date of the
        ancestor
    4.  Find out what happens when one lineage doesn't follow the clock

    /// attention | This project is graded for correctness
    Unlike the lab exercises, which are graded for effort, this project is graded
    for correctness.
    The number of points each challenge is worth is listed in its heading.
    Each code challenge has a test cell to help you check your work.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tools from previous exercises

    The functions below are from the phylogenetics exercise.
    **You do not need to edit any of them**, but you will use some of them later
    in the notebook.
    As a reminder:

    -   `parse_newick(newick)` converts a Newick tree string into a list of nodes in
        postorder (every node comes after its children, so the root is last); each
        node is a dictionary with the keys `"name"`, `"children"` (a list of the
        indices of the node's children), and `"length"`
    -   `get_tip_names(tree)` returns the names of the tips of a tree
    -   `draw_tree(tree)` draws a tree; the input is a list of nodes (dictionaries)
        in postorder, like `parse_newick` returns
    -   `count_site_patterns(alignment, tip_names)` counts how many times each
        unique column (site pattern) occurs in an alignment
    -   `tree_log_likelihood(tree, alignment, rate_matrix, base_frequencies)`
        calculates the log-likelihood of a whole alignment on a tree, using
        Felsenstein's pruning algorithm (the functions it uses are also below)

    The functions for the pruning algorithm use the NumPy shortcut (`P @ L`) from
    the optional drop-down in the last exercise, so that they run faster.
    """)
    return


@app.function
def parse_newick(newick):
    """Convert a Newick tree string into a list of nodes in postorder.

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
        # Remove the semi-colon at the end of the newick tree string
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
    # The root node has no branch length, because it has no parent
    nodes[-1]["length"] = None
    return nodes


@app.function
def get_tip_names(tree):
    """Get the names of the tips of a tree, in the order they appear in the tree.

    Args:
        tree (list[dict]): A list of nodes in postorder, as returned by
            `parse_newick`.

    Returns:
        list[str]: The names of the nodes that have no children.

    Examples:
        >>> get_tip_names(parse_newick("((A:0.1,B:0.2):0.3,C:0.4);"))
        ['A', 'B', 'C']
    """
    tip_names = []
    for node in tree:
        if len(node["children"]) == 0:
            tip_names.append(node["name"])
    return tip_names


@app.function
def draw_tree(tree, title = "", label_internal_nodes = True,
              tip_font_size = 11, height_per_tip = 0.45):
    """Draw a tree (a list of nodes in postorder) with matplotlib.

    Branch lengths are drawn to scale, from the root at the left to the tips
    at the right.

    Returns:
        matplotlib.figure.Figure: The figure.
    """
    number_of_nodes = len(tree)
    parent = [None] * number_of_nodes
    for index, node in enumerate(tree):
        for child in node["children"]:
            parent[child] = index
    x = [0.0] * number_of_nodes
    for index in reversed(range(number_of_nodes - 1)):
        x[index] = x[parent[index]] + tree[index]["length"]
    y = [0.0] * number_of_nodes
    next_tip_y = 0
    for index, node in enumerate(tree):
        if len(node["children"]) == 0:
            y[index] = next_tip_y
            next_tip_y += 1
        else:
            y[index] = sum(y[child] for child in node["children"]) / len(node["children"])

    figure, axes = plt.subplots(figsize = (7, height_per_tip * next_tip_y + 1))
    max_x = max(x)
    for index, node in enumerate(tree):
        if parent[index] is not None:
            axes.plot([x[parent[index]], x[index]], [y[index], y[index]],
                      color = "black", linewidth = 1.5)
        if node["children"]:
            child_ys = [y[child] for child in node["children"]]
            axes.plot([x[index], x[index]], [min(child_ys), max(child_ys)],
                      color = "black", linewidth = 1.5)
            if label_internal_nodes and node["name"]:
                axes.text(x[index] + 0.01 * max_x, y[index], node["name"],
                          ha = "left", va = "center", fontsize = 9,
                          color = "firebrick",
                          bbox = {"facecolor": "white", "edgecolor": "none",
                                  "pad": 1})
        else:
            axes.text(x[index] + 0.01 * max_x, y[index], node["name"],
                      va = "center", fontsize = tip_font_size)
    axes.set_xlim(-0.02 * max_x, 1.35 * max_x)
    axes.set_ylim(-0.7, next_tip_y - 0.3)
    axes.invert_yaxis()
    axes.set_yticks([])
    for side in ["left", "right", "top"]:
        axes.spines[side].set_visible(False)
    axes.set_xlabel("Distance from the root (expected substitutions per site)")
    axes.set_title(title)
    figure.tight_layout()
    return figure


@app.function
def count_site_patterns(alignment, tip_names):
    """Count how many times each unique column occurs in an alignment.

    Anything other than A, C, G, or T is treated as missing ("N").

    Args:
        alignment (dict[str, str]): Maps each sequence name to its aligned
            sequence.
        tip_names (list[str]): The sequences to include, in order.

    Returns:
        collections.Counter: Maps each pattern (a tuple of bases, one per tip,
            in the order of `tip_names`) to the number of times it occurs.
    """
    length = len(alignment[tip_names[0]])
    patterns = collections.Counter()
    for index in range(length):
        column = []
        for name in tip_names:
            base = alignment[name][index]
            if base not in BASES:
                base = "N"
            column.append(base)
        patterns[tuple(column)] += 1
    return patterns


@app.function
def get_transition_probabilities(rate_matrix, t):
    """Calculate the transition probability matrix P(t) = e^(Qt).

    Args:
        rate_matrix (numpy.ndarray): A 4-by-4 rate matrix, Q.
        t (float): Time, in expected substitutions per site.

    Returns:
        numpy.ndarray: A 4-by-4 array where row i, column j is the probability
            that a site that starts as base i is base j after time t.
    """
    return expm(rate_matrix * t)


@app.function
def get_transition_matrices(tree, rate_matrix):
    """Calculate P(t) for the branch above every node in a tree.

    Args:
        tree (list[dict]): A list of nodes in postorder.
        rate_matrix (numpy.ndarray): A 4-by-4 rate matrix, Q.

    Returns:
        list: One 4-by-4 NumPy array per node, in the same order as `tree`,
            for the branch between the node and its parent; the entry for the
            root is None.
    """
    transition_matrices = []
    for node in tree:
        if node["length"] is None:
            transition_matrices.append(None)
        else:
            transition_matrices.append(
                get_transition_probabilities(rate_matrix, node["length"])
            )
    return transition_matrices


@app.function
def tip_likelihoods(base):
    """Get the conditional likelihoods of a tip with the given base.

    Args:
        base (str): The base at the tip. "A", "C", "G", or "T"; anything else
            (such as "-" or "N") is treated as missing data.

    Returns:
        numpy.ndarray: Four numbers, in the order of BASES ("ACGT"): 1.0 for
            the observed base and 0.0 for the others, or 1.0 for all four if
            the base is missing.

    Examples:
        >>> tip_likelihoods("G")
        array([0., 0., 1., 0.])
        >>> tip_likelihoods("-")
        array([1., 1., 1., 1.])
    """
    likelihoods = np.zeros(4)
    if base in BASES:
        likelihoods[BASES.index(base)] = 1.0
    else:
        likelihoods.fill(1.0)
    return likelihoods


@app.function
def combine_children(child_likelihoods, child_transition_matrices):
    """Calculate the conditional likelihoods of a parent from those of its children.

    Args:
        child_likelihoods (list[numpy.ndarray]): The conditional likelihoods (four
            numbers, in the order of BASES) of each child.
        child_transition_matrices (list[numpy.ndarray]): The 4-by-4 transition
            probability matrix for the branch above each child, in the same
            order as `child_likelihoods`.

    Returns:
        numpy.ndarray: The conditional likelihoods of the parent: for each base i,
            the product over children of sum_j P[i, j] * likelihoods[j].
    """
    parent_likelihoods = np.ones(4)
    for likelihoods, P in zip(child_likelihoods, child_transition_matrices):
        parent_likelihoods *= P @ likelihoods
    return parent_likelihoods


@app.function
def get_root_likelihoods(tree, site_bases, transition_matrices):
    """Calculate the conditional likelihoods at the root of a tree for one site.

    Args:
        tree (list[dict]): A list of nodes in postorder.
        site_bases (dict[str, str]): Maps the name of each tip to its base at
            this site.
        transition_matrices (list): The transition probability matrix for the
            branch above each node, as returned by `get_transition_matrices`.

    Returns:
        numpy.ndarray: The conditional likelihoods (four numbers, in the order of
            BASES) of the root.
    """
    node_likelihoods = []
    for node in tree:
        if len(node["children"]) == 0:
            node_likelihoods.append(tip_likelihoods(site_bases[node["name"]]))
        else:
            child_likelihoods = []
            child_matrices = []
            for child in node["children"]:
                child_likelihoods.append(node_likelihoods[child])
                child_matrices.append(transition_matrices[child])
            node_likelihoods.append(
                combine_children(child_likelihoods, child_matrices)
            )
    return node_likelihoods[-1]


@app.function
def site_log_likelihood(tree, site_bases, transition_matrices, base_frequencies):
    """Calculate the log-likelihood of one site on a tree.

    Args:
        tree (list[dict]): A list of nodes in postorder.
        site_bases (dict[str, str]): Maps the name of each tip to its base at
            this site.
        transition_matrices (list): The transition probability matrix for the
            branch above each node, as returned by `get_transition_matrices`.
        base_frequencies (dict[str, float]): The frequency of each base.

    Returns:
        float: The natural log of the likelihood of the site.
    """
    root_likelihoods = get_root_likelihoods(tree, site_bases,
                                            transition_matrices)
    likelihood = 0.0
    for i in range(4):
        likelihood += base_frequencies[BASES[i]] * root_likelihoods[i]
    return math.log(likelihood)


@app.function
def tree_log_likelihood(tree, alignment, rate_matrix, base_frequencies):
    """Calculate the log-likelihood of a whole alignment on a tree.

    Args:
        tree (list[dict]): A list of nodes in postorder.
        alignment (dict[str, str]): Maps the name of each tip to its aligned
            sequence.
        rate_matrix (numpy.ndarray): A 4-by-4 rate matrix, Q.
        base_frequencies (dict[str, float]): The frequency of each base.

    Returns:
        float: The log-likelihood: the sum of the log-likelihoods of all sites.
    """
    tip_names = get_tip_names(tree)
    patterns = count_site_patterns(alignment, tip_names)
    transition_matrices = get_transition_matrices(tree, rate_matrix)
    log_like = 0.0
    for pattern, count in patterns.items():
        site_bases = dict(zip(tip_names, pattern))
        log_like += count * site_log_likelihood(
            tree, site_bases, transition_matrices, base_frequencies
        )
    return log_like


@app.function
def parse_fasta_url(fasta_url):
    """Download a FASTA file from a URL and parse it into a dictionary.

    Args:
        fasta_url (str): The URL of a FASTA file.

    Returns:
        dict[str, str]: Maps the description line of each record, with the
            leading ">" removed, to that record's sequence.
    """
    import urllib.request

    sequences = {}
    current_name = None
    current_seq = ""
    with urllib.request.urlopen(fasta_url) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            if line[0] == ">":
                if current_name is not None:
                    sequences[current_name] = current_seq
                current_name = line[1:].strip()
                current_seq = ""
            else:
                current_seq += line.upper()
    if current_name is not None:
        sequences[current_name] = current_seq
    return sequences


@app.cell
def _():
    # The JC rate matrix (rows and columns are A, C, G, T)
    jc_rate_matrix = np.array([
        [-1.0, 1 / 3, 1 / 3, 1 / 3],
        [1 / 3, -1.0, 1 / 3, 1 / 3],
        [1 / 3, 1 / 3, -1.0, 1 / 3],
        [1 / 3, 1 / 3, 1 / 3, -1.0],
    ])
    equal_frequencies = {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}
    return equal_frequencies, jc_rate_matrix


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The data

    The next cell downloads the same alignment of 24 SARS-CoV-2 genomes we used
    in the phylogenetics exercise.
    Each genome's description line has four parts, separated by `|`:

    1.  The lineage's common name
    2.  Its Pango lineage
    3.  Its GenBank accession number
    4.  The date the sample was collected

    The next Python cell stores:

    -   `all_genomes`: A dictionary of all 24 genomes, keyed by the common name
        and accession number (*e.g.*, `"Delta_OL524349.1"`)
    -   `collection_dates`: A dictionary of the date each genome was collected
        (*e.g.*, `"2021-07-24"`), keyed by the same names
    -   `lineage_of`: A dictionary of the common name of each genome's lineage
        (*e.g.*, `"Delta"`), keyed by the same names
    -   `four_genomes`: The four genomes we compared in the phylogenetics exercise
        (Wuhan, Delta, Alpha, and Omicron), keyed by their common names

    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(mo):
    _url = (
        "https://raw.githubusercontent.com/phyletica/intro-to-comp-bio/"
        + "refs/heads/main/notebooks/data/SARS-CoV-2.nextclade.aligned.fasta"
    )
    _raw_genomes = parse_fasta_url(_url)

    all_genomes = {}
    collection_dates = {}
    lineage_of = {}
    for _description, _sequence in _raw_genomes.items():
        _name, _lineage, _accession, _date = _description.split("|")
        _key = f"{_name}_{_accession}"
        all_genomes[_key] = _sequence
        collection_dates[_key] = _date
        lineage_of[_key] = _name

    # The same four genomes we compared in the phylogenetics exercise
    _four_keys = {
        "Wuhan": "Wuhan_NC_045512.2",
        "Delta": "Delta_OL524349.1",
        "Alpha": "Alpha_OY916467.1",
        "Omicron": "Omicron_OP349650.1",
    }
    four_genomes = {}
    for _name, _key in _four_keys.items():
        four_genomes[_name] = all_genomes[_key]

    _counts = collections.Counter(lineage_of.values())
    mo.md(
        f"Downloaded {len(all_genomes)} genomes of "
        + f"{len(all_genomes['Wuhan_NC_045512.2']):,} sites each: "
        + ", ".join(f"{_count} {_name}" for _name, _count in _counts.items())
    )
    return all_genomes, collection_dates, four_genomes, lineage_of


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: Parsimony and Fitch's algorithm

    ***Maximum parsimony*** chooses the tree that needs the **fewest
    substitutions** to explain the data.
    To use it, we need a way to count the fewest substitutions a tree needs at a
    site.
    ***Fitch's algorithm*** (Fitch 1971) does this by working from the tips to the
    root, in postorder, just like the pruning algorithm.
    But instead of four conditional likelihoods, each node gets a ***set*** of
    bases: The bases it could have, if the tree has the fewest possible
    substitutions below it.

    Fitch's algorithm has ***two rules*** (for trees where every internal node has
    two children):

    1.  **At a tip**, the set is just the base we observed (*e.g.*, `{"A"}`).
        If the base is missing (*e.g.*, `-` or `N`), the set is all four bases,
        `{"A", "C", "G", "T"}`, because the tip could have any of them.
    2.  **At an internal node**, compare the sets of its two children:
        -   If they have any bases in common (the ***intersection*** of the two
            sets is not empty), the node's set is the bases they have in common,
            and no substitution is needed
        -   If they have no bases in common, the node's set is all the bases in
            either set (the ***union*** of the two sets), and we count **one**
            substitution

    The number of substitutions counted in this way, from the tips to the root, is
    the fewest substitutions the tree needs to explain the site.

    ## An example

    Here is Fitch's algorithm on one site of our example tree from the last
    exercise, `((Human,Chimp)Primates,(Mouse,Rat)Rodents)Root`, where Human and
    Chimp have `A`, Mouse has `G`, and Rat has `C`:

    | Node | Children's sets | In common? | Node's set | Substitutions so far |
    |:--|:--|:-:|:--|:-:|
    | Human | | | `{A}` | 0 |
    | Chimp | | | `{A}` | 0 |
    | Primates | `{A}` and `{A}` | Yes | `{A}` | 0 |
    | Mouse | | | `{G}` | 0 |
    | Rat | | | `{C}` | 0 |
    | Rodents | `{G}` and `{C}` | No | `{C, G}` | 1 |
    | Root | `{A}` and `{C, G}` | No | `{A, C, G}` | 2 |

    So, this tree needs at least 2 substitutions to explain this site (for
    example, `A` at the root, with one substitution from `A` to `G` on the way to
    Mouse and one from `A` to `C` on the way to Rat).

    ## Sets in Python

    A Python ***set*** is like a list, except that it has no order and can't hold
    duplicate items.
    Sets are perfect for Fitch's algorithm, because Python can find the
    intersection and union of two sets for us.
    I recommend you open marimo's "Scratchpad" and type these examples to get a feel
    for how sets work in Python.

    ```python
    set_1 = {"A", "G"}
    set_2 = {"G", "T"}
    set_1 & set_2       # Intersection: {"G"}
    set_1 | set_2       # Union: {"A", "G", "T"}
    {"A"} & {"C"}       # An empty set: set()
    len({"A"} & {"C"})  # 0, because the intersection is empty
    set("ACGT")         # {"A", "C", "G", "T"}
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 1: Fitch's algorithm (4 points) </font>

    Complete the `fitch_site` function below, which returns the fewest
    substitutions a tree needs to explain one site.
    Like `get_root_likelihoods` from the last exercise, it loops over the nodes of
    the tree in postorder, and stores something for every node in a list, in the
    same order as the nodes.
    This time, it stores a set of bases for each node in the `node_sets` list.
    A recipe:

    1.  Loop over every `node` in `tree`
    2.  If the node is a tip (it has no children), get its base with
        `site_bases[node["name"]]`; if the base is one of the four `BASES`, append
        the set `{base}` to `node_sets`; otherwise, append `set(BASES)`
    3.  Otherwise, get the sets of its two children:
        `left_set = node_sets[node["children"][0]]` and
        `right_set = node_sets[node["children"][1]]`
    4.  If the intersection of `left_set` and `right_set` is not empty, append the
        intersection to `node_sets`
    5.  Otherwise, append the union of `left_set` and `right_set` to `node_sets`,
        and add 1 to `number_of_substitutions`

    /// tip
    An empty set counts as `False` in an `if` statement, and a set with anything in
    it counts as `True`.
    So, after `common = left_set & right_set`, you can write `if common:`.
    ///
    """)
    return


@app.function
def fitch_site(tree, site_bases):
    """Count the fewest substitutions a tree needs at one site (Fitch's algorithm).

    Args:
        tree (list[dict]): A list of nodes in postorder, where every internal
            node has exactly two children.
        site_bases (dict[str, str]): Maps the name of each tip to its base at
            this site.

    Returns:
        int: The fewest substitutions the tree needs to explain the site.

    Examples:
        >>> tree = parse_newick("((A,B),(C,D));")
        >>> fitch_site(tree, {"A": "A", "B": "A", "C": "G", "D": "G"})
        1
    """
    node_sets = []
    number_of_substitutions = 0
    # Add your code here!
    return number_of_substitutions


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function on our example tree.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _example_tree = parse_newick(
        "((Human:0.1,Chimp:0.1)Primates:0.3,(Mouse:0.2,Rat:0.2)Rodents:0.2)Root;"
    )
    _fitch_test_cases = [
        ({"Human": "A", "Chimp": "A", "Mouse": "G", "Rat": "C"}, 2),
        ({"Human": "A", "Chimp": "A", "Mouse": "G", "Rat": "G"}, 1),
        ({"Human": "A", "Chimp": "A", "Mouse": "A", "Rat": "A"}, 0),
        ({"Human": "A", "Chimp": "A", "Mouse": "A", "Rat": "T"}, 1),
        ({"Human": "A", "Chimp": "G", "Mouse": "A", "Rat": "G"}, 2),
        ({"Human": "A", "Chimp": "C", "Mouse": "G", "Rat": "T"}, 3),
        ({"Human": "A", "Chimp": "-", "Mouse": "N", "Rat": "A"}, 0),
        ({"Human": "-", "Chimp": "-", "Mouse": "-", "Rat": "-"}, 0),
    ]
    _fitch_failures = []
    for _site_bases, _expected in _fitch_test_cases:
        try:
            _found = fitch_site(_example_tree, _site_bases)
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
        if _found != _expected:
            _fitch_failures.append(f"  {_site_bases}: expected {_expected}, got {_found}")

    fitch_site_works = len(_fitch_failures) == 0
    if fitch_site_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, fitch_site failed these cases:\n" + "\n".join(_fitch_failures))
    return (fitch_site_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 2: The parsimony score of a tree (2 points) </font>

    The ***parsimony score*** of a tree is the fewest substitutions it needs to
    explain **all** of the sites in an alignment: The sum of `fitch_site` over
    every site.
    Like `tree_log_likelihood`, we can save time by counting site patterns, and
    calculating each pattern's score only once.

    Complete the `parsimony_score` function below.
    A recipe:

    1.  Get the names of the tips of the tree with `get_tip_names`
    2.  Count the site patterns with
        `count_site_patterns(alignment, tip_names)`, which returns a dictionary
        (technically a `collections.Counter`, which is a dictionary subclass)
        that maps each pattern to the number of times it occurs
    3.  Loop over each `pattern` and its `count` in the patterns returned by
        `count_site_patterns`, and for each pattern:
        1.  Make a dictionary of the base of each tip with
            `site_bases = dict(zip(tip_names, pattern))`
        2.  Multiply `count` by the number returned by `fitch_site`
        3.  Add the product to `score`

    /// tip
    1.  Look at the `tree_log_likelihood` function in the "Tools" section at the top
        of the notebook: Your function will look a lot like it!
    2.  You can loop over the items in a dictionary (or `collections.Counter`
        dictionary subclass) in two ways.
        You can loop over the keys and then look up the values:

        ```python
        d = {"A" : 1, "B" : 2, "C" : 3}
        for key in d:
            value = d[key]
            print(f"{key} : {value}")
        ```

        Or, you can loop over the keys and values at once by using the `.items()`
        method of dictionaries:

        ```python
        d = {"A" : 1, "B" : 2, "C" : 3}
        for key, value in d.items():
            print(f"{key} : {value}")
        ```
    ///
    """)
    return


@app.function
def parsimony_score(tree, alignment):
    """Count the fewest substitutions a tree needs to explain an alignment.

    Args:
        tree (list[dict]): A list of nodes in postorder, where every internal
            node has exactly two children.
        alignment (dict[str, str]): Maps the name of each tip to its aligned
            sequence.

    Returns:
        int: The parsimony score: the sum of `fitch_site` over every site.
    """
    score = 0
    # Add your code here!
    return score


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(fitch_site_works):
    parsimony_score_works = False
    if not fitch_site_works:
        print("Get fitch_site working first!")
    else:
        _example_tree = parse_newick(
            "((Human:0.1,Chimp:0.1)Primates:0.3,(Mouse:0.2,Rat:0.2)Rodents:0.2)Root;"
        )
        _score_test_cases = [
            ({"Human": "AAAA", "Chimp": "ACAG", "Mouse": "GGA-", "Rat": "GTAA"}, 5),
            ({"Human": "AAAAAA", "Chimp": "AAAAAA", "Mouse": "GGGGGG",
              "Rat": "GGGGGG"}, 6),
            ({"Human": "ACGT", "Chimp": "ACGT", "Mouse": "ACGT", "Rat": "ACGT"}, 0),
        ]
        _score_failures = []
        for _alignment, _expected in _score_test_cases:
            try:
                _found = parsimony_score(_example_tree, _alignment)
            except Exception as _error:
                _found = f"an error ({type(_error).__name__}: {_error})"
            if _found != _expected:
                _score_failures.append(
                    f"  {_alignment}: expected {_expected}, got {_found}"
                )
        parsimony_score_works = len(_score_failures) == 0
        if parsimony_score_works:
            print("Yay, your function passed the test!")
        else:
            print("Sorry, parsimony_score failed these cases:\n"
                  + "\n".join(_score_failures))
    return (parsimony_score_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Parsimony vs. likelihood

    The next cell calculates the parsimony score of each of the three trees for
    four genomes (Wuhan, Delta, Alpha, and Omicron) from the phylogenetics
    exercise, using your `parsimony_score` function.
    It also calculates each tree's log-likelihood under the JC model, with the
    same branch lengths we used in that exercise.

    Fitch's algorithm needs every internal node to have two children, so we give
    it ***rooted*** versions of the three trees (*e.g.*,
    `((Wuhan,Delta),(Alpha,Omicron))`).
    Each one has the same unrooted topology as the tree we used for likelihood,
    and the parsimony score of a tree doesn't depend on where the root is.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(
    equal_frequencies,
    four_genomes,
    jc_rate_matrix,
    mo,
    parsimony_score_works,
):
    mo.stop(
        not parsimony_score_works,
        mo.md("***Waiting — Get your `parsimony_score` function working first.***"),
    )

    # Rooted versions of the three trees, for Fitch's algorithm
    _rooted_trees = {
        "1: (Wuhan, Delta), (Alpha, Omicron)": "((Wuhan,Delta),(Alpha,Omicron));",
        "2: (Wuhan, Alpha), (Delta, Omicron)": "((Wuhan,Alpha),(Delta,Omicron));",
        "3: (Wuhan, Omicron), (Delta, Alpha)": "((Wuhan,Omicron),(Delta,Alpha));",
    }
    # The same trees, unrooted, with their maximum likelihood branch lengths
    _unrooted_trees = {
        "1: (Wuhan, Delta), (Alpha, Omicron)":
            "(Wuhan:0.000178972,Delta:0.000929634,"
            + "(Alpha:0.000705813,Omicron:0.00170239):0.000134645);",
        "2: (Wuhan, Alpha), (Delta, Omicron)":
            "(Wuhan:0.000216696,Alpha:0.00079132,"
            + "(Delta:0.000915385,Omicron:0.0017608):0.0000348304);",
        "3: (Wuhan, Omicron), (Delta, Alpha)":
            "(Wuhan:0.000220262,Omicron:0.00179091,"
            + "(Delta:0.000946957,Alpha:0.000793881):0.00000001);",
    }
    _rows = []
    for _label in _rooted_trees:
        _score = parsimony_score(parse_newick(_rooted_trees[_label]), four_genomes)
        _log_like = tree_log_likelihood(
            parse_newick(_unrooted_trees[_label]), four_genomes, jc_rate_matrix,
            equal_frequencies,
        )
        _rows.append(f"| {_label} | {_score} | {_log_like:.2f} |")
    mo.md(
        "| Tree | Parsimony score (substitutions) | Log-likelihood (JC) |\n"
        + "|:--|--:|--:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 3: Do parsimony and likelihood agree? (3 points) </font>

    In the phylogenetics exercise, we found the four "two pairs" sites, where
    the four genomes share bases in two pairs:

    | Position | Wuhan | Delta | Alpha | Omicron | Groups the pairs as in |
    |--:|:-:|:-:|:-:|:-:|:-:|
    | 22,995 | C | A | C | A | Tree 2 |
    | 23,063 | A | A | T | T | Tree 1 |
    | 28,882 | G | G | A | A | Tree 1 |
    | 28,883 | G | G | C | C | Tree 1 |

    Double-click this cell and answer the questions below.

    1.  **Which tree has the best (lowest) parsimony score? Do parsimony and
        likelihood agree about which tree is best?**

        **Answer**:

    2.  **Tree 2's parsimony score is exactly 2 higher than Tree 1's, and Tree 3's
        is exactly 3 higher. Use the four "two pairs" sites to explain why.
        (Hint: How many substitutions does each of these sites need on the tree
        that groups its pairs, and on the other two trees?)**

        **Answer**:

    3.  **In the phylogenetics exercise, we saw that *every* site affects the
        likelihood of each tree, through the branch lengths. Is that true of the
        parsimony score? Which sites does parsimony use to choose among trees?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 2: How far is each genome from the root?

    ## A molecular clock

    If substitutions accumulate at a roughly constant rate (a ***molecular
    clock***), then genomes sampled **later** should have had more time to
    evolve since their common ancestor, and so they should be **farther** from the
    root of the tree.
    If we plot each genome's distance from the root against the date it was
    collected, we should see a straight line:

    -   The ***slope*** of the line is the **rate** of evolution: the number of
        substitutions per year
    -   Where the line reaches a distance of **zero** is the **date of the common
        ancestor** (the root of the tree), because that's when the genomes had not
        yet started to diverge

    This is called a ***root-to-tip regression***, and it was one of the first
    analyses researchers ran on SARS-CoV-2 genomes early in the pandemic.

    ## The tree of all 24 genomes

    The next cell defines and draws the maximum likelihood tree of all 24 genomes,
    which I estimated with IQ-TREE under the HKY model of sequence evolution.
    The tree is rooted where the Wuhan reference genome attaches to the rest of
    the tree, which is a reasonable place for the root, because the Wuhan genome
    was sampled first.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _():
    tree_of_24 = parse_newick(
        "(Wuhan_NC_045512.2:0.000133778,(((B.1_MT358705.1:0.000100331,"
        + "B.1_MZ472100.1:0.000133778):0.000001,B.1_PV612058.1:0.000066886)"
        + ":0.000001,B.1_OK075089.1:0.000334491):0.000066886,"
        + "(((Delta_OL524349.1:0.0000334422,Delta_OL524558.1:0.000066886)"
        + ":0.00036779,(Delta_OK189634.1:0.000343097,(Delta_ON005388.1:0.000401407,"
        + "Delta_LC643044.1:0.000301035):0.000384501):0.0000717863):0.000539336,"
        + "(((Alpha_MZ023129.1:0.000301035,((Alpha_OY916467.1:0.000066886,"
        + "Alpha_OY942636.1:0.0000334422):0.000001,(Alpha_MZ233978.1:0.000234127,"
        + "Alpha_OY953412.1:0.000234127):0.0000334422):0.000001):0.000636951,"
        + "((((Omicron_OP349650.1:0.000125001,Omicron_ON383275.1:0.000100331)"
        + ":0.000001,Omicron_ON532287.1:0.000133778):0.0000418346,"
        + "Omicron_ON947472.1:0.0000334422):0.000001,Omicron_ON142791.1:0.000100331)"
        + ":0.00160846):0.0000330727,(((Gamma_OL522294.1:0.000200676,"
        + "Gamma_OL522071.1:0.000334491):0.000001,Gamma_OK548698.1:0.000100331)"
        + ":0.0000333531,Gamma_MW990931.1:0.000233975):0.000835758):0.000134707)"
        + ":0.000001)Root;"
    )
    draw_tree(tree_of_24, title = "Maximum likelihood tree of 24 genomes (HKY)",
              label_internal_nodes = False, tip_font_size = 9,
              height_per_tip = 0.3)
    return (tree_of_24,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 4: Distances from the root (4 points) </font>

    The distance from the root to a tip is the sum of the lengths of the branches
    on the path along the tree between them.
    Complete the `root_to_tip_distances` function below, which returns a dictionary
    of the distance from each tip to the root
    (key = tip name : value = distance to the root).

    To calculate distances from the root, we have to visit each node **after** its
    parent (the opposite of postorder!).
    Because our list of nodes is in postorder, every child comes **before** its
    parent in the list.
    So, if we loop over the list **backward**, from the root to the first node,
    we will always visit a node's parent before the node itself.

    A recipe:

    1.  **Find each node's parent.**
        Make a list called `parents` with one item for each node, all set to
        `None` (`parents = [None] * len(tree)`).
        Then loop over each `index` and `node` in `enumerate(tree)` (see tip below),
        and for each `child` in `node["children"]`, set `parents[child]` to `index`.
    2.  **Calculate the distance of every node from the root.**
        Make a list called `distances` with one `0.0` for each node.
        The root is the last node, and its distance is 0.
        Loop **backward** over every other node, with
        `for index in reversed(range(len(tree) - 1)):`, and set
        `distances[index]` to the distance of the node's parent
        (`distances[parents[index]]`) plus the length of the branch to the node
        (`tree[index]["length"]`).
    3.  **Collect the tips.**
        Loop over the nodes one more time, and for each tip (a node with no
        children), set `tip_distances[node["name"]]` to the tip's distance.

    /// tip
    1.  `reversed(range(5))` gives the numbers 4, 3, 2, 1, 0, in that order.
        `range(len(tree) - 1)` leaves out the last node (the root), because its
        distance is already 0.
    2.  `enumerate` provides a way to loop over the indices and items of a list (or
        other collection type) at the same time.
        For example, we can use `enumerate` to simplify:

        ```python
        x = ["A", "B", "C"]
        for i in range(len(x)):
            item = x[i]
            print(f"index: {i} ; item: {item}")
        ```

        to:

        ```python
        x = ["A", "B", "C"]
        for i, item in enumerate(x):
            print(f"index: {i} ; item: {item}")
        ```

        I recommend you open marimo's "Scratchpad" and play around with the example
        above to get a feel for how `enumerate` works.
    ///
    """)
    return


@app.function
def root_to_tip_distances(tree):
    """Calculate the distance from the root of a tree to each of its tips.

    Args:
        tree (list[dict]): A list of nodes in postorder, with branch lengths.

    Returns:
        dict[str, float]: Maps the name of each tip to the sum of the branch
            lengths on the path from the root to that tip.

    Examples:
        >>> root_to_tip_distances(parse_newick("((A:0.1,B:0.3):0.2,C:0.5);"))
        {'A': 0.30000000000000004, 'B': 0.5, 'C': 0.5}
    """
    tip_distances = {}
    # Add your code here!
    return tip_distances


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _distance_test_cases = [
        ("((Human:0.1,Chimp:0.1)Primates:0.3,(Mouse:0.2,Rat:0.2)Rodents:0.2)Root;",
         {"Human": 0.4, "Chimp": 0.4, "Mouse": 0.4, "Rat": 0.4}),
        ("((A:0.1,B:0.3):0.2,C:0.5);", {"A": 0.3, "B": 0.5, "C": 0.5}),
        ("(A:1,B:2,(C:3,(D:4,E:5):6):7);",
         {"A": 1.0, "B": 2.0, "C": 10.0, "D": 17.0, "E": 18.0}),
    ]
    _distance_failures = []
    for _newick, _expected in _distance_test_cases:
        try:
            _found = root_to_tip_distances(parse_newick(_newick))
            _ok = (isinstance(_found, dict)
                   and set(_found) == set(_expected)
                   and all(abs(_found[_name] - _expected[_name]) < 1e-9
                           for _name in _expected))
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
            _ok = False
        if not _ok:
            _distance_failures.append(
                f"  {_newick}\n    expected {_expected}\n    got {_found}"
            )
    root_to_tip_distances_works = len(_distance_failures) == 0
    if root_to_tip_distances_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, root_to_tip_distances failed these cases:\n"
              + "\n".join(_distance_failures))
    return (root_to_tip_distances_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## From distances and dates to numbers we can plot

    The next cell uses your `root_to_tip_distances` function to get the distance
    of each genome from the root, and converts it from expected substitutions
    **per site** to expected substitutions **per genome**, by multiplying by the
    length of the genome (29,903 sites).
    It also converts each collection date into a ***decimal year*** (*e.g.*,
    July 1, 2021 is about 2021.5), using the `date_to_year` function below, so
    that dates are numbers we can plot and fit a line to.
    It stores everything in three lists, in the same order:

    -   `years`: The date each genome was collected, as a decimal year
    -   `substitutions`: The genome's distance from the root, in substitutions per
        genome
    -   `lineages`: The common name of the genome's lineage (*e.g.*, `"Delta"`)

    **You do not need to edit the next three cells.**
    """)
    return


@app.function
def date_to_year(date):
    """Convert a date like "2021-07-24" (or "2021-07") to a decimal year.

    If the day is missing, the middle of the month is used.

    Examples:
        >>> round(date_to_year("2021-07-02"), 3)
        2021.5
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


@app.function
def year_to_date(decimal_year):
    """Convert a decimal year (like 2021.5) back into a date (like "2021-07-02")."""
    year = int(math.floor(decimal_year))
    start = datetime.date(year, 1, 1)
    days_in_year = (datetime.date(year + 1, 1, 1) - start).days
    day = int((decimal_year - year) * days_in_year)
    return (start + datetime.timedelta(days = day)).isoformat()


@app.cell
def _(
    all_genomes,
    collection_dates,
    lineage_of,
    mo,
    root_to_tip_distances_works,
    tree_of_24,
):
    mo.stop(
        not root_to_tip_distances_works,
        mo.md("***Waiting — Get your `root_to_tip_distances` function working "
              + "first.***"),
    )

    genome_length = len(all_genomes["Wuhan_NC_045512.2"])
    _distances = root_to_tip_distances(tree_of_24)
    years = []
    substitutions = []
    lineages = []
    for _name in get_tip_names(tree_of_24):
        years.append(date_to_year(collection_dates[_name]))
        substitutions.append(_distances[_name] * genome_length)
        lineages.append(lineage_of[_name])

    _rows = []
    for _name, _year, _subs in zip(get_tip_names(tree_of_24), years, substitutions):
        _rows.append(f"| {_name} | {collection_dates[_name]} | {_year:.3f} "
                     + f"| {_subs:.1f} |")
    mo.md(
        "| Genome | Collected | Decimal year | Substitutions from the root |\n"
        + "|:--|:--|--:|--:|\n"
        + "\n".join(_rows)
    )
    return lineages, substitutions, years


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 3: Fitting a molecular clock

    ## <font color=red> Challenge 5: Fitting a line (3 points) </font>

    Complete the `fit_clock` function below, which fits a straight line to the
    number of substitutions from the root versus the year each genome was
    collected, and returns:

    -   `rate`: The slope of the line, in substitutions per genome per year
    -   `ancestor_year`: The year at which the line reaches zero substitutions
    -   `r_squared`: The ***coefficient of determination***, $R^2$, which is the
        fraction of the variation in the number of substitutions explained by the
        line (1 means every point is exactly on the line; 0 means the line
        explains nothing)

    The SciPy package can do the hard work for us.
    The `linregress` function (short for ***linear regression***), which we
    imported from `scipy.stats` at the top of the notebook, finds the straight
    line that best fits the points `x` and `y` (by ***least squares***):

    ```python
    fit = linregress(x, y)
    fit.slope      # The slope of the line
    fit.intercept  # The intercept of the line (the value of y when x is 0)
    fit.rvalue     # The correlation coefficient between x and y
    ```

    `linregress` returns a single object that holds several results, and we get
    each one by its name, with a dot (*e.g.*, `fit.slope`).

    A recipe:

    1.  Use `linregress` to fit a line to `substitutions` (the $y$ values) versus
        `years` (the $x$ values)
    2.  The rate is the slope of the line
    3.  The line is $y = \text{slope} \times x + \text{intercept}$, so it reaches
        $y = 0$ at $x = -\text{intercept} / \text{slope}$; that's `ancestor_year`
    4.  $R^2$ is the correlation coefficient (`rvalue`) squared
    """)
    return


@app.function
def fit_clock(years, substitutions):
    """Fit a molecular clock (a straight line) to substitutions versus time.

    Args:
        years (list[float]): The year each genome was collected.
        substitutions (list[float]): Each genome's number of substitutions from
            the root, in the same order as `years`.

    Returns:
        tuple[float, float, float]: The rate (substitutions per year), the year
            at which the line reaches zero substitutions (the date of the
            ancestor), and the R-squared of the fit.

    Examples:
        >>> fit_clock([2020, 2021, 2022], [0, 10, 20])
        (10.0, 2020.0, 1.0)
    """
    rate = 0.0
    ancestor_year = 0.0
    r_squared = 0.0
    # Add your code here!
    return float(rate), float(ancestor_year), float(r_squared)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _clock_test_cases = [
        (([2020, 2021, 2022], [0, 10, 20]), (10.0, 2020.0, 1.0)),
        (([2020, 2021, 2022, 2023], [5, 15, 25, 35]), (10.0, 2019.5, 1.0)),
        (([2020, 2021, 2022, 2023], [3, 9, 22, 31]), (9.7, 2019.824742, 0.982663)),
    ]
    _clock_failures = []
    for (_years, _subs), _expected in _clock_test_cases:
        try:
            _found = fit_clock(_years, _subs)
            _ok = all(abs(_a - _b) < 1e-4 for _a, _b in zip(_found, _expected))
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
            _ok = False
        if not _ok:
            _clock_failures.append(
                f"  years {_years}, substitutions {_subs}:\n"
                + f"    expected (rate, ancestor_year, r_squared) = {_expected}\n"
                + f"    got {_found}"
            )
    fit_clock_works = len(_clock_failures) == 0
    if fit_clock_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, fit_clock failed these cases:\n" + "\n".join(_clock_failures))
    return (fit_clock_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A first look at plotting in Python

    The function below draws a ***scatter plot*** of substitutions versus year,
    with one color for each lineage, and adds the line you fit above.
    We have used plots made with ***matplotlib*** in every exercise, but this is
    the first time we'll look closely at how one is made.
    **You do not need to edit this function**, but please read it, along with the
    notes below.

    Every matplotlib plot follows the same basic steps:

    1.  **Make a figure and axes.**
        `figure, axes = plt.subplots(figsize = (8, 5))` makes a ***figure*** (the
        whole image, 8 inches wide and 5 tall) and one set of ***axes*** (the area
        with the $x$ and $y$ axes, where the data are drawn).
        (Remember, `plt` is short for `matplotlib.pyplot`, which we imported at
        the top of the notebook.)
    2.  **Draw the data on the axes.**
        `axes.scatter(x, y)` draws a point at each pair of `x` and `y` values, and
        `axes.plot(x, y)` draws a line through them.
        Optional ***keyword arguments*** change how they look, like `color`,
        `marker` (the shape of the points), `s` (the size of the points), and
        `label` (the name to show in the legend).
    3.  **Label everything.**
        `axes.set_xlabel(...)`, `axes.set_ylabel(...)`, and
        `axes.set_title(...)` label the axes and the plot, and `axes.legend()`
        adds a legend of everything that has a `label`.
    4.  **Show the figure.**
        In marimo, a cell displays the figure if it is the last thing in the
        cell; here, the function returns `figure`, and the cell that calls the
        function displays it.

    /// tip | Try it!
    Plotting code is easy to experiment with.
    After you finish the project and save your PDF of the notebook, try changing a
    color, the size of the points, or the size of the figure in the function below,
    and see what happens.
    ///
    """)
    return


@app.function
def plot_clock(years, substitutions, lineages, rate, ancestor_year, title = ""):
    """Plot substitutions versus year, colored by lineage, with a fitted clock.

    Args:
        years (list[float]): The year each genome was collected.
        substitutions (list[float]): Each genome's substitutions from the root.
        lineages (list[str]): The lineage of each genome.
        rate (float): The slope of the fitted line (substitutions per year).
        ancestor_year (float): The year at which the fitted line reaches zero.
        title (str): A title for the plot.

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

    # Step 2a: Draw the points, one lineage at a time, so that each lineage gets
    # its own color and its own entry in the legend
    for lineage, color in lineage_colors.items():
        # Collect the x and y values of the genomes in this lineage
        lineage_years = []
        lineage_substitutions = []
        for year, subs, genome_lineage in zip(years, substitutions, lineages):
            if genome_lineage == lineage:
                lineage_years.append(year)
                lineage_substitutions.append(subs)
        # Skip lineages with no genomes (e.g., if we removed them)
        if len(lineage_years) == 0:
            continue
        axes.scatter(
            lineage_years,          # x values
            lineage_substitutions,  # y values
            color = color,          # the color of the points
            s = 50,                 # the size of the points
            edgecolor = "white",    # a thin white outline around each point
            label = lineage,        # the name to show in the legend
            zorder = 3,             # draw the points on top of the line
        )

    # Step 2b: Draw the fitted line, from the ancestor to the latest genome.
    # A line only needs two points: where it starts, and where it ends.
    line_years = [ancestor_year, max(years)]
    line_substitutions = [0.0, rate * (max(years) - ancestor_year)]
    axes.plot(
        line_years,
        line_substitutions,
        color = "black",
        linestyle = "--",           # a dashed line
        label = f"Clock: {rate:.1f} substitutions per year",
    )

    # Step 2c: Mark the date of the ancestor, where the line reaches zero
    axes.scatter(
        [ancestor_year], [0],
        color = "gold",
        marker = "*",               # a star
        s = 300,
        edgecolor = "black",
        label = f"Ancestor: {year_to_date(ancestor_year)}",
        zorder = 4,
    )

    # Step 3: Label everything
    axes.set_xlabel("Year the genome was collected")
    axes.set_ylabel("Substitutions from the root")
    axes.set_title(title)
    axes.legend(loc = "upper left")
    axes.grid(alpha = 0.3)          # faint grid lines (alpha is transparency)

    # Step 4: Return the figure, so that the cell that calls this function can
    # display it
    figure.tight_layout()           # tidy up the spacing
    return figure


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell uses your `fit_clock` function to fit a molecular clock to all
    24 genomes, and plots the result with the `plot_clock` function.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(fit_clock_works, lineages, mo, substitutions, years):
    mo.stop(
        not fit_clock_works,
        mo.md("***Waiting — Get your `fit_clock` function working first.***"),
    )

    all_rate, all_ancestor_year, all_r_squared = fit_clock(years, substitutions)
    mo.vstack([
        mo.md(
            "| Rate (substitutions per genome per year) | Ancestor's date "
            + "| $R^2$ |\n|--:|--:|--:|\n"
            + f"| {all_rate:.1f} | {year_to_date(all_ancestor_year)} "
            + f"({all_ancestor_year:.2f}) | {all_r_squared:.2f} |"
        ),
        plot_clock(years, substitutions, lineages, all_rate, all_ancestor_year,
                   title = "All 24 genomes"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 6: Reading the clock (3 points) </font>

    Double-click this cell and answer the questions below.

    1.  **How many substitutions per genome per year does SARS-CoV-2 accumulate,
        according to the clock? About how many months does it take, on average,
        for one new substitution to appear in a lineage?**

        **Answer**:

    2.  **The rate per *site* per year is the rate per genome per year divided by
        the length of the genome (29,903 sites). What is it? How does it compare to
        the rate of substitution in the nuclear genomes of mammals, which is roughly
        $10^{-9}$ substitutions per site per year?**

        **Answer**:

    3.  **The first known cases of COVID-19 were reported in Wuhan, China in
        December 2019. Does the clock's estimate of the date of the ancestor make
        sense? Why or why not?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 4: Does every lineage follow the same clock?

    A molecular clock assumes that every lineage evolves at about the same rate.
    Omicron gives us reason to doubt that.
    It was first detected in November 2021, and it was very different from every
    other known lineage.
    Look back at the tree of 24 genomes: The branch leading to the Omicron genomes
    is about 0.0016 substitutions per site long, which is about 48 substitutions,
    far longer than any other branch in the tree.
    And Omicron's closest known relatives had been sampled more than a year
    before it was found.

    Omicron's genomes are also the latest ones in our data, so they're at the far
    right end of the plot.
    Points at either end of the $x$ axis have the most influence on the slope of a
    line fit by least squares, so if Omicron doesn't follow the clock, it could
    change our estimates of the rate and the date of the ancestor a lot.
    One way to find out is to fit the clock **without** Omicron, and then see how
    well that clock predicts the numbers of substitutions Omicron's genomes
    have accrued from the root of the tree.

    ## <font color=red> Challenge 7: Refitting the clock without Omicron (2 points) </font>

    In the cell below, beneath the "`Add your code here!`" comment, make new
    lists of `years`, `substitutions`, and `lineages` **without** the Omicron
    genomes.
    Then use `fit_clock` to fit a clock to the new lists.
    A recipe:

    1.  Loop over the three lists together with
        `for year, subs, lineage in zip(years, substitutions, lineages):`
    2.  If `lineage` is not `excluded_lineage` (which is set to `"Omicron"` for
        you), append `year`, `subs`, and `lineage` to the matching new list
        (`kept_years`, `kept_substitutions`, and `kept_lineages`)
    3.  Replace the `None`s in the line that calls `fit_clock` (the
        `kept_rate, kept_ancestor_year, kept_r_squared = ...` line) with the
        right function call

    The rest of the cell plots the new clock with `plot_clock`, and then **adds**
    the Omicron genomes to the plot as open circles, so you can see how well the
    new clock predicts them.
    Read the comments in that code to see how we can add more to a figure after
    it's made.

    /// tip
    `zip` lets us loop over several lists at the same time, one item from each
    list per iteration.
    For example, `for a, b in zip([1, 2], ["x", "y"]):` sets `a` to `1` and `b` to
    `"x"` in the first iteration, and `a` to `2` and `b` to `"y"` in the second.
    ///
    """)
    return


@app.cell
def _(fit_clock_works, lineages, mo, substitutions, years):
    mo.stop(not fit_clock_works)

    excluded_lineage = "Omicron"
    kept_years = []
    kept_substitutions = []
    kept_lineages = []
    # Add your code here!

    # Replace the `None`s below with a call to `fit_clock`
    kept_rate, kept_ancestor_year, kept_r_squared = None, None, None

    # You do NOT need to edit the rest of this cell's code below
    mo.stop(
        kept_rate is None or len(kept_years) == 0,
        mo.md("***Waiting — Make the new lists and call `fit_clock` above.***"),
    )

    # Collect the genomes we left out, so we can add them to the plot
    excluded_years = []
    excluded_substitutions = []
    for year, subs, lineage in zip(years, substitutions, lineages):
        if lineage == excluded_lineage:
            excluded_years.append(year)
            excluded_substitutions.append(subs)

    # Plot the new clock, just like before
    clock_figure = plot_clock(
        kept_years, kept_substitutions, kept_lineages, kept_rate,
        kept_ancestor_year, title = f"Clock fit without {excluded_lineage}",
    )

    # `plot_clock` returns the figure, and `figure.axes` is a list of the axes in
    # the figure; there is only one, so we get it with `[0]`. Now we can keep
    # drawing on the same axes, just like inside `plot_clock`.
    clock_axes = clock_figure.axes[0]

    # Extend the clock (as a dotted line) to the latest of the left-out genomes,
    # to show how many substitutions the clock predicts they should have
    extension_years = [max(kept_years), max(excluded_years)]
    clock_axes.plot(
        extension_years,
        [kept_rate * (year - kept_ancestor_year) for year in extension_years],
        color = "black",
        linestyle = ":",            # a dotted line
    )

    # Add the left-out genomes as open circles: `facecolor = "none"` leaves the
    # inside of each circle empty, so only its outline (`edgecolor`) is drawn
    clock_axes.scatter(
        excluded_years,
        excluded_substitutions,
        facecolor = "none",
        edgecolor = "tab:red",
        linewidth = 1.5,
        s = 50,
        label = f"{excluded_lineage} (left out of the fit)",
        zorder = 3,
    )

    # Redraw the legend, so that it includes the new points
    clock_axes.legend(loc = "upper left")

    mo.vstack([
        mo.md(
            "| Genomes | Rate (substitutions per genome per year) | Ancestor's date "
            + "| $R^2$ |\n|:--|--:|--:|--:|\n"
            + f"| Without {excluded_lineage} ({len(kept_years)}) | {kept_rate:.1f} "
            + f"| {year_to_date(kept_ancestor_year)} ({kept_ancestor_year:.2f}) "
            + f"| {kept_r_squared:.2f} |"
        ),
        clock_figure,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 8: Does Omicron follow the clock? (3 points) </font>

    Double-click this cell and answer the questions below.

    1.  **In the plot of the clock fit without Omicron, are the Omicron genomes
        above or below the line? About how many more (or fewer) substitutions do
        they have than the clock predicts? What does that tell us?**

        **Answer**:

    2.  **How did leaving out Omicron change the estimated rate and the date of
        the ancestor? Which estimate of the date of the ancestor makes more
        sense, and why?**

        **Answer**:

    3.  **Propose a biological explanation for why Omicron's genomes have so many
        more substitutions than the clock predicts. (Hint: Think about what we
        learned about Omicron at the start of Part 4.)**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Extra credit challenge (3 points) </font>

    In lecture, we learned that parsimony can be ***positively misleading***: When
    two branches that are **not** next to each other on the true tree are
    **long**, parsimony tends to group them together.
    This is called ***long-branch attraction***.
    Let's see it for ourselves!

    The `simulate_alignment` function below simulates sequences evolving on a tree
    under the JC model, and the `best_log_likelihood` function finds the branch
    lengths that maximize the log-likelihood of a tree topology, and returns that
    maximum log-likelihood.
    **You do not need to edit these two functions.**

    In the cell after them, beneath the "`Write your extra credit code here`"
    comment, write code to:

    1.  Simulate an alignment of 1,000 sites on `true_tree` (defined for you),
        by calling `simulate_alignment(true_tree, 1000, jc_rate_matrix,
        equal_frequencies, random.Random(1))`
    2.  For each of the three possible topologies (in the `topologies` dictionary,
        also defined for you), calculate:
        -   its parsimony score, with your `parsimony_score` function, using the
            rooted version of the tree
        -   its maximum log-likelihood, with `best_log_likelihood`, using the
            unrooted version of the tree
    3.  Print the parsimony score and the maximum log-likelihood of each
        topology

    In the true tree, tips `A` and `C` are on **long** branches (0.75 expected
    substitutions per site), but they are not next to each other: `A` is grouped
    with `B`, and `C` with `D`.
    The last Python cell below draws the true tree for you, so you can see the
    relationships and branch lengths.

    /// tip
    Finding the branch lengths that maximize the likelihood (*i.e.*, running
    `best_log_likelihood`) takes a few seconds for each topology, so be patient when
    you run the cell!
    ///

    After your code prints the results, answer the questions below.
    One of the three extra credit points is for your code, and one is for each of
    your answers.

    1.  **Which topology does parsimony choose? Which does likelihood choose?
        Which one is right?**

        **Answer**:

    2.  **Why does parsimony group `A` and `C` together? (Hint: Think about what
        happens on two long branches, where many substitutions happen.)**

        **Answer**:
    """)
    return


@app.function
def simulate_alignment(tree, number_of_sites, rate_matrix, base_frequencies, rng):
    """Simulate sequences evolving along a tree.

    For each site, the root's base is drawn from the base frequencies, and then,
    from the root toward the tips, each node's base is drawn from the row of its
    branch's transition probability matrix for its parent's base.

    Args:
        tree (list[dict]): A list of nodes in postorder, with branch lengths.
        number_of_sites (int): The number of sites to simulate.
        rate_matrix (numpy.ndarray): A 4-by-4 rate matrix, Q.
        base_frequencies (dict[str, float]): The frequency of each base.
        rng (random.Random): A random number generator.

    Returns:
        dict[str, str]: Maps the name of each tip to its simulated sequence.
    """
    transition_matrices = get_transition_matrices(tree, rate_matrix)
    parents = [None] * len(tree)
    for index, node in enumerate(tree):
        for child in node["children"]:
            parents[child] = index
    frequencies = [base_frequencies[base] for base in BASES]
    sequences = {node["name"]: [] for node in tree if not node["children"]}
    for _ in range(number_of_sites):
        bases = [None] * len(tree)
        bases[-1] = rng.choices(range(4), weights = frequencies)[0]
        for index in reversed(range(len(tree) - 1)):
            row = transition_matrices[index][bases[parents[index]]]
            bases[index] = rng.choices(range(4), weights = list(row))[0]
        for index, node in enumerate(tree):
            if not node["children"]:
                sequences[node["name"]].append(BASES[bases[index]])
    return {name: "".join(bases) for name, bases in sequences.items()}


@app.function
def best_log_likelihood(tree, alignment, rate_matrix, base_frequencies):
    """Find the maximum log-likelihood of a tree topology.

    Adjusts one branch length at a time to increase the log-likelihood, and
    repeats until the log-likelihood stops improving.

    Args:
        tree (list[dict]): A list of nodes in postorder, with starting branch
            lengths (a copy is made, so the tree is not changed).
        alignment (dict[str, str]): Maps the name of each tip to its sequence.
        rate_matrix (numpy.ndarray): A 4-by-4 rate matrix, Q.
        base_frequencies (dict[str, float]): The frequency of each base.

    Returns:
        float: The maximum log-likelihood of the topology.
    """
    tree = [dict(node) for node in tree]
    branches = [index for index, node in enumerate(tree) if node["length"] is not None]
    current = tree_log_likelihood(tree, alignment, rate_matrix, base_frequencies)
    for _ in range(20):
        for index in branches:
            def negative_log_likelihood(log_length):
                tree[index]["length"] = math.exp(log_length)
                return -tree_log_likelihood(tree, alignment, rate_matrix,
                                            base_frequencies)
            result = minimize_scalar(negative_log_likelihood,
                                     bounds = (math.log(1e-8), math.log(5.0)),
                                     method = "bounded", options = {"xatol": 1e-4})
            tree[index]["length"] = math.exp(result.x)
        new = tree_log_likelihood(tree, alignment, rate_matrix, base_frequencies)
        if new - current < 1e-6:
            return new
        current = new
    return current


@app.cell
def _(mo, parsimony_score_works):
    mo.stop(not parsimony_score_works)

    # The true tree: A and C are on long branches, but A is grouped with B, and C
    # with D
    true_tree = parse_newick("((A:0.75,B:0.1):0.05,(C:0.75,D:0.1):0.05);")

    # The three possible topologies: a rooted version (for parsimony) and an
    # unrooted version with starting branch lengths (for likelihood)
    topologies = {
        "(A,B),(C,D)": {
            "rooted": parse_newick("((A,B),(C,D));"),
            "unrooted": parse_newick("(A:0.1,B:0.1,(C:0.1,D:0.1):0.1);"),
        },
        "(A,C),(B,D)": {
            "rooted": parse_newick("((A,C),(B,D));"),
            "unrooted": parse_newick("(A:0.1,C:0.1,(B:0.1,D:0.1):0.1);"),
        },
        "(A,D),(B,C)": {
            "rooted": parse_newick("((A,D),(B,C));"),
            "unrooted": parse_newick("(A:0.1,D:0.1,(B:0.1,C:0.1):0.1);"),
        },
    }

    # Write your extra credit code here
    return (true_tree,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell shows what the true tree looks like (**you don't need to edit
    it**).
    """)
    return


@app.cell
def _(true_tree):
    draw_tree(true_tree, title = "The true tree")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    Starting from 24 SARS-CoV-2 genomes and the dates they were collected, you:

    -   Wrote **Fitch's algorithm** to find the **parsimony score** of a tree, and
        found that parsimony and likelihood agree about how our four lineages are
        related
    -   Calculated each genome's **distance from the root** of the tree, by visiting
        the nodes in the opposite order of postorder
    -   Fit a **molecular clock**, and estimated that SARS-CoV-2 accumulates about
        two substitutions per month
    -   Found that one lineage, Omicron, **does not follow the clock**, and that
        without it, the clock places the common ancestor of our genomes at about
        the **beginning of December 2019**, right around when the first known
        patients got sick

    Researchers used these same kinds of analyses throughout the pandemic, to
    figure out when and how fast new variants arose.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How to submit your notebook on Canvas

    Once you've completed this notebook, follow these steps to submit
    it on Canvas.

    1. Save the notebook by clicking the disk icon near the bottom-right of
       the notebook page (or use the `Ctrl + S` keyboard shortcut).
       Marimo is good about auto saving, but it doesn't hurt to be sure!
    2. Download the notebook as a PDF.
       To do this, click the icon near the top-right of the page that has three
       horizontal lines, then click "Download", and then "Download as PDF".
       In the pop-up window, leave all the settings at their defaults and
       click "Export PDF".
    3. Go to the corresponding Capstone Project assignment on Canvas and upload the
       PDF file of your notebook to complete the assignment.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Acknowledgements

    The SARS-CoV-2 genomes are from [GenBank](https://www.ncbi.nlm.nih.gov/genbank/)
    (the accession number of each genome is in the alignment file), and were
    aligned to the Wuhan-Hu-1 reference genome with
    [Nextclade](https://clades.nextstrain.org/).
    Fitch's algorithm is from Fitch (1971), *Systematic Zoology* 20:406–416.
    I used Anthropic's Claude (Opus 5.5 model) to help draft this capstone project.
    """)
    return


if __name__ == "__main__":
    app.run()
