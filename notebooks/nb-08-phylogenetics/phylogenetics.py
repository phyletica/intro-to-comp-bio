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
    import math

    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.linalg import expm

    # The four DNA bases
    BASES = "ACGT"


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Phylogenetics: The likelihood of a tree

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## From pairs of sequences to trees

    In the last two exercises, we calculated the likelihood of the divergence
    between **two** sequences.
    But most questions in biology involve **many** sequences, related by shared
    ancestry, which we can model with a tree.
    In this exercise, we will extend our likelihood calculations from pairs of
    sequences to whole trees, and use them to learn about the evolution of
    SARS-CoV-2, the virus that causes COVID-19.

    Here's our plan:

    1.  Store a tree in Python as a **list of nodes**
    2.  Count how many possible trees there are (spoiler: There are a lot!)
    3.  Calculate the **likelihood of a tree** with Felsenstein's ***pruning
        algorithm***
    4.  Use likelihood to ask **which tree** best explains four SARS-CoV-2 genomes
    5.  Reconstruct the genomes of virus **ancestors** that nobody ever sequenced
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: Trees as data

    ## Some tree terms

    -   ***Tips*** (or ***leaves***): The sequences we have data for (*e.g.*,
        genomes from different samples)
    -   ***Internal nodes***: The ancestors of the tips; we don't have their
        sequences
    -   ***Branches*** (or ***edges***): Lines connecting nodes; each branch
        represents a lineage (*e.g.*, a population or species) evolving through time
    -   ***Branch length***: How much evolution happened along a branch, in expected
        substitutions per site (just like $t$ in the last two exercises)
    -   ***Root***: The ancestor of everything in the tree
    -   ***Topology***: The branching pattern of the tree, ignoring branch lengths
    -   ***Clade***: An ancestor and all of its descendants (also called a
        ***monophyletic group***)

    ## Newick format

    Trees are usually written in ***Newick format***, where each pair of
    parentheses holds the descendants of an ancestor, and a number after a colon
    is the length of the branch above that node:

    ```
    ((Human:0.1,Chimp:0.1)Primates:0.3,(Mouse:0.2,Rat:0.2)Rodents:0.2)Root;
    ```

    This tree has four tips (`Human`, `Chimp`, `Mouse`, and `Rat`) and three internal
    nodes (`Primates`, `Rodents`, and `Root`).
    Most trees don't name their internal nodes, but we will name some of them,
    so that we can refer to them later.
    Using text characters, we can draw this tree as (we will draw it nicer in a
    later Python cell ☺️):

    ```
                     |----  Human 👩
        |-Primates---|
        |            |----  Chimp 🐵
    -Root
        |        |--------  Mouse 🐁
        |-Rodents|
                 |--------  Rat 🐀
    ```

    ## A tree as a list of nodes

    The `parse_newick` function below converts a Newick string into a ***list of
    nodes***.
    Each node is a dictionary with three keys:

    -   `"name"`: The name of the node (an empty string if it has no name)
    -   `"children"`: A list of the **indices** of the node's children in the list
        (an empty list, `[]`, if the node is a tip, because tips have no children)
    -   `"length"`: The length of the branch from the node to its parent (`None`
        for the root, which has no parent)

    The list is in ***postorder***: Every node comes **after** all of its
    children, so the root is always the **last** node in the list.
    As we will see, this order is exactly what we need to calculate the
    likelihood of a tree.
    **You do not need to edit this function,**
    but I encourage you to read the optional dropdown below to understand how it
    works!

    /// details | Optional: How does `parse_newick` work?
    `parse_newick` reads the Newick string one character at a time, from left to
    right.
    It uses three Python features we haven't seen before.

    **1. Functions inside a function.**
    `read_name_and_length` and `read_subtree` are defined *inside*
    `parse_newick`.
    They are helpers that only `parse_newick` needs, so defining them inside
    keeps them out of the way of the rest of the notebook.
    Inner functions can *read* the variables of the function they are inside
    (here, `newick`, `nodes`, and `position`).

    **2. `nonlocal`.**
    `position` is the index of the next character to read, and both helper
    functions need to move it forward as they read.
    Normally, assigning to a variable inside a function (*e.g.*,
    `position += 1`) creates a new variable that only exists inside that
    function.
    The line `nonlocal position` tells Python to use the `position` that belongs
    to `parse_newick` instead, so every helper moves the same "bookmark" through
    the string.
    (`nodes` doesn't need `nonlocal`, because `nodes.append(...)` changes the list
    without assigning a new value to the variable `nodes`.)

    **3. A function that calls itself.**
    `read_subtree` reads one node and everything below it.
    If the next character is `(`, the node has children, so `read_subtree`
    calls **itself** to read each child (separated by commas) until it reaches
    `)`.
    Then it reads the node's name and branch length, appends the node to
    `nodes`, and returns the node's index, so the parent can store it in its
    list of children.
    A function that calls itself is called ***recursive***.
    This works for trees because every subtree is itself a tree!

    Because a node is appended only **after** all of its children have been
    read, the list ends up in postorder automatically.
    For example, for `((A:0.1,B:0.2)X:0.3,C:0.4);`, the nodes are appended in
    the order `A` (index 0), `B` (1), `X` (2, children `[0, 1]`), `C` (3), and
    finally the root (4, children `[2, 3]`).
    ///
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell parses our example tree and shows its list of nodes as a table.
    The function after that draws a tree.
    **You do not need to edit the next three cells,**
    but compare the output table and tree and try to understand how the tree is
    stored in Python as a list of nodes (where each node is a `dict`).
    """)
    return


@app.cell
def _(mo):
    example_tree = parse_newick(
        "((Human:0.1,Chimp:0.1)Primates:0.3,(Mouse:0.2,Rat:0.2)Rodents:0.2)Root;"
    )

    _rows = []
    for _index, _node in enumerate(example_tree):
        _rows.append(
            f"| {_index} | `{_node['name']}` | `{_node['children']}` "
            + f"| {_node['length']} |"
        )
    mo.md(
        "| Index | `name` | `children` | `length` |\n"
        + "|:-:|:--|:--|--:|\n"
        + "\n".join(_rows)
    )
    return (example_tree,)


@app.function
def draw_tree(tree, title = "", label_internal_nodes = True):
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

    figure, axes = plt.subplots(figsize = (6, 0.45 * next_tip_y + 1))
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
                      va = "center", fontsize = 11)
    axes.set_xlim(-0.02 * max_x, 1.3 * max_x)
    axes.set_ylim(-0.7, next_tip_y - 0.3)
    axes.invert_yaxis()
    axes.set_yticks([])
    for side in ["left", "right", "top"]:
        axes.spines[side].set_visible(False)
    axes.set_xlabel("Distance from the root (expected substitutions per site)")
    axes.set_title(title)
    figure.tight_layout()
    return figure


@app.cell
def _(example_tree):
    draw_tree(example_tree, title = "Our example tree")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Look at the table and the tree above to make sure you see how they match.
    For example, `Primates` is node 2, and its `children` are nodes 0 (`Human`) and 1
    (`Chimp`), which both come before it in the list.

    ## <font color=red> Challenge 1: Finding the tips </font>

    Complete the `get_tip_names` function below, which returns a list of the names
    of the tips of a tree, in the order they appear in the list of nodes.
    A recipe:

    1.  Loop over every `node` in `tree`
    2.  If the node has no children (*i.e.*, `len(node["children"])` is 0), append
        its name (`node["name"]`) to `tip_names`
    """)
    return


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
    # Add your code here!

    return tip_names


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _tip_test_cases = [
        ("((Human:0.1,Chimp:0.1)Primates:0.3,(Mouse:0.2,Rat:0.2)Rodents:0.2)Root;",
         ["Human", "Chimp", "Mouse", "Rat"]),
        ("(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);", ["A", "B", "C", "D"]),
        ("((((E,D),C),B),A);", ["E", "D", "C", "B", "A"]),
        ("Lonely;", ["Lonely"]),
    ]
    _tip_failures = []
    for _newick, _expected in _tip_test_cases:
        try:
            _found = get_tip_names(parse_newick(_newick))
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
        if _found != _expected:
            _tip_failures.append(f"  {_newick}\n    expected {_expected}, got {_found}")

    get_tip_names_works = len(_tip_failures) == 0
    if get_tip_names_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, get_tip_names failed these cases:\n" + "\n".join(_tip_failures))
    return (get_tip_names_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 2: How many trees are there?

    If we want to find the tree that best explains our sequences, why not just
    calculate the likelihood of **every** possible tree?
    To find out, let's count how many trees there are.

    For now, let's ignore the root and count ***unrooted*** trees (we'll see why in
    Part 5).
    With 3 tips, there is only one unrooted tree: Three branches joined at one
    internal node.
    An unrooted tree with $n$ tips has $2n - 3$ branches.
    So, we can add a 4th tip to any of the 3 branches of the 3-tip tree, which
    gives us 3 trees with 4 tips.
    Each of those has 5 branches, so we can add a 5th tip in 5 places, for
    $3 \times 5 = 15$ trees with 5 tips.
    Each of those has 7 branches, and so on.
    The number of unrooted trees with $n$ tips is:

    $$
    1 \times 3 \times 5 \times 7 \times \cdots \times (2n - 5)
    $$

    /// details | Optional: A deeper dive into deriving this formula
    **Step 1: Count the branches.**
    The 3-tip tree has 3 branches.
    Adding a tip in the middle of a branch splits that branch into two, and adds a
    new branch leading to the new tip.
    So, each tip we add gives the tree **2 more branches**:

    | Tips | Branches |
    |:-:|:-:|
    | 3 | 3 |
    | 4 | 5 |
    | 5 | 7 |
    | $k$ | $2k - 3$ |

    **Step 2: Count the ways to add each tip.**
    To build a tree with $k$ tips, we add tip number $k$ to a tree with $k - 1$
    tips, which has $2(k - 1) - 3 = 2k - 5$ branches.
    Adding the new tip to each of those branches gives a different tree, so there
    are $2k - 5$ choices for where tip $k$ goes.

    **Step 3: Multiply.**
    Every tree with $n$ tips can be built in exactly one way by adding the tips one
    at a time (if you remove the last tip from a tree, there is only one smaller
    tree it could have come from).
    So, the number of trees is the number of choices for tip 3, times the number of
    choices for tip 4, and so on, up to tip $n$:

    | Adding tip $k$ | Choices ($2k - 5$) | Number of trees with $k$ tips |
    |:-:|:-:|--:|
    | 3 | 1 | $1$ |
    | 4 | 3 | $1 \times 3 = 3$ |
    | 5 | 5 | $3 \times 5 = 15$ |
    | 6 | 7 | $15 \times 7 = 105$ |

    This is exactly what the loop in Challenge 2 does: `k` is the tip being
    added, and `number *= 2 * k - 5` multiplies the number of trees so far by the
    number of places to put tip `k`.
    The first time through the loop, `k` is 3, so `number` is multiplied by
    $2 \times 3 - 5 = 1$ (there is only one tree with 3 tips).

    Mathematicians write this product of odd numbers as $(2n - 5)!!$, the
    ***double factorial***.
    For **rooted** trees, there is one more choice to make: which of the
    $2n - 3$ branches the root goes on, so there are
    $1 \times 3 \times 5 \times \cdots \times (2n - 3)$ rooted trees with $n$ tips.
    ///

    ## <font color=red> Challenge 2: Counting trees </font>

    Complete the `number_of_unrooted_trees` function below.
    A recipe:

    1.  Loop over `k` from 3 to `n` (*i.e.*, `range(3, n + 1)`), which is the
        number of tips in the tree as we add each tip
    2.  Each time through the loop, multiply `number` by `2 * k - 5`

    /// tip
    `number *= 3` is a shortcut for `number = number * 3`.
    ///
    """)
    return


@app.function
def number_of_unrooted_trees(n):
    """Count the number of unrooted, bifurcating trees with n labeled tips.

    Args:
        n (int): The number of tips (at least 3).

    Returns:
        int: 1 * 3 * 5 * ... * (2n - 5).

    Examples:
        >>> number_of_unrooted_trees(4)
        3
        >>> number_of_unrooted_trees(5)
        15
    """
    number = 1
    # Add your code here!

    return number


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _count_test_cases = [(3, 1), (4, 3), (5, 15), (6, 105), (10, 2027025)]
    _count_failures = []
    for _n, _expected in _count_test_cases:
        try:
            _found = number_of_unrooted_trees(_n)
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
        if _found != _expected:
            _count_failures.append(f"  n = {_n}: expected {_expected}, got {_found}")

    number_of_unrooted_trees_works = len(_count_failures) == 0
    if number_of_unrooted_trees_works:
        print("Yay, your function passed the test!")
    else:
        print(
            "Sorry, number_of_unrooted_trees failed these cases:\n"
            + "\n".join(_count_failures)
        )
    return (number_of_unrooted_trees_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell uses your function to make a table of the number of trees for
    different numbers of tips, and how long it would take to calculate the
    likelihood of all of them, if a computer could do **one million trees per
    second**.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(mo, number_of_unrooted_trees_works):
    mo.stop(
        not number_of_unrooted_trees_works,
        mo.md("***Waiting — Get your `number_of_unrooted_trees` function working "
              + "first.***"),
    )

    _rows = []
    for _n in [4, 5, 6, 8, 10, 15, 20, 24, 50]:
        _trees = number_of_unrooted_trees(_n)
        _seconds = _trees / 1_000_000
        if _seconds < 60:
            _time = f"{_seconds:.6g} seconds"
        elif _seconds < 60 * 60 * 24 * 365:
            _time = f"{_seconds / (60 * 60 * 24):,.1f} days"
        else:
            _time = f"{_seconds / (60 * 60 * 24 * 365):.3g} years"
        _rows.append(f"| {_n} | {_trees:.4g} | {_time} |")
    mo.md(
        "| Tips | Unrooted trees | Time to check them all |\n"
        + "|--:|--:|--:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 3: How big is the space of all possible trees? </font>

    Double-click this cell and answer the questions below.

    1.  **Our SARS-CoV-2 alignment has 24 genomes. Could we find the best tree for
        all 24 by calculating the likelihood of every possible tree?
        For comparison, the universe is about $1.4 \times 10^{10}$ years old.**

        **Answer**:

    2.  **Programs that estimate trees, like IQ-TREE and RAxML, can't check every
        tree. What do you think they do instead?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 3: The likelihood of a tree

    ## A problem: We don't know the ancestors

    For two sequences, we calculated the probability of each site by
    looking up one transition probability, $P_{xy}(t)$.
    On a tree, we know the bases at the tips, but not at the internal nodes.
    To calculate the probability of a site, we have to **add up** the
    probabilities of every possible combination of bases at the internal nodes.
    An unrooted tree of our 24 genomes has 22 internal nodes, so with 4 possible
    bases at each, that's $4^{22} \approx 1.8 \times 10^{13}$ combinations, for
    **every site**!

    ## The solution: Felsenstein's pruning algorithm

    Felsenstein (1981) showed that we can avoid all of that work by moving
    from the tips toward the root (*i.e.*, in postorder), and calculating, for
    each node, a list of four numbers called its ***conditional likelihoods***:

    $L_{\text{node}}(i)$ = the probability of the data at the tips that descend from
    this node, **if** the node has base $i$ (in other words, *conditional on* the
    node having base $i$)

    /// note
    You may also see these called ***partial likelihoods*** (or just
    "partials"), especially in the documentation of phylogenetics software.
    ///

    The pruning algorithm uses **three rules**:

    1.  **At a tip**, the conditional likelihood is 1 for the base we observed and
        0 for the other three bases.
        If the base is missing (a gap, `-`, or an ambiguous base, like `N`), the
        conditional likelihood is 1 for all four bases: We would have seen the same
        missing data no matter which base is really there, so the probability of
        what we observed is 1 for each base.

    2.  **At an internal node**, for each base $i$, multiply together, over each
        child, the probability of getting the child's data if the node has base $i$:

        $$
        L_{\text{parent}}(i) = \prod_{\text{children}} \Big[ \sum_{j}
        P_{ij}(t_{\text{child}}) \, L_{\text{child}}(j) \Big]
        $$

        where $t_{\text{child}}$ is the length of the branch between the child and
        the parent. The sum inside the brackets covers every base $j$ the child
        could have.

    3.  **At the root**, the likelihood of the site is the sum over the four bases,
        weighted by the base frequencies:

        $$
        L_{\text{site}} = \sum_{i} \pi_i \, L_{\text{root}}(i)
        $$

        Note: The likelihood of the site is just a weighted average of the
        conditional likelihoods of the four bases at the root, where the weights are
        base frequencies.

    Because our list of nodes is in postorder, a simple loop over the list visits
    every node after its children, so the children's conditional likelihoods are
    always ready when we need them.

    ## Visualizing the pruning algorithm at work

    The animation below shows the pruning algorithm calculating the likelihood of
    one site on our example tree, under the JC model.
    Click "Play" to watch it, or step through it with "Previous" and "Next."
    At each step, the algorithm visits the next node in the list (the orange
    node), and calculates its conditional likelihoods from those of its children
    (the blue nodes).
    The table on the right is the list of conditional likelihoods of every node,
    which gets filled in, one row at a time, in postorder.

    Use the menus to change the base of each tip, and watch how the conditional
    likelihoods change.
    For example, what happens if you make the Chimp's base missing (`-`)?
    **You do not need to edit the next four cells.**
    """)
    return


@app.function(hide_code=True)
def draw_pruning_step(tree, site_bases, rate_matrix, base_frequencies, step):
    """Draw the pruning algorithm after `step` nodes have been visited.

    Step 0 is before any node is visited; steps 1 to len(tree) visit the nodes
    in postorder; the last step (len(tree) + 1) combines the root's conditional
    likelihoods into the likelihood of the site. This function does its own
    calculations, so it works before you have completed the challenges.

    Returns:
        matplotlib.figure.Figure: The figure.
    """
    number_of_nodes = len(tree)
    last_step = number_of_nodes + 1
    step = max(0, min(step, last_step))

    # Run the pruning algorithm, keeping everything we need to show
    matrices = [None if node["length"] is None
                else expm(rate_matrix * node["length"]) for node in tree]
    node_likelihoods = []
    child_sums = []  # For each node, the bracketed sum for each of its children
    for node in tree:
        if not node["children"]:
            base = site_bases[node["name"]]
            vector = np.zeros(4)
            if base in BASES:
                vector[BASES.index(base)] = 1.0
            else:
                vector[:] = 1.0
            node_likelihoods.append(vector)
            child_sums.append([])
        else:
            sums = [matrices[child] @ node_likelihoods[child]
                    for child in node["children"]]
            node_likelihoods.append(np.prod(sums, axis = 0))
            child_sums.append(sums)
    frequencies = np.array([base_frequencies[base] for base in BASES])
    site_likelihood = float(frequencies @ node_likelihoods[-1])

    # Where to draw each node
    parent = [None] * number_of_nodes
    for index, node in enumerate(tree):
        for child in node["children"]:
            parent[child] = index
    x = [0.0] * number_of_nodes
    for index in reversed(range(number_of_nodes - 1)):
        x[index] = x[parent[index]] + tree[index]["length"]
    y = [0.0] * number_of_nodes
    next_tip = 0
    for index, node in enumerate(tree):
        if not node["children"]:
            y[index] = next_tip
            next_tip += 1
        else:
            y[index] = float(np.mean([y[child] for child in node["children"]]))
    max_x = max(x)

    current = step - 1 if 1 <= step <= number_of_nodes else None
    done = set(range(min(step, number_of_nodes)))
    highlight = "darkorange"

    figure = plt.figure(figsize = (11, 6.2))
    grid = figure.add_gridspec(2, 2, height_ratios = [3, 1.4],
                               width_ratios = [1.1, 1], hspace = 0.25,
                               wspace = 0.05)
    tree_axes = figure.add_subplot(grid[0, 0])
    table_axes = figure.add_subplot(grid[0, 1])
    text_axes = figure.add_subplot(grid[1, :])

    # The tree
    for index, node in enumerate(tree):
        color, width = "black", 2
        if current is not None and parent[index] == current:
            color, width = "steelblue", 4
        if parent[index] is not None:
            tree_axes.plot([x[parent[index]], x[index]], [y[index], y[index]],
                           color = color, linewidth = width, zorder = 1)
        if node["children"]:
            child_ys = [y[child] for child in node["children"]]
            tree_axes.plot([x[index], x[index]], [min(child_ys), max(child_ys)],
                           color = "black", linewidth = 2, zorder = 1)
        if node["length"] is not None:
            tree_axes.text((x[parent[index]] + x[index]) / 2, y[index] + 0.12,
                           f"{node['length']:g}", ha = "center", va = "top",
                           fontsize = 9, color = "gray")
    for index, node in enumerate(tree):
        if index == current:
            face, size = highlight, 260
        elif current is not None and parent[index] == current:
            face, size = "steelblue", 160
        elif index in done:
            face, size = "dimgray", 90
        else:
            face, size = "white", 90
        tree_axes.scatter([x[index]], [y[index]], s = size, color = face,
                          edgecolor = "black", zorder = 3)
        label = node["name"] or f"node {index}"
        if not node["children"]:
            tree_axes.text(x[index] + 0.04 * max_x, y[index],
                           f"{label}:  {site_bases[node['name']]}",
                           va = "center", fontsize = 13)
        else:
            tree_axes.text(x[index] - 0.03 * max_x, y[index] - 0.18, label,
                           ha = "right", va = "bottom", fontsize = 11,
                           color = "firebrick")
    tree_axes.set_xlim(-0.25 * max_x, 1.45 * max_x)
    tree_axes.set_ylim(-0.8, next_tip - 0.2)
    tree_axes.invert_yaxis()
    tree_axes.axis("off")
    tree_axes.set_title("The tree (visited in postorder)", fontsize = 13)

    # The list of conditional likelihoods, one row per node
    table_axes.set_xlim(0, 6)
    table_axes.set_ylim(number_of_nodes + 0.6, -1)
    table_axes.axis("off")
    table_axes.set_title("node_likelihoods", fontsize = 13, family = "monospace")
    for column, base in enumerate(BASES):
        table_axes.text(2.5 + column, -0.4, base, ha = "center", va = "center",
                        fontsize = 13, fontweight = "bold")
    for index, node in enumerate(tree):
        row = index + 0.5
        row_label = f"[{index}] {node['name'] or 'node ' + str(index)}"
        table_axes.text(0.05, row, row_label, va = "center", fontsize = 11,
                        color = highlight if index == current else "black",
                        fontweight = "bold" if index == current else "normal")
        for column in range(4):
            box = plt.Rectangle((2.05 + column, row - 0.42), 0.9, 0.84,
                                facecolor = "white", edgecolor = "lightgray")
            if index in done:
                vector = node_likelihoods[index]
                share = vector[column] / vector.max()
                box.set_facecolor(plt.cm.Blues(0.08 + 0.7 * share))
                if vector[column] in (0.0, 1.0):
                    text = f"{vector[column]:.0f}"
                else:
                    text = f"{vector[column]:.4f}"
                table_axes.text(2.5 + column, row, text, ha = "center",
                                va = "center", fontsize = 10,
                                color = "white" if share > 0.6 else "black")
            if index == current:
                box.set_edgecolor(highlight)
                box.set_linewidth(2.5)
            table_axes.add_patch(box)

    # What happens at this step
    text_axes.axis("off")
    if step == 0:
        lines = [
            "Start: No conditional likelihoods have been calculated yet.",
            "We will visit the nodes in postorder (the order of the list), so "
            + "every child is visited before its parent.",
        ]
    elif current is not None:
        node = tree[current]
        name = node["name"] or f"node {current}"
        if not node["children"]:
            base = site_bases[node["name"]]
            vector = ", ".join(f"{value:.0f}" for value in node_likelihoods[current])
            if base in BASES:
                lines = [f"Rule 1 (a tip): {name} has {base}, so its conditional "
                         + f"likelihoods are ({vector}).",
                         "The probability of the data at a tip is 1 for the base "
                         + "we observed, and 0 for the other bases."]
            else:
                lines = [f"Rule 1 (a tip): {name}'s base is missing ({base}), so "
                         + f"its conditional likelihoods are ({vector}).",
                         "We would see the same missing data no matter which base "
                         + "is really there."]
        else:
            children = node["children"]
            names = [tree[child]["name"] or f"node {child}" for child in children]
            brackets = " × ".join(
                rf"[$\sum_j P_{{ij}}({tree[child]['length']:g})\,"
                + rf"L_{{\mathrm{{{child_name}}}}}(j)$]"
                for child, child_name in zip(children, names)
            )
            lines = [f"Rule 2 (an internal node): For each base $i$ of {name}, "
                     + f"multiply over its children ({', '.join(names)}):",
                     rf"$L_{{\mathrm{{{name.replace(' ', '~')}}}}}(i)$ = " + brackets]
            for column, base in enumerate(BASES):
                factors = " × ".join(f"{sums[column]:.4f}"
                                     for sums in child_sums[current])
                lines.append(f"    {base}:  {factors} = "
                             + f"{node_likelihoods[current][column]:.4f}")
    else:
        root = node_likelihoods[-1]
        terms = " + ".join(f"{frequencies[column]:g} × {root[column]:.4f}"
                           for column in range(4))
        lines = [r"Rule 3 (the root): Average the conditional likelihoods of "
                 + "each base $i$: $L_{\mathrm{site}} = \sum_i \pi_i\,"
                 + r"L_{\mathrm{root}}(i)$",
                 f"= {terms}",
                 f"= {site_likelihood:.4f},   so the log-likelihood of the site "
                 + f"is ln({site_likelihood:.4f}) = {math.log(site_likelihood):.4f}"]
    text_axes.text(0.0, 1.0, "\n".join(lines), va = "top", ha = "left",
                   fontsize = 12, linespacing = 1.5, transform = text_axes.transAxes)
    figure.suptitle(f"Step {step} of {last_step}", fontsize = 14, x = 0.12,
                    ha = "left")
    return figure


@app.function(hide_code=True)
def pruning_animation_html(
    tree, site_bases, rate_matrix, base_frequencies, seconds_per_step = 2.5
):
    """Make an HTML player that steps through `draw_pruning_step`.

    Returns:
        str: HTML (with a little JavaScript) to display with `mo.iframe`.
    """
    import base64
    import io
    import json

    frames = []
    for step in range(len(tree) + 2):
        figure = draw_pruning_step(tree, site_bases, rate_matrix,
                                   base_frequencies, step)
        buffer = io.BytesIO()
        figure.savefig(buffer, format = "png", dpi = 90)
        plt.close(figure)
        frames.append("data:image/png;base64,"
                      + base64.b64encode(buffer.getvalue()).decode())
    milliseconds = int(1000 * seconds_per_step)
    return f"""
    <div style="font-family: sans-serif; text-align: center;">
      <img id="frame" src="{frames[0]}" style="max-width: 100%;">
      <div style="margin-top: 6px;">
        <button id="previous">&#9664; Previous</button>
        <button id="play">&#9654; Play</button>
        <button id="next">Next &#9654;</button>
      </div>
    </div>
    <script>
      const frames = {json.dumps(frames)};
      let index = 0;
      let timer = null;
      const image = document.getElementById("frame");
      const play = document.getElementById("play");
      function show(i) {{
        index = (i + frames.length) % frames.length;
        image.src = frames[index];
      }}
      function stop() {{
        clearInterval(timer);
        timer = null;
        play.innerHTML = "&#9654; Play";
      }}
      document.getElementById("previous").onclick = () => {{ stop(); show(index - 1); }};
      document.getElementById("next").onclick = () => {{ stop(); show(index + 1); }};
      play.onclick = () => {{
        if (timer) {{ stop(); return; }}
        if (index === frames.length - 1) {{ show(0); }}
        play.innerHTML = "&#10074;&#10074; Pause";
        timer = setInterval(() => {{
          if (index === frames.length - 1) {{ stop(); return; }}
          show(index + 1);
        }}, {milliseconds});
      }};
    </script>
    """


@app.cell
def _(example_tree, mo):
    _tip_names = [_node["name"] for _node in example_tree if not _node["children"]]
    _defaults = {"Human": "A", "Chimp": "A", "Mouse": "G", "Rat": "G"}
    pruning_tip_menus = mo.ui.dictionary({
        _name: mo.ui.dropdown(
            options = ["A", "C", "G", "T", "-"],
            value = _defaults.get(_name, "A"),
            label = _name,
        )
        for _name in _tip_names
    })
    return (pruning_tip_menus,)


@app.cell
def _(equal_frequencies, example_tree, jc_rate_matrix, mo, pruning_tip_menus):
    mo.vstack([
        mo.hstack(list(pruning_tip_menus.values()), justify = "start"),
        mo.iframe(
            pruning_animation_html(
                example_tree, pruning_tip_menus.value, jc_rate_matrix,
                equal_frequencies,
            ),
            height = "650px",
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We'll build the pruning algorithm one rule at a time, starting with tips.
    In this exercise, we'll store each list of conditional likelihoods as a NumPy
    array of four numbers, in the order of `BASES` (`"ACGT"`).

    ## <font color=red> Challenge 4: Conditional likelihoods at a tip </font>

    Complete the `tip_likelihoods` function below (Rule 1 from above).
    A recipe:

    1.  If `base` is one of the four `BASES`, set the entry of `likelihoods` at index
        `BASES.index(base)` to 1.0 (the others stay 0)
    2.  Otherwise, set all four entries of `likelihoods` to 1.0
    """)
    return


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
    # Add your code here!

    return likelihoods


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _tip_likelihoods_test_cases = [
        ("A", [1.0, 0.0, 0.0, 0.0]),
        ("C", [0.0, 1.0, 0.0, 0.0]),
        ("G", [0.0, 0.0, 1.0, 0.0]),
        ("T", [0.0, 0.0, 0.0, 1.0]),
        ("-", [1.0, 1.0, 1.0, 1.0]),
        ("N", [1.0, 1.0, 1.0, 1.0]),
    ]
    _tip_likelihoods_failures = []
    for _base, _expected in _tip_likelihoods_test_cases:
        try:
            _found = tip_likelihoods(_base)
            _ok = np.allclose(_found, _expected)
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
            _ok = False
        if not _ok:
            _tip_likelihoods_failures.append(
                f"  {_base!r}: expected {_expected}, got {_found}"
            )

    tip_likelihoods_works = len(_tip_likelihoods_failures) == 0
    if tip_likelihoods_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, tip_likelihoods failed these cases:\n"
              + "\n".join(_tip_likelihoods_failures))
    return (tip_likelihoods_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Transition probabilities for every branch

    To combine children (Rule 2), we need the transition probability matrix,
    $P(t)$, for the branch above each child.
    In this exercise, we'll use the Jukes-Cantor (JC) model.
    The next cell has the JC rate matrix, $Q$, and the
    `get_transition_probabilities` function from the last exercise (which
    calculates $P(t) = e^{Qt}$).
    The `get_transition_matrices` function uses `get_transition_probabilities` to
    calculate $P(t)$ for the branch above every node in a tree, and returns them in
    a list in the same order as the nodes (with `None` for the root, which has no
    branch above it).
    **You do not need to edit the next three cells.**
    """)
    return


@app.cell
def _():
    # The JC rate matrix from the last exercise (rows and columns are A, C, G, T)
    jc_rate_matrix = np.array([
        [-1.0, 1 / 3, 1 / 3, 1 / 3],
        [1 / 3, -1.0, 1 / 3, 1 / 3],
        [1 / 3, 1 / 3, -1.0, 1 / 3],
        [1 / 3, 1 / 3, 1 / 3, -1.0],
    ])
    # Under the JC model, all four bases have the same frequency
    equal_frequencies = {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}
    return equal_frequencies, jc_rate_matrix


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 5: Combining children </font>

    Complete the `combine_children` function below (Rule 2).
    It takes a list of the conditional likelihoods of each child, and a list of the
    transition probability matrices of the branches above each child (in the same
    order).
    A recipe:

    1.  Loop over the children; for each child, get its conditional likelihoods
        (call them `likelihoods`) and the transition probability matrix of the
        branch above it (call it `P`); see the tip below for an easy way to do this
    2.  For each base index `parent_base_i` of the parent (`range(4)`), calculate
        `total`, the sum over each base index `child_base_i` of the child
        (`range(4)`) of `P[parent_base_i, child_base_i] * likelihoods[child_base_i]`
    3.  Multiply `parent_likelihoods[parent_base_i]` by `total`

    /// tip
    Python's `zip` function lets you loop over two lists at the same time:

    ```python
    for likelihoods, P in zip(child_likelihoods, child_transition_matrices):
    ```
    ///

    /// details | Optional: A NumPy shortcut
    The sum in Step 2, for all four values of `parent_base_i` at once, is a
    ***matrix-vector product***, which NumPy writes as `P @ likelihoods`.
    So, the whole function could be written with one loop:

    ```python
    for likelihoods, P in zip(child_likelihoods, child_transition_matrices):
        parent_likelihoods *= P @ likelihoods
    ```

    But it's worth writing the loops yourself first, so you can see what the
    shortcut does!
    ///
    """)
    return


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
    # Add your code here!

    return parent_likelihoods


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(jc_rate_matrix, tip_likelihoods_works):
    combine_children_works = False
    if not tip_likelihoods_works:
        print("Get tip_likelihoods working first!")
    else:
        _P1 = get_transition_probabilities(jc_rate_matrix, 0.1)
        _P2 = get_transition_probabilities(jc_rate_matrix, 0.2)
        _P3 = get_transition_probabilities(jc_rate_matrix, 0.3)
        _combine_test_cases = [
            ("two tips (A and G)",
             [tip_likelihoods("A"), tip_likelihoods("G")], [_P1, _P2],
             [0.053039, 0.001826, 0.025728, 0.001826]),
            ("three tips (A, A, and C)",
             [tip_likelihoods("A"), tip_likelihoods("A"), tip_likelihoods("C")],
             [_P1, _P1, _P3],
             [0.06771, 0.000733, 0.00008, 0.00008]),
            ("an internal node and a gap",
             [np.array([0.5, 0.1, 0.2, 0.0]), tip_likelihoods("-")], [_P2, _P3],
             [0.429779, 0.123407, 0.2, 0.046814]),
        ]
        _combine_failures = []
        for _label, _child_likelihoods, _matrices, _expected in _combine_test_cases:
            try:
                _found = combine_children(_child_likelihoods, _matrices)
                _ok = np.allclose(_found, _expected, atol = 1e-6)
            except Exception as _error:
                _found = f"an error ({type(_error).__name__}: {_error})"
                _ok = False
            if not _ok:
                _combine_failures.append(
                    f"  {_label}:\n    expected {_expected}\n    got {_found}"
                )
        combine_children_works = len(_combine_failures) == 0
        if combine_children_works:
            print("Yay, your function passed the test!")
        else:
            print("Sorry, combine_children failed these cases:\n"
                  + "\n".join(_combine_failures))
    return (combine_children_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 6: From the tips to the root </font>

    Now, let's put Rules 1 and 2 together.
    Complete the `get_root_likelihoods` function below, which calculates the
    conditional likelihoods of every node in a tree, for one site, and returns
    those of the root.
    The bases at the tips for this site are in the dictionary `site_bases` (*e.g.*,
    `site_bases["Human"]` is the base of `Human` at this site).
    A recipe:

    1.  Loop over every `node` in `tree` (in order, which is postorder).
        Remember, `tree` is a list of nodes, and each node is a dictionary.
    2.  If the node is a tip (it has no children), use
        `tip_likelihoods(site_bases[node["name"]])` to get the conditional
        likelihoods of the tip as a NumPy array, and append the array to
        `node_likelihoods`
    3.  Otherwise (`else`),
        1.  Make two empty lists to store two things from all of the node's
            children: Conditional likelihoods and transition probability matrices.
            You could call these `child_likelihoods = []` and `child_matrices = []`.
        2.  Loop over each `child` in `node["children"]` and append
            `node_likelihoods[child]` to `child_likelihoods` and append
            `transition_matrices[child]` to `child_matrices`.
        3.  Use the `child_likelihoods` and `child_matrices` lists you created in
            the 2 previous steps to get the conditional likelihoods for the current
            (parent) node by using `combine_children(...)`, and append those
            conditional likelihoods to `node_likelihoods`.
    4.  After the loop over the nodes of `tree`, the conditional likelihoods of the
        root are the last item of `node_likelihoods`

    /// tip
    Because we append to `node_likelihoods` in the same order as the nodes,
    `node_likelihoods[k]` holds the conditional likelihoods of node `k`, and,
    because the nodes are in postorder, the children's conditional likelihoods are
    always calculated before the parent's.
    ///
    """)
    return


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
    # Add your code here!

    if len(node_likelihoods) == 0:
        return np.zeros(4)
    return node_likelihoods[-1]


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function on our example tree.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(combine_children_works, example_tree, jc_rate_matrix):
    get_root_likelihoods_works = False
    if not combine_children_works:
        print("Get tip_likelihoods and combine_children working first!")
    else:
        _matrices = get_transition_matrices(example_tree, jc_rate_matrix)
        _root_test_cases = [
            ({"Human": "A", "Chimp": "A", "Mouse": "G", "Rat": "G"},
             [0.026601, 0.00295, 0.038486, 0.00295]),
            ({"Human": "A", "Chimp": "C", "Mouse": "G", "Rat": "T"},
             [0.000206, 0.000206, 0.000235, 0.000235]),
            ({"Human": "A", "Chimp": "-", "Mouse": "N", "Rat": "A"},
             [0.476079, 0.010679, 0.010679, 0.010679]),
        ]
        _root_failures = []
        for _site_bases, _expected in _root_test_cases:
            try:
                _found = get_root_likelihoods(example_tree, _site_bases, _matrices)
                _ok = np.allclose(_found, _expected, atol = 1e-6)
            except Exception as _error:
                _found = f"an error ({type(_error).__name__}: {_error})"
                _ok = False
            if not _ok:
                _root_failures.append(
                    f"  {_site_bases}:\n    expected {_expected}\n    got {_found}"
                )
        get_root_likelihoods_works = len(_root_failures) == 0
        if get_root_likelihoods_works:
            print("Yay, your function passed the test!")
        else:
            print("Sorry, get_root_likelihoods failed these cases:\n"
                  + "\n".join(_root_failures))
    return (get_root_likelihoods_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 7: The log-likelihood of a site </font>

    Complete the `site_log_likelihood` function below (Rule 3).
    A recipe:

    1.  Replace `None` in `root_likelihoods = None` with the conditional likelihoods
        of the root, using your `get_root_likelihoods` function
    2.  Under the "`2. Add your code here!`" comment, loop over each base index `i`
        in `range(4)`, and add `base_frequencies[BASES[i]] * root_likelihoods[i]` to
        `likelihood`

    The function then returns the log of the likelihood.
    """)
    return


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
    # 1. Replace `None` with the conditional likelihoods of the root
    root_likelihoods = None

    likelihood = 0.0
    # 2. Add your code here!

    if likelihood <= 0.0:
        return -math.inf
    return math.log(likelihood)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function on our example tree.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(
    equal_frequencies,
    example_tree,
    get_root_likelihoods_works,
    jc_rate_matrix,
):
    site_log_likelihood_works = False
    if not get_root_likelihoods_works:
        print("Get get_root_likelihoods working first!")
    else:
        _matrices = get_transition_matrices(example_tree, jc_rate_matrix)
        _site_test_cases = [
            ({"Human": "A", "Chimp": "A", "Mouse": "G", "Rat": "G"}, -4.031561),
            ({"Human": "A", "Chimp": "C", "Mouse": "G", "Rat": "T"}, -8.418127),
            ({"Human": "A", "Chimp": "-", "Mouse": "N", "Rat": "A"}, -2.063341),
            ({"Human": "-", "Chimp": "-", "Mouse": "-", "Rat": "-"}, 0.0),
        ]
        _site_failures = []
        for _site_bases, _expected in _site_test_cases:
            try:
                _found = site_log_likelihood(
                    example_tree, _site_bases, _matrices, equal_frequencies
                )
                _ok = abs(_found - _expected) < 1e-5
            except Exception as _error:
                _found = f"an error ({type(_error).__name__}: {_error})"
                _ok = False
            if not _ok:
                _site_failures.append(
                    f"  {_site_bases}: expected {_expected}, got {_found}"
                )
        site_log_likelihood_works = len(_site_failures) == 0
        if site_log_likelihood_works:
            print("Yay, your function passed the test!")
        else:
            print("Sorry, site_log_likelihood failed these cases:\n"
                  + "\n".join(_site_failures))
    return (site_log_likelihood_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// note | Why is the log-likelihood 0 when every base is missing?
    The fourth test case above expects the log-likelihood of a site to be zero when
    all the tips have no data (a gap) at that site.
    If we have no data at a site, the probability of "no data" is 1, and
    $\ln(1) = 0$.
    So, a site where every sequence has a gap doesn't change the log-likelihood of
    the tree at all.
    This is why we can include gaps and ambiguous bases without having to remove
    them: Missing data don't help or hurt any tree.
    ///

    # Part 4: Which tree best explains the data?

    ## SARS-CoV-2 genomes

    Now, let's use your pruning algorithm on real data.
    The alignment we'll use has 24 SARS-CoV-2 genomes from GenBank, including
    the original "Wuhan-Hu-1" reference genome, sampled early in the
    pandemic, and genomes from several lineages that spread around the world
    later.
    The genomes were aligned to the reference with a program called
    [Nextclade](https://clades.nextstrain.org/), which keeps the reference's
    numbering, so position 23,403 in the alignment is position 23,403 of the
    reference genome.

    The lineages have names (called "Pango lineages"), like `B.1.1.7`, that work like
    addresses: `B.1.1` is a descendant of `B.1`, which is a descendant of `B`.
    In this exercise, we'll call each lineage by a shorter name (Alpha, Gamma,
    Delta, and Omicron are the World Health Organization's names for these
    "variants of concern"):

    | Our name | Pango lineage |
    |:--|:--|
    | Wuhan | `B` (the reference genome) |
    | B.1 | `B.1` |
    | Delta | `B.1.617.2` |
    | Alpha | `B.1.1.7` |
    | Gamma | `P.1` (short for `B.1.1.28.1`) |
    | Omicron | `BA.1.1` (short for `B.1.1.529.1.1`) |

    The next two cells download the aligned genomes and pick one genome from each of
    the six viral lineages in the table above.
    **You do not need to edit the next two cells.**
    """)
    return


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
def _(mo):
    _url = (
        "https://raw.githubusercontent.com/phyletica/intro-to-comp-bio/"
        + "refs/heads/main/notebooks/data/SARS-CoV-2.nextclade.aligned.fasta"
    )
    _all_genomes = parse_fasta_url(_url)

    # Each description line is "common name|lineage|GenBank accession|date"
    _chosen_accessions = {
        "Wuhan": "NC_045512.2",
        "B.1": "PV612058.1",
        "Delta": "OL524349.1",
        "Alpha": "OY916467.1",
        "Gamma": "OL522294.1",
        "Omicron": "OP349650.1",
    }
    genomes = {}
    _rows = []
    for _description, _sequence in _all_genomes.items():
        _name, _lineage, _accession, _date = _description.split("|")
        if _chosen_accessions.get(_name) == _accession:
            genomes[_name] = _sequence
            _rows.append(f"| {_name} | `{_lineage}` | {_accession} | {_date} "
                         + f"| {len(_sequence):,} |")

    mo.md(
        f"Downloaded {len(_all_genomes)} genomes, and picked these "
        + f"{len(genomes)}:\n\n"
        + "| Name | Lineage | GenBank accession | Collected | Length |\n"
        + "|:--|:--|:--|:--|--:|\n"
        + "\n".join(_rows)
    )
    return (genomes,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below defines a `get_site` function for getting a dictionary of the
    base of every sequence at one position of an alignment.
    Note: `position` is 1-based (not zero-based) to match the reference genome's
    numbering system.
    **You don't need to edit the next cell**.
    """)
    return


@app.function
def get_site(alignment, position):
    """Get the base of every sequence at one position of an alignment.

    Args:
        alignment (dict[str, str]): Maps each sequence name to its aligned
            sequence.
        position (int): The position, counting from 1 (like the reference
            genome's numbering), not from 0 like Python.

    Returns:
        dict[str, str]: Maps each sequence name to its base at the position.
    """
    site_bases = {}
    for name, sequence in alignment.items():
        site_bases[name] = sequence[position - 1]
    return site_bases


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Avoiding duplicated work across sites

    To get the log-likelihood of a whole alignment, we add up the log-likelihoods
    of all its sites.
    But, there's a shortcut!
    SARS-CoV-2 genomes are very similar, so most columns of the alignment are
    identical (*e.g.*, every genome has an `A`), and identical columns have the same
    log-likelihood.
    So, the `tree_log_likelihood` function below counts how many times each unique
    column (or ***site pattern***) occurs, calculates the log-likelihood of each
    pattern only once (using your `site_log_likelihood` function), and multiplies
    it by the number of times the pattern occurs.
    **You do not need to edit the next two functions.**
    """)
    return


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Three possible trees

    Let's start with just four of the genomes: Wuhan, Delta, Alpha, and Omicron.
    With four tips, there are only three unrooted trees.
    Each tree splits the four genomes into two pairs:

    1.  Wuhan + Delta, and Alpha + Omicron
    2.  Wuhan + Alpha, and Delta + Omicron
    3.  Wuhan + Omicron, and Delta + Alpha

    The next cell defines these three trees, with the branch lengths that
    maximize each tree's likelihood under the JC model (I calculated those for
    you).
    Because these are unrooted trees, we write them with three branches coming
    out of the "root", and draw them with an arbitrary root at the left.
    The cell after that uses your functions to calculate the log-likelihood of
    each tree.
    **You do not need to edit the next two cells.**
    """)
    return


@app.cell
def _(genomes):
    four_genomes = {}
    for _name in ["Wuhan", "Delta", "Alpha", "Omicron"]:
        four_genomes[_name] = genomes[_name]

    four_tip_trees = {
        "1: (Wuhan, Delta), (Alpha, Omicron)": parse_newick(
            "(Wuhan:0.000178972,Delta:0.000929634,"
            + "(Alpha:0.000705813,Omicron:0.00170239):0.000134645);"
        ),
        "2: (Wuhan, Alpha), (Delta, Omicron)": parse_newick(
            "(Wuhan:0.000216696,Alpha:0.00079132,"
            + "(Delta:0.000915385,Omicron:0.0017608):0.0000348304);"
        ),
        "3: (Wuhan, Omicron), (Delta, Alpha)": parse_newick(
            "(Wuhan:0.000220262,Omicron:0.00179091,"
            + "(Delta:0.000946957,Alpha:0.000793881):0.00000001);"
        ),
    }
    return four_genomes, four_tip_trees


@app.cell
def _(
    equal_frequencies,
    four_genomes,
    four_tip_trees,
    get_tip_names_works,
    jc_rate_matrix,
    mo,
    site_log_likelihood_works,
):
    mo.stop(
        not (site_log_likelihood_works and get_tip_names_works),
        mo.md("***Waiting — Get your functions from Challenges 1 and 4–7 working "
              + "first.***"),
    )

    _number_of_patterns = len(count_site_patterns(four_genomes, ["Wuhan", "Delta",
                                                                 "Alpha", "Omicron"]))
    _log_likes = {}
    for _label, _tree in four_tip_trees.items():
        _log_likes[_label] = tree_log_likelihood(
            _tree, four_genomes, jc_rate_matrix, equal_frequencies
        )
    _best = max(_log_likes.values())
    _rows = []
    for _label, _log_like in _log_likes.items():
        _rows.append(f"| {_label} | {_log_like:.2f} | {_best - _log_like:.2f} |")

    _figures = []
    for _label, _tree in four_tip_trees.items():
        _figures.append(draw_tree(_tree, title = "Tree " + _label))

    mo.vstack([
        mo.md(
            f"The {len(four_genomes['Wuhan']):,} sites of the alignment have only "
            + f"**{_number_of_patterns}** different patterns among these four "
            + "genomes.\n\n"
            + "| Tree | Log-likelihood | Worse than the best tree by |\n"
            + "|:--|--:|--:|\n"
            + "\n".join(_rows)
        ),
        mo.hstack(_figures, widths = "equal"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The tree with the highest likelihood splits the 4 viral genomes into the pairs
    Wuhan + Delta and Alpha + Omicron.

    ## How much does each site matter?

    Every site contributes to the log-likelihood of every tree, but some sites help
    us choose among tree topologies more than others.
    Think about these kinds of sites:

    -   **All four genomes have the same base**: No substitutions are needed, on any
        tree
    -   **One genome differs**: One substitution, on that genome's own branch,
        explains the site well on any tree
    -   **Two pairs** (*e.g.*, two `A`s and two `T`s): One substitution can explain
        the site, but **only** on the tree that groups the pairs together; the other
        two trees need at least two substitutions

    So, the "two pairs" sites should favor one tree over the others the most.
    But that's not the whole story!
    Each tree has its **own** branch lengths, and **every** site helps estimate
    them: Sites where all the genomes match tell us the branches are short, and
    sites where one genome differs tell us how long that genome's branch is.
    So, every kind of site can fit one tree a little better than another.

    The next cell uses your functions to add up, for each kind of site, how much
    better (positive numbers) or worse (negative numbers) Tree 1 fits than the
    other two trees.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(
    equal_frequencies,
    four_genomes,
    four_tip_trees,
    get_tip_names_works,
    jc_rate_matrix,
    mo,
    site_log_likelihood_works,
):
    mo.stop(
        not (site_log_likelihood_works and get_tip_names_works),
        mo.md("***Waiting — Get your functions from Challenges 1 and 4–7 working "
              + "first.***"),
    )

    def _kind_of_site(pattern):
        if "N" in pattern:
            return "Missing data (a gap or ambiguous base)"
        _counts = sorted(collections.Counter(pattern).values())
        if _counts == [4]:
            return "All four the same"
        if _counts == [1, 3]:
            return "One genome differs"
        if _counts == [2, 2]:
            return "Two pairs"
        return "Three or more different bases"

    _names = ["Wuhan", "Delta", "Alpha", "Omicron"]
    _patterns = count_site_patterns(four_genomes, _names)
    _labels = list(four_tip_trees.keys())
    # The log-likelihood of each pattern on each tree
    _site_log_likes = {}
    for _label in _labels:
        _tree = four_tip_trees[_label]
        _tips = get_tip_names(_tree)
        _matrices = get_transition_matrices(_tree, jc_rate_matrix)
        _site_log_likes[_label] = {}
        for _pattern in _patterns:
            _site_bases = dict(zip(_names, _pattern))
            _site_log_likes[_label][_pattern] = site_log_likelihood(
                _tree, {_tip: _site_bases[_tip] for _tip in _tips}, _matrices,
                equal_frequencies,
            )

    _kinds = ["Two pairs", "All four the same", "One genome differs",
              "Three or more different bases",
              "Missing data (a gap or ambiguous base)"]
    _number_of_sites = {_kind: 0 for _kind in _kinds}
    _versus_2 = {_kind: 0.0 for _kind in _kinds}
    _versus_3 = {_kind: 0.0 for _kind in _kinds}
    for _pattern, _count in _patterns.items():
        _kind = _kind_of_site(_pattern)
        _number_of_sites[_kind] += _count
        _tree_1 = _count * _site_log_likes[_labels[0]][_pattern]
        _versus_2[_kind] += _tree_1 - _count * _site_log_likes[_labels[1]][_pattern]
        _versus_3[_kind] += _tree_1 - _count * _site_log_likes[_labels[2]][_pattern]

    _rows = []
    for _kind in _kinds:
        _rows.append(f"| {_kind} | {_number_of_sites[_kind]:,} "
                     + f"| {_versus_2[_kind]:+.2f} | {_versus_3[_kind]:+.2f} |")
    _rows.append(f"| **Total** | {sum(_number_of_sites.values()):,} "
                 + f"| **{sum(_versus_2.values()):+.2f}** "
                 + f"| **{sum(_versus_3.values()):+.2f}** |")
    mo.md(
        "| Kind of site | Number of sites | Tree 1 vs. Tree 2 | Tree 1 vs. Tree 3 |\n"
        + "|:--|--:|--:|--:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice that all the sites contribute to the trees' likelihoods.
    This is because of what the sites say about the branch lengths of the trees.
    However, the "two pairs" sites are responsible for the largest differences in
    likelihoods between the tree topologies.

    The next cell shows all of the "two pairs" sites, and the tree that groups each
    site's pairs together.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(four_genomes, mo):
    _names = ["Wuhan", "Delta", "Alpha", "Omicron"]
    _split_to_tree = {
        frozenset(["Wuhan", "Delta"]): "1",
        frozenset(["Alpha", "Omicron"]): "1",
        frozenset(["Wuhan", "Alpha"]): "2",
        frozenset(["Delta", "Omicron"]): "2",
        frozenset(["Wuhan", "Omicron"]): "3",
        frozenset(["Delta", "Alpha"]): "3",
    }
    _rows = []
    for _position in range(1, len(four_genomes["Wuhan"]) + 1):
        _site_bases = get_site(four_genomes, _position)
        _column = [_site_bases[_name] for _name in _names]
        if any(_base not in BASES for _base in _column):
            continue
        _counts = collections.Counter(_column)
        if len(_counts) == 2 and all(_count == 2 for _count in _counts.values()):
            _pair = frozenset(_name for _name in _names
                              if _site_bases[_name] == _column[0])
            _rows.append(
                f"| {_position:,} | " + " | ".join(_column)
                + f" | {_split_to_tree[_pair]} |"
            )
    mo.md(
        "| Position | " + " | ".join(_names) + " | Supported tree topology |\n"
        + "|--:|:-:|:-:|:-:|:-:|:-:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What does a branch length mean?

    The branch lengths represent the amount of evolution that occurred.
    So, it makes sense that changing the length of a branch will change the
    probability of producing the observed data (the likelihood!).

    The slider below changes the length of Omicron's branch in Tree 1, and the plot
    shows how the log-likelihood of the tree changes.
    The dashed line marks the length we gave you.
    **You do not need to edit the next three cells**, but please play with the
    slider.
    """)
    return


@app.cell
def _(mo):
    omicron_branch_slider = mo.ui.slider(
        start = 0.0001,
        stop = 0.004,
        step = 0.0001,
        value = 0.0005,
        label = "Length of Omicron's branch",
        show_value = True,
        full_width = True,
    )
    return (omicron_branch_slider,)


@app.cell
def _(
    equal_frequencies,
    four_genomes,
    four_tip_trees,
    get_tip_names_works,
    jc_rate_matrix,
    mo,
    site_log_likelihood_works,
):
    mo.stop(
        not (site_log_likelihood_works and get_tip_names_works),
        mo.md("***Waiting — Get your functions from Challenges 1 and 4–7 working "
              + "first.***"),
    )

    # Calculate the log-likelihood over a grid of lengths for Omicron's branch
    _tree = [dict(_node) for _node in four_tip_trees["1: (Wuhan, Delta), (Alpha, Omicron)"]]
    omicron_index = [_node["name"] for _node in _tree].index("Omicron")
    omicron_best_length = _tree[omicron_index]["length"]
    omicron_lengths = [0.0001 * (_i + 1) for _i in range(40)]
    omicron_log_likes = []
    for _length in omicron_lengths:
        _tree[omicron_index]["length"] = _length
        omicron_log_likes.append(
            tree_log_likelihood(_tree, four_genomes, jc_rate_matrix, equal_frequencies)
        )
    return (
        omicron_best_length,
        omicron_index,
        omicron_lengths,
        omicron_log_likes,
    )


@app.cell
def _(
    equal_frequencies,
    four_genomes,
    four_tip_trees,
    jc_rate_matrix,
    mo,
    omicron_best_length,
    omicron_branch_slider,
    omicron_index,
    omicron_lengths,
    omicron_log_likes,
):
    _tree = [dict(_node) for _node in four_tip_trees["1: (Wuhan, Delta), (Alpha, Omicron)"]]
    _tree[omicron_index]["length"] = omicron_branch_slider.value
    _log_like = tree_log_likelihood(
        _tree, four_genomes, jc_rate_matrix, equal_frequencies
    )

    _figure, _axes = plt.subplots(figsize = (7, 4))
    _axes.plot(omicron_lengths, omicron_log_likes, color = "steelblue", linewidth = 2)
    _axes.axvline(omicron_best_length, color = "gray", linestyle = "--")
    _axes.scatter([omicron_branch_slider.value], [_log_like], color = "darkorange",
                  s = 60, zorder = 3)
    _axes.set_ylim(max(omicron_log_likes) - 60, max(omicron_log_likes) + 5)
    _axes.set_xlabel("Length of Omicron's branch (expected substitutions per site)")
    _axes.set_ylabel("Log-likelihood of Tree 1")
    _axes.set_title(
        f"Branch length = {omicron_branch_slider.value:.4f} "
        + f"(about {omicron_branch_slider.value * len(four_genomes['Omicron']):.0f} "
        + f"substitutions); log-likelihood = {_log_like:.2f}"
    )
    _figure.tight_layout()

    _instructions = (
        "**Use the slider to adjust the length of Omicron's branch and watch how "
        + "the log-likelihood of the tree changes**"
    )

    mo.vstack([
        mo.md(_instructions),
        omicron_branch_slider,
        _figure,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 8: Which tree? </font>

    Double-click this cell and answer the questions below.

    1.  **Which tree has the highest log-likelihood, and by how much is it better
        than the other two? Does it make sense, given the lineage names of the
        genomes (see the table in Part 4)?**

        **Answer**:

    2.  **Which kind of site contributes the most to Tree 1's advantage?**

        **Answer**:

    3.  **Does any kind of site favor Tree 2 or Tree 3 over Tree 1?**

        **Answer**:

    4.  **Why might sites where all four genomes have the same base fit one tree
        better than another?**

        **Answer**:

    5.  **Use the slider to make Omicron's branch much shorter, and then much
        longer, than the length we gave you.
        What happens to the log-likelihood? Why do you think the given length is
        the best?
        Approximately how many substitutions does that length imply occurred on
        Omicron's branch?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 5: Reconstructing ancestors

    ## What base did the ancestor have?

    The conditional likelihoods at the root tell us more than the likelihood.
    $\pi_i L_{\text{root}}(i)$ is the probability of the data **and** base $i$ at
    the root, so dividing by the likelihood of the site (the probability of the data
    at that site) gives the probability that the root had base $i$, given the data:

    $$
    \text{Probability that the root had base } i = \frac{\pi_i \,
    L_{\text{root}}(i)}{\sum_{k} \pi_k \, L_{\text{root}}(k)}
    $$

    ## <font color=red> Challenge 9: Probabilities of the root's base </font>

    Complete the `root_state_probabilities` function below.
    A recipe:

    1.  Get the conditional likelihoods of the root as a NumPy array called
        `root_likelihoods` with the `get_root_likelihoods` function.
    2.  For each base index `i` in `range(4)`, set `probabilities[i]` to
        `base_frequencies[BASES[i]] * root_likelihoods[i]`
    3.  Divide `probabilities` by its sum, so that the four probabilities add up
        to 1

    /// tip
    Dividing a NumPy array by a number divides every entry of the array by that
    number, so after Step 2 you can use
    `probabilities = probabilities / probabilities.sum()`.
    ///
    """)
    return


@app.function
def root_state_probabilities(tree, site_bases, transition_matrices, base_frequencies):
    """Calculate the probability of each base at the root of a tree, for one site.

    Args:
        tree (list[dict]): A list of nodes in postorder.
        site_bases (dict[str, str]): Maps the name of each tip to its base at
            this site.
        transition_matrices (list): The transition probability matrix for the
            branch above each node, as returned by `get_transition_matrices`.
        base_frequencies (dict[str, float]): The frequency of each base.

    Returns:
        numpy.ndarray: The probabilities of A, C, G, and T at the root, which
            add up to 1.
    """
    probabilities = np.zeros(4)
    # Add your code here!

    return probabilities


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function on our example tree.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(
    equal_frequencies,
    example_tree,
    get_root_likelihoods_works,
    jc_rate_matrix,
):
    root_state_probabilities_works = False
    if not get_root_likelihoods_works:
        print("Get get_root_likelihoods working first!")
    else:
        _matrices = get_transition_matrices(example_tree, jc_rate_matrix)
        _root_state_test_cases = [
            ({"Human": "A", "Chimp": "A", "Mouse": "G", "Rat": "G"},
             [0.374732, 0.041556, 0.542156, 0.041556]),
            ({"Human": "A", "Chimp": "-", "Mouse": "N", "Rat": "A"},
             [0.93695, 0.021017, 0.021017, 0.021017]),
            ({"Human": "-", "Chimp": "-", "Mouse": "-", "Rat": "-"},
             [0.25, 0.25, 0.25, 0.25]),
        ]
        _root_state_failures = []
        for _site_bases, _expected in _root_state_test_cases:
            try:
                _found = root_state_probabilities(
                    example_tree, _site_bases, _matrices, equal_frequencies
                )
                _ok = np.allclose(_found, _expected, atol = 1e-5)
            except Exception as _error:
                _found = f"an error ({type(_error).__name__}: {_error})"
                _ok = False
            if not _ok:
                _root_state_failures.append(
                    f"  {_site_bases}:\n    expected {_expected}\n    got {_found}"
                )
        root_state_probabilities_works = len(_root_state_failures) == 0
        if root_state_probabilities_works:
            print("Yay, your function passed the test!")
        else:
            print("Sorry, root_state_probabilities failed these cases:\n"
                  + "\n".join(_root_state_failures))
    return (root_state_probabilities_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What about the other ancestors?

    The `root_state_probabilities` function only tells us about the root.
    What if we want to know about a different ancestor?

    There's a trick!
    With models like JC (and K80, HKY, and the others we've seen),
    the likelihood of a tree **doesn't depend on where the root is**.
    Felsenstein (1981) called this the ***pulley principle***: We can slide the root
    anywhere on the tree, like a rope over a pulley, without changing the
    likelihood.
    So, to learn about any ancestor, we can ***reroot*** the tree at that ancestor,
    and then use `root_state_probabilities`!

    The `reroot` function below does the rerooting for you.
    It takes a tree and the name of an internal node, and returns a new list of nodes
    (in postorder), with that node as the root.
    **You do not need to edit the next function.**
    """)
    return


@app.function
def reroot(tree, node_name):
    """Make a new copy of a tree, rerooted at an internal node.

    Args:
        tree (list[dict]): A list of nodes in postorder.
        node_name (str): The name of the internal node to use as the new root.

    Returns:
        list[dict]: A new list of nodes in postorder, with the node called
            `node_name` as the root (the last node). The branches and their
            lengths are the same as in `tree`.
    """
    names = [node["name"] for node in tree]
    if names.count(node_name) != 1:
        raise ValueError(f"The tree must have exactly one node named {node_name!r}")
    new_root = names.index(node_name)
    if len(tree[new_root]["children"]) == 0:
        raise ValueError(f"{node_name!r} is a tip; we can only reroot at an "
                         + "internal node")
    # Make a list of the neighbors of each node, and the branch lengths to them
    neighbors = collections.defaultdict(list)
    for index, node in enumerate(tree):
        for child in node["children"]:
            length = tree[child]["length"]
            neighbors[index].append((child, length))
            neighbors[child].append((index, length))
    # Walk away from the new root, adding each node after all of its children
    new_tree = []

    def add_subtree(index, came_from, length):
        children = []
        for neighbor, neighbor_length in neighbors[index]:
            if neighbor != came_from:
                children.append(add_subtree(neighbor, index, neighbor_length))
        new_tree.append(
            {"name": tree[index]["name"], "children": children, "length": length}
        )
        return len(new_tree) - 1

    add_subtree(new_root, None, None)
    return new_tree


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 10: Reconstructing an ancestor </font>

    Complete the `reconstruct_ancestor` function below, which calculates the
    probability of each base at one position of the alignment, for the ancestor
    called `node_name`.
    A recipe:

    1.  Get a new tree (list of nodes) that is rooted at `node_name`, using the
        `reroot` function
    2.  Get the transition probability matrices of the new rerooted tree, using
        the `get_transition_matrices` function
    3.  Get the bases of every genome at `position`, using the `get_site` function
    4.  Set `probabilities` to the result of `root_state_probabilities`, using the
        rerooted tree, the results of Steps 2 and 3, and `base_frequencies`
    """)
    return


@app.function
def reconstruct_ancestor(
    tree, node_name, alignment, position, rate_matrix, base_frequencies
):
    """Calculate the probability of each base for an ancestor at one position.

    Args:
        tree (list[dict]): A list of nodes in postorder.
        node_name (str): The name of the internal node (ancestor).
        alignment (dict[str, str]): Maps the name of each tip to its aligned
            sequence.
        position (int): The position in the alignment, counting from 1.
        rate_matrix (numpy.ndarray): A 4-by-4 rate matrix, Q.
        base_frequencies (dict[str, float]): The frequency of each base.

    Returns:
        numpy.ndarray: The probabilities of A, C, G, and T for the ancestor.
    """
    probabilities = np.zeros(4)
    # Add your code here!

    return probabilities


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function on our example tree.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(
    equal_frequencies,
    example_tree,
    jc_rate_matrix,
    root_state_probabilities_works,
):
    reconstruct_ancestor_works = False
    if not root_state_probabilities_works:
        print("Get root_state_probabilities working first!")
    else:
        _example_alignment = {"Human": "AT", "Chimp": "AT", "Mouse": "GT", "Rat": "GC"}
        _ancestor_test_cases = [
            ("Primates", 1, [0.99171, 0.001176, 0.005939, 0.001176]),
            ("Rodents", 1, [0.025185, 0.004862, 0.965091, 0.004862]),
            ("Root", 1, [0.374732, 0.041556, 0.542156, 0.041556]),
            ("Rodents", 2, [0.011228, 0.158184, 0.011228, 0.819361]),
        ]
        _ancestor_failures = []
        for _node_name, _position, _expected in _ancestor_test_cases:
            try:
                _found = reconstruct_ancestor(
                    example_tree, _node_name, _example_alignment, _position,
                    jc_rate_matrix, equal_frequencies,
                )
                _ok = np.allclose(_found, _expected, atol = 1e-5)
            except Exception as _error:
                _found = f"an error ({type(_error).__name__}: {_error})"
                _ok = False
            if not _ok:
                _ancestor_failures.append(
                    f"  {_node_name}, position {_position}:\n"
                    + f"    expected {_expected}\n    got {_found}"
                )
        reconstruct_ancestor_works = len(_ancestor_failures) == 0
        if reconstruct_ancestor_works:
            print("Yay, your function passed the test!")
        else:
            print("Sorry, reconstruct_ancestor failed these cases:\n"
                  + "\n".join(_ancestor_failures))
    return (reconstruct_ancestor_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The ancestors of SARS-CoV-2 lineages

    Now let's reconstruct two ancestors of our six virus genomes.
    The next cell defines the maximum likelihood tree of the six genomes under the
    JC model (I estimated the tree for you, using a program called IQ-TREE), and
    names two of its internal nodes:

    -   `B.1 ancestor`: The common ancestor of B.1 and its descendants (Delta, Alpha,
        Gamma, and Omicron)
    -   `B.1.1 ancestor`: The common ancestor of the B.1.1 lineages (Alpha, Gamma,
        and Omicron)

    The cell after that checks the pulley principle, by calculating the
    log-likelihood of the tree as given, and after rerooting it at `B.1.1 ancestor`.
    **You do not need to edit the next two cells.**
    """)
    return


@app.cell
def _():
    six_tip_tree = parse_newick(
        "(Wuhan:0.000133475,B.1:0.000133667,"
        + "(Delta:0.000936309,((Alpha:0.000704525,Omicron:0.00170696):0.0000336162,"
        + "Gamma:0.00106654)B.1.1 ancestor:0.000135986):0.00000001)B.1 ancestor;"
    )
    draw_tree(six_tip_tree, title = "Maximum likelihood tree")
    return (six_tip_tree,)


@app.cell
def _(
    equal_frequencies,
    genomes,
    get_tip_names_works,
    jc_rate_matrix,
    mo,
    site_log_likelihood_works,
    six_tip_tree,
):
    mo.stop(
        not (site_log_likelihood_works and get_tip_names_works),
        mo.md("***Waiting — Get your functions from Challenges 1 and 4–7 working "
              + "first.***"),
    )

    _log_like = tree_log_likelihood(
        six_tip_tree, genomes, jc_rate_matrix, equal_frequencies
    )
    _rerooted_log_like = tree_log_likelihood(
        reroot(six_tip_tree, "B.1.1 ancestor"), genomes, jc_rate_matrix,
        equal_frequencies,
    )
    mo.md(
        "| Rooted at | Log-likelihood |\n|:--|--:|\n"
        + f"| `B.1 ancestor` (as drawn above) | {_log_like:.4f} |\n"
        + f"| `B.1.1 ancestor` | {_rerooted_log_like:.4f} |"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell uses your `reconstruct_ancestor` function to reconstruct both
    ancestors at a few positions that are famous among SARS-CoV-2 researchers.
    For each ancestor, it shows the most probable base and its probability.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(
    equal_frequencies,
    genomes,
    jc_rate_matrix,
    mo,
    reconstruct_ancestor_works,
    six_tip_tree,
):
    mo.stop(
        not reconstruct_ancestor_works,
        mo.md("***Waiting — Get your `reconstruct_ancestor` function working "
              + "first.***"),
    )

    _tip_names = ["Wuhan", "B.1", "Delta", "Alpha", "Gamma", "Omicron"]
    _ancestors = ["B.1 ancestor", "B.1.1 ancestor"]
    _rows = []
    for _position in [3037, 14408, 23403, 28881, 28882, 28883]:
        _site_bases = get_site(genomes, _position)
        _row = f"| {_position:,} | " + " | ".join(
            _site_bases[_name] for _name in _tip_names
        )
        for _ancestor in _ancestors:
            _probabilities = reconstruct_ancestor(
                six_tip_tree, _ancestor, genomes, _position, jc_rate_matrix,
                equal_frequencies,
            )
            _best = int(np.argmax(_probabilities))
            _row += f" | **{BASES[_best]}** ({_probabilities[_best]:.4f})"
        _rows.append(_row + " |")
    mo.md(
        "| Position | " + " | ".join(_tip_names) + " | "
        + " | ".join(f"`{_ancestor}`" for _ancestor in _ancestors) + " |\n"
        + "|--:|" + ":-:|" * len(_tip_names) + ":-:|:-:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 11: Ancestral genomes </font>

    Here are some facts about the positions in the table above:

    -   The changes at positions 3,037 and 14,408 are some of the first changes
        that defined the B.1 lineage, which spread around the world early in 2020
    -   The change at 23,403 changes the spike protein (the part of the virus that
        attaches to our cells), and is called "D614G," because it changes the
        614th amino acid of the spike protein from aspartic acid (D) to glycine
        (G); viruses with this change spread faster
    -   The changes at 28,881–28,883 alter two amino acids of the
        nucleocapsid (N) protein, and define the B.1.1 lineage

    Double-click this cell and answer the questions below.

    1.  **Does the log-likelihood of the six-genome tree change when we reroot it
        at the B.1.1 ancestor? Why does this matter for reconstructing ancestors?**

        **Answer**:

    2.  **What three bases did the B.1.1 ancestor most likely have at positions
        28,881–28,883? How about the B.1 ancestor? How confident are these
        reconstructions?**

        **Answer**:

    3.  **Did the B.1 ancestor already have the D614G change (a `G` at 23,403)?
        Why are the reconstructions so confident, even though nobody sequenced
        these ancestors?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Stretch goal </font>

    Can you reconstruct the **whole** genome of the B.1.1 ancestor, and find every
    position where it differs from the Wuhan reference genome?

    In the cell below, beneath the "`Write your stretch goal code below ...`"
    comment, write a loop over every position of the alignment (from 1 to
    `len(genomes["Wuhan"])`).
    For each position:

    1.  Skip the position if all six genomes have the same base (this saves a lot
        of time, because the ancestor will have that base too); the `set` of the
        bases at the position, `set(get_site(genomes, position).values())`, has
        only one item when all six bases are the same
    2.  Otherwise, use `reconstruct_ancestor` to get the probabilities of the bases
        for `"B.1.1 ancestor"`
    3.  If the most probable base (use `BASES[int(np.argmax(probabilities))]`) is
        different from the Wuhan genome's base at that position, print the
        position, the Wuhan base, the ancestor's most probable base, and its
        probability

    Then answer the question below.

    **Alpha, Gamma, and Omicron all have the change at position 23,063 (called
    "N501Y," another change to the spike protein). Your reconstruction probably
    says the B.1.1 ancestor had it too. But the earliest B.1.1 genomes, sampled in
    early 2020, did not have N501Y; it arose separately in Alpha, Gamma, and
    Omicron (and in other lineages) in late 2020 and 2021. Why did our
    reconstruction get this wrong, and so confidently?**

    **Answer**:
    """)
    return


@app.cell
def _(mo, reconstruct_ancestor_works):
    mo.stop(not reconstruct_ancestor_works)

    # Write your stretch goal code below that loops over every position, skips
    # positions where all six genomes have the same base, and prints the positions
    # where the most probable base of the B.1.1 ancestor differs from Wuhan
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    -   A tree can be stored as a **list of nodes in postorder**, where every node
        comes after its children
    -   The number of possible trees grows **astronomically** with the number of
        tips, so programs **search** for good trees rather than trying them all
    -   **Felsenstein's pruning algorithm** calculates the likelihood of a tree
        by working from the tips to the root, one node at a time
    -   A few sites (where bases are shared in **pairs**, when there are four
        sequences) strongly favor one tree, but **every** site informs the branch
        lengths, and so the likelihood of every tree
    -   The conditional likelihoods at the root give the **probabilities of the
        ancestor's bases**, and, thanks to the **pulley principle**, we can reroot
        the tree to reconstruct **any** ancestor
    -   A reconstruction is only as good as the model and data: Convergent
        evolution (like N501Y) can fool it
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
    3. Go to the corresponding Lab Exercise assignment on Canvas and upload the
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
    The pruning algorithm and the pulley principle are from Felsenstein (1981),
    *Journal of Molecular Evolution* 17:368–376.
    I used Anthropic's Claude (Opus 5.5 model) to help draft this notebook.
    """)
    return


if __name__ == "__main__":
    app.run()
