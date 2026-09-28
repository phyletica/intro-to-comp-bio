# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.0",
#     "matplotlib",
#     "biopython",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Capstone Project 1: Tracing the SARS-CoV-2 variants

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

    In the sequence alignment exercise, we worked with the genomes of five
    SARS-CoV-2 samples: The original reference genome sampled in Wuhan, China in
    December 2019, and four "variants of concern" that drove major waves of the
    COVID-19 pandemic.

    In this project, you will answer two questions about those genomes:

    1.  **How are these variants related to one another?**
    2.  **Does every part of the genome tell the same story?**

    To answer them, you will use nearly everything you have learned so far this
    semester:

    1.  Use a **string search** to extract the same two genes from each SARS-CoV-2
        genome
    2.  **Align** every pair of sequences with the Needleman-Wunsch code you wrote
    3.  Count the **differences** between each aligned pair of sequences to build a
        **distance matrix**
    4.  Use the distance matrix to estimate a **phylogeny** (an evolutionary tree)
        and compare it to what we know about the history of the pandemic

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

    The functions below are the ones we built in the sequence alignment exercise,
    plus our `parse_fasta_file` function from our first notebook.
    **You do not need to edit any of them**, but you will use them later on in the
    notebook.
    As a reminder:

    -   `score_pair(base_1, base_2)` scores one column of an alignment
    -   `align_sequences(seq_1, seq_2)` returns the two aligned sequences and the
        alignment score, in that order
    -   `print_alignment(aligned_1, aligned_2, score)` prints an alignment
    -   `parse_fasta_file(file_name)` returns a dictionary of sequences keyed by
        their name
    """)
    return


@app.function
def score_pair(base_1, base_2, match = 1, mismatch = -1, gap = -2):
    """Score a single column of an alignment."""
    if (base_1 == "-") or (base_2 == "-"):
        return gap
    if base_1 == base_2:
        return match
    return mismatch


@app.function
def get_initial_matrix(seq_1, seq_2, gap = -2):
    """Create a scoring matrix with its first row and column filled in."""
    number_of_rows = len(seq_1) + 1
    number_of_columns = len(seq_2) + 1
    matrix = []
    for i in range(number_of_rows):
        matrix.append([0] * number_of_columns)
    for i in range(1, number_of_rows):
        matrix[i][0] = i * gap
    for j in range(1, number_of_columns):
        matrix[0][j] = j * gap
    return matrix


@app.function
def fill_scoring_matrix(seq_1, seq_2, match = 1, mismatch = -1, gap = -2):
    """Fill a Needleman-Wunsch scoring matrix for two sequences."""
    matrix = get_initial_matrix(seq_1, seq_2, gap)
    number_of_rows = len(seq_1) + 1
    number_of_columns = len(seq_2) + 1
    for i in range(1, number_of_rows):
        for j in range(1, number_of_columns):
            pair_score = score_pair(
                seq_1[i - 1], seq_2[j - 1], match, mismatch, gap
            )
            diagonal = matrix[i - 1][j - 1] + pair_score
            up = matrix[i - 1][j] + gap
            left = matrix[i][j - 1] + gap
            matrix[i][j] = max(diagonal, up, left)
    return matrix


@app.function
def traceback_alignment(
    matrix,
    seq_1,
    seq_2,
    match = 1,
    mismatch = -1,
    gap = -2,
):
    """Recover the optimal global alignment from a filled scoring matrix."""
    aligned_1 = ""
    aligned_2 = ""
    i = len(seq_1)
    j = len(seq_2)
    while (i > 0) or (j > 0):
        pair_score = 0
        if (i > 0) and (j > 0):
            pair_score = score_pair(
                seq_1[i - 1], seq_2[j - 1], match, mismatch, gap
            )
        if (i > 0) and (j > 0) and (matrix[i][j] == matrix[i - 1][j - 1] + pair_score):
            aligned_1 = seq_1[i - 1] + aligned_1
            aligned_2 = seq_2[j - 1] + aligned_2
            i = i - 1
            j = j - 1
        elif (i > 0) and (matrix[i][j] == matrix[i - 1][j] + gap):
            aligned_1 = seq_1[i - 1] + aligned_1
            aligned_2 = "-" + aligned_2
            i = i - 1
        else:
            aligned_1 = "-" + aligned_1
            aligned_2 = seq_2[j - 1] + aligned_2
            j = j - 1
    return aligned_1, aligned_2


@app.function
def align_sequences(seq_1, seq_2, match = 1, mismatch = -1, gap = -2):
    """Compute the optimal global alignment of two sequences.

    Returns:
        tuple[str, str, int]: The two aligned sequences and the score of the
            alignment.
    """
    matrix = fill_scoring_matrix(seq_1, seq_2, match, mismatch, gap)
    aligned_1, aligned_2 = traceback_alignment(
        matrix, seq_1, seq_2, match, mismatch, gap
    )
    return aligned_1, aligned_2, matrix[-1][-1]


@app.function
def print_alignment(aligned_1, aligned_2, score = None):
    """Print a pairwise alignment with a match line between the sequences."""
    match_line = ""
    for index in range(len(aligned_1)):
        if aligned_1[index] == aligned_2[index]:
            match_line += "|"
        else:
            match_line += " "
    print(aligned_1)
    print(match_line)
    print(aligned_2)
    if score is not None:
        print("Score:", score)


@app.function
def parse_fasta_file(file_name):
    """Read a FASTA file into a dictionary of sequences keyed by name."""
    sequences = {}
    current_id = None
    with open(file_name, "r") as in_stream:
        for line in in_stream:
            line = line.strip()
            if not line:
                continue
            if line[0] == ">":
                current_id = line[1:].strip()
                sequences[current_id] = ""
            else:
                if current_id is not None:
                    sequences[current_id] += line
    return sequences


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: Extracting genes from the genomes

    Let's start by loading the five genomes.
    The cell below also:

    -   Shortens each sequence's name to just the variant name and stores these
        shortened names in a list called `variant_names`.
    -   Stores the genomes in the `variant_genomes` list, in the same order as the
        names in `variant_names`.
    -   Counts the number of `N` characters in each genome.

    **You do not need to edit the code below**, but look it over and try to
    understand how it works.
    """)
    return


@app.cell
def _(local_files):
    local_files  # Ignore this line; it just ensures the FASTA file is present
    covid_genomes = parse_fasta_file("SARS-CoV-2-unaligned.fasta")

    variant_names = []
    variant_genomes = []
    for _full_name in covid_genomes:
        # Keep just the part of the name before the first "-"
        _short_name = _full_name.split("-")[0]
        variant_names.append(_short_name)
        variant_genomes.append(covid_genomes[_full_name])
        _genome = covid_genomes[_full_name]
        print(f"{_short_name:8} {len(_genome):6} bases, {_genome.count('N'):4} Ns")
    return variant_genomes, variant_names


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two things jump out from the output above.

    First, the genomes are **different lengths**.
    Some of that is real insertions and deletions, but a lot of it is because each
    genome was sequenced a little differently, so each one starts and stops at a
    slightly different point in the viral genome.

    Second, some of the genomes contain a lot of `N` characters.
    An `N` means "some nucleotide was here, but the sequencing could not tell which
    one."
    In other words, **an `N` is ambiguous data**, not a real nucleotide.
    Keep that in mind, because it will matter in Part 2.

    ## Locating two genes

    Rather than working with whole genomes, we will extract two genes from each
    genome and analyze them separately:

    -   **The spike gene (the S1 part).**
        The spike protein studs the outside of the virus particle and is what the
        virus uses to latch onto and enter our cells.
        The S1 part of spike contains the region that binds to our cells, and it is
        also the main target of the antibodies our immune systems make, including
        the antibodies produced in response to COVID-19 vaccines.
    -   **The N gene.**
        The N (nucleocapsid) protein packages the virus's RNA genome *inside* the
        virus particle.

    To find these genes in each genome, we will do exactly what we did at the end of
    the sequence alignment exercise:
    Use string searches to locate short **anchor sequences** at the beginning and
    end of each gene, and keep everything from the start of the first anchor to the
    end of the second.

    The anchors below are 20-base sequences that appear **exactly once** in each of
    the five genomes.
    I found them with a string search.
    I took every 20-base sequence near the start and end of each gene in the Wuhan
    genome, and kept the ones found exactly once in all five genomes.
    The spike start anchor begins with `ATG`, the start codon of the spike gene, and
    the N gene end anchor ends with `TAA`, the stop codon of the N gene.

    **Note**: You do not need to edit the code below.
    """)
    return


@app.cell
def _():
    # The start of the spike gene
    spike_start_anchor = "ATGTTTGTTTTTCTTGTTTT"
    # The boundary between the S1 and S2 parts of the spike gene
    spike_end_anchor = "TCGGCGGGCACGTAGTGTAG"

    # Near the start of the N gene
    n_start_anchor = "AATGGACCCCAAAATCAGCG"
    # The end of the N gene
    n_end_anchor = "CTGACTCAACTCAGGCCTAA"
    return n_end_anchor, n_start_anchor, spike_end_anchor, spike_start_anchor


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 1: Extracting a gene region (3 points) </font>

    Complete the `extract_region` function below.
    It should return the part of `genome` that starts at the **beginning** of
    `start_anchor` and ends at the **end** of `end_anchor`, so that both anchors are
    included in the region it returns.

    A recipe for the function:

    1.  Use the `.find()` string method to get the index where `start_anchor` begins
        in `genome`, and store it in a variable
    2.  Do the same for `end_anchor`
    3.  Use `assert` to make sure **both** anchors were found (see the warning
        below)
    4.  Use slicing to store the region of the genome in the `region` variable.
        Remember that the region should *include* all of `end_anchor`, so think
        carefully about where your slice needs to stop.

    Replace the "`# Add your code here!`" comment line with your code to complete
    the function.

    /// warning | `.find()` does not complain when it fails
    If `.find()` cannot find what you are searching for, it does not raise an
    error; it returns `-1`.
    If you slice with a `-1` by mistake, you will silently get back the wrong
    sequence (often an empty one), and every step after this will be wrong without
    any warning.
    Use `assert` to stop the function if either anchor is missing.
    For example, `assert start_index >= 0` will stop the function with an
    `AssertionError` if `start_index` is `-1`.
    ///
    """)
    return


@app.function
def extract_region(genome, start_anchor, end_anchor):
    """Extract the region of a genome between (and including) two anchors.

    Args:
        genome (str): The genome sequence to search.
        start_anchor (str): A short sequence marking the start of the region.
        end_anchor (str): A short sequence marking the end of the region.

    Returns:
        str: The part of `genome` from the first base of `start_anchor` to the
            last base of `end_anchor`.

    Raises:
        AssertionError: If either anchor is not found in `genome`.

    Examples:
        >>> extract_region("GGGGTTTTACGTCCCCAAAA", "TTTT", "CCCC")
        'TTTTACGTCCCC'
    """
    region = ""
    # Add your code here!
    return region


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function. **Note**: you do not need to edit the code in
    the cell below.
    """)
    return


@app.cell
def _():
    _test_genome = "GGGGTTTTACGTCCCCAAAA"
    _passed = True

    # Test 1: Does it return the right region, including both anchors?
    _region = extract_region(_test_genome, "TTTT", "CCCC")
    if _region != "TTTTACGTCCCC":
        _passed = False
        print(f"""Test 1 failed: extract_region should have returned
    'TTTTACGTCCCC', but it returned '{_region}'.""")

    # Test 2: Does it stop when an anchor is missing?
    for _start, _end in [("TTTT", "GATTACA"), ("GATTACA", "CCCC")]:
        try:
            extract_region(_test_genome, _start, _end)
            _passed = False
            print(f"""Test 2 failed: extract_region should have raised an
    AssertionError when searching for anchors '{_start}' and '{_end}', because one
    of them is not in the genome.""")
        except AssertionError:
            pass

    if _passed:
        print("Yay, your function passed the test!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, let's use your function to extract both genes from all five genomes.
    **Note**: you do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(
    n_end_anchor,
    n_start_anchor,
    spike_end_anchor,
    spike_start_anchor,
    variant_genomes,
    variant_names,
):
    spike_sequences = []
    n_sequences = []
    for _genome in variant_genomes:
        _spike_seq = extract_region(_genome, spike_start_anchor, spike_end_anchor)
        spike_sequences.append(_spike_seq)
        _n_seq = extract_region(_genome, n_start_anchor, n_end_anchor)
        n_sequences.append(_n_seq)

    print("Variant    spike S1    N gene")
    for _index in range(len(variant_names)):
        print(
            f"{variant_names[_index]:8} {len(spike_sequences[_index]):6} bases",
            f"{len(n_sequences[_index]):5} bases",
        )
    return (spike_sequences,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 2: Why not use whole genomes? (2 points) </font>

    You may be wondering why we are working with two genes rather than whole
    genomes.
    The reason comes down to what you learned in the complexity exercise.

    Filling a Needleman-Wunsch scoring matrix for two sequences of length $n$
    requires $O(n^2)$ time.
    When I tested this notebook, aligning one pair of spike S1 regions (about 2,000
    bases each) took about **2 seconds**.

    Double-click this cell and answer the questions below.

    **The whole genomes are about 30,000 bases long. Roughly how long would it take
    to align one pair of whole genomes? How long would it take to align all 10 pairs
    of our five genomes? Show your reasoning.**

    **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 2: Measuring how different two sequences are

    The tree building method we will use later needs a single number for each pair
    of sequences that says how different they are: A ***distance***.

    Once two sequences are aligned, the simplest distance is to count the columns
    where they differ.
    In the complexity exercise, we did exactly that with this function:

    ```python
    def hamming_distance(seq_a, seq_b):
        "Count of positions where two equal-length strings differ."
        dist = 0
        # Make sure the sequences have equal length
        assert len(seq_a) == len(seq_b)
        # Loop over each base
        for base_index in range(len(seq_a)):
            if seq_a[base_index] != seq_b[base_index]:
                # The sequences differ, so add to the distance
                dist += 1
        return dist
    ```

    That function has a problem with our real data.
    It counts **every** column where the two characters differ, including:

    -   Columns where one sequence has an `N`. An `N` is missing data, so we do not
        know whether the bases really differ.
    -   Columns where one sequence has a gap (`-`).
        We will leave gaps out of our distance and count only substitutions.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 3: Counting only real differences (3 points) </font>

    Complete the `count_differences` function below.
    It should work like the `hamming_distance` function shown above, except that it
    should only count a column as a difference if **both** characters are one of
    `A`, `C`, `G`, or `T` **and** the two characters are not the same.

    /// tip
    Remember the `gc_content` function from the complexity exercise, which used
    "`if base in "GC":`" to check whether a base was a `G` or a `C`?
    You can use the same logic here:
    "`base in "ACGT"`" will be `True` if `base` is a
    nucleotide, and `False` if it is an `N` or a gap (`-`).

    You can combine several conditions in one `if` statement with `and`, for example
    `if (base_1 in "ACGT") and (base_2 in "ACGT") and (...):`
    ///

    Replace the "`# Add your code here!`" comment line with your code to complete
    the function.
    """)
    return


@app.function
def count_differences(aligned_seq_1, aligned_seq_2):
    """Count substitutions between two aligned sequences.

    A column counts as a difference only if both characters are nucleotides
    (A, C, G, or T) and they are not the same. Columns containing a gap ("-")
    or an ambiguous base (such as "N") in either sequence are skipped.

    Args:
        aligned_seq_1 (str): The first aligned sequence.
        aligned_seq_2 (str): The second aligned sequence, the same length as
            `aligned_seq_1`.

    Returns:
        int: The number of columns with a nucleotide substitution.

    Examples:
        >>> count_differences("ACGT", "ACCT")
        1
        >>> count_differences("ANGT-A", "ACCTTA")
        1
    """
    assert len(aligned_seq_1) == len(aligned_seq_2)
    differences = 0
    # Add your code here!
    return differences


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function. **Note**: you do not need to edit the code in
    the cell below.
    """)
    return


@app.cell
def _():
    # Each test is: (aligned_seq_1, aligned_seq_2, expected count, what it checks)
    _tests = [
        ("ACGTACGT", "ACCTACGA", 2, "counting substitutions"),
        ("ACGTNCGT", "ACCTACGA", 2, "skipping an N in the first sequence"),
        ("ACGTACGT", "ACCTNCGN", 1, "skipping Ns in the second sequence"),
        ("ACGT-CGT", "ACCTACG-", 1, "skipping gaps in either sequence"),
    ]
    _passed = True
    for _seq_1, _seq_2, _expected, _description in _tests:
        _result = count_differences(_seq_1, _seq_2)
        if _result != _expected:
            _passed = False
            print(f"""Failed the test for {_description}:
        {_seq_1}
        {_seq_2}
    should have {_expected} difference(s), but your function returned {_result}.
    """)
    if _passed:
        print("Yay, your function passed the test!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 4: Why skip the Ns? (2 points) </font>

    Look back at the output of the cell where we extracted the genes.
    The N gene from the Omicron genome is about the same length as the others, but
    227 of its bases are `N`s.

    Double-click this cell and answer the question below.

    **If we used the original `hamming_distance` function, which counts every `N` as
    a difference, what would happen to the distances between Omicron and the other
    variants in the N gene? Why would that be misleading?**

    **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 3: Building a distance matrix

    The method we will use to build a tree of the SARS-CoV-2 variants
    needs the distance between **every pair** of our five
    sequences, stored in a ***distance matrix***.
    Like the scoring matrix from the sequence alignment exercise, a distance matrix
    is a list of lists.
    Row `i`, Column `j` holds the distance between Sequence `i` and Sequence `j`.

    Two properties of a distance matrix make our job easier:

    -   The distance from a sequence to itself is 0, so the top-left to bottom-right
        diagonal across the matrix is all 0s
    -   The distance from Sequence `i` to Sequence `j` is the same as from `j` to
        `i`, so the matrix is **symmetric**: `matrix[i][j]` equals `matrix[j][i]`

    Because of the symmetry, we only need to align each pair **once**, and then we
    can store the distance in both places (`matrix[i][j]` and `matrix[j][i]`).
    That is why the inner loop below starts at `i + 1`: It only visits the cells
    above the top-left to bottom-right diagonal across the matrix.

    ## <font color=red> Challenge 5: Building the distance matrix (3 points) </font>

    The nested loop in `get_distance_matrix` below visits every pair of sequences.
    Inside the inner loop, replace the `# Add your code here!` comment with code
    that:

    1.  Aligns `sequences[i]` with `sequences[j]` using the `align_sequences`
        function
    2.  Counts the differences between the two **aligned** sequences using your
        `count_differences` function
    3.  Stores that count in the distance matrix, in **both** `distance_matrix[i][j]`
        and `distance_matrix[j][i]`

    /// tip
    Remember that `align_sequences` returns three things: The two aligned
    sequences and the score.
    You can catch all three at once using, for example,
    `aligned_1, aligned_2, score = align_sequences(seq_1, seq_2)`
    ///
    """)
    return


@app.function
def get_distance_matrix(sequences):
    """Build a matrix of pairwise distances among a list of sequences.

    Each pair of sequences is aligned with `align_sequences`, and their
    distance is the number of substitutions between the aligned sequences, as
    counted by `count_differences`.

    Args:
        sequences (list[str]): The (unaligned) sequences to compare.

    Returns:
        list[list[int]]: A symmetric matrix where row `i`, column `j` holds the
            distance between `sequences[i]` and `sequences[j]`.
    """
    number_of_sequences = len(sequences)
    # Start with a matrix of zeros
    distance_matrix = []
    for _ in range(number_of_sequences):
        distance_matrix.append([0] * number_of_sequences)
    # Visit every pair of sequences once
    for i in range(number_of_sequences):
        for j in range(i + 1, number_of_sequences):
            print(f"Aligning sequence {i} with sequence {j}")
            # Add your code here!
    return distance_matrix


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function on four short sequences.
    **Note**: you do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _test_sequences = ["ACGT", "ACGA", "AGGA", "ACGN"]
    _expected = [
        [0, 1, 2, 0],
        [1, 0, 1, 0],
        [2, 1, 0, 1],
        [0, 0, 1, 0],
    ]
    _result = get_distance_matrix(_test_sequences)
    print()

    _symmetric = True
    for _i in range(len(_result)):
        for _j in range(len(_result)):
            if _result[_i][_j] != _result[_j][_i]:
                _symmetric = False

    if _result == _expected:
        print("Yay, your function passed the test!")
    elif not _symmetric:
        print(f"""Sorry, your distance matrix is not symmetric:
    {_result}
    Did you store each distance in both [i][j] and [j][i]?""")
    else:
        print(f"""Sorry, your get_distance_matrix function should have returned
    {_expected}
    but it returned
    {_result}
    Please try again!""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The function below creates a nice Markdown-formatted table from a distance
    matrix.
    We will use it later to visualize the distance matrices we create.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.function
def distance_matrix_to_markdown(names, distance_matrix):
    """Render a distance matrix as a Markdown table."""
    header = "|   | " + " | ".join(f"**{name}**" for name in names) + " |"
    rule = "|:--|" + "--:|" * len(names)
    lines = [header, rule]
    for i in range(len(names)):
        cells = " | ".join(str(value) for value in distance_matrix[i])
        lines.append(f"| **{names[i]}** | " + cells + " |")
    return "\n".join(lines)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 4: Building a tree

    The functions below turn a distance matrix into a tree and draw it.
    **You do not need to edit these functions**,
    but I encourage you to read through them and try to understand how they work.
    The functions use the Biopython library, which is a widely used collection of
    tools for computational biology.
    """)
    return


@app.function
def build_tree(names, distance_matrix, method = "nj", outgroup = "Wuhan"):
    """Estimate a tree from a distance matrix.

    Args:
        names (list[str]): The name of each sequence, in the same order as the
            rows of `distance_matrix`.
        distance_matrix (list[list[int]]): A symmetric matrix of distances.
        method (str): "nj" for neighbor-joining (rooted with `outgroup`), or
            "upgma" for UPGMA (which produces a rooted tree on its own).
        outgroup (str): The name of the sequence to root a neighbor-joining tree
            with.

    Returns:
        Bio.Phylo.BaseTree.Tree: The estimated tree.
    """
    from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor

    # Biopython wants only the lower triangle of the matrix, including the diagonal
    lower_triangle = []
    for i in range(len(names)):
        lower_triangle.append(distance_matrix[i][: i + 1])
    biopython_matrix = DistanceMatrix(list(names), lower_triangle)

    constructor = DistanceTreeConstructor()
    if method == "upgma":
        return constructor.upgma(biopython_matrix)
    tree = constructor.nj(biopython_matrix)
    tree.root_with_outgroup(outgroup)
    return tree


@app.function
def draw_tree(tree, title):
    """Draw a tree with its branch lengths labeled, and return the figure."""
    import matplotlib.pyplot as plt
    from Bio import Phylo

    figure, axes = plt.subplots(figsize=(7, 4))
    Phylo.draw(
        tree,
        axes=axes,
        do_show=False,
        # Label only the tips of the tree with names
        label_func=lambda clade: clade.name if clade.is_terminal() else None,
        # Label each branch with its length
        branch_labels=lambda clade: (
            f"{clade.branch_length:.1f}" if clade.branch_length else None
        ),
    )
    axes.set_title(title)
    axes.set_xlabel("Branch length (number of differences)")
    axes.set_ylabel("")
    axes.set_yticks([])
    return figure


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The neighbor-joining algorithm

    We will estimate our trees with the ***neighbor-joining*** algorithm, introduced
    by Naruya Saitou and Masatoshi Nei in 1987.
    Their paper has been cited more than 60,000 times, making it one of the most
    cited papers in all of biology.
    <!-- TODO (Jamie): update with current citation statistics. -->
    It is still used every day, because it works quite well and is very fast.

    The idea behind the neighbor-joining algorithm is simple.
    Start with every sequence as its own separate tip.
    Then, over and over, find the pair of tips that are closest to each other
    (after adjusting for how far each tip is from *everything else*), join them
    together as "neighbors," and treat the pair as a single new tip.
    Keep going until everything is joined into one tree.

    Neighbor-joining produces an ***unrooted*** tree: It tells us which sequences
    group together, but not which point on the tree is the oldest (the root of the
    tree).
    To decide that, we ***root*** the tree with a sequence we know to be outside the
    group of interest.
    We will root our trees with the Wuhan reference genome.

    Now, we can compute the distance matrix for the spike S1 sequences and build our
    first tree.
    This takes a while (about 20 seconds in my testing), so the cell below will not
    run until you click the button.
    If you edit any of your functions above, you will need to click the button
    again.
    **Note**: You do not need to edit the code in the next cell.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    spike_run = mo.ui.run_button(
        label="Align the spike S1 sequences", kind="success"
    )
    spike_run
    return (spike_run,)


@app.cell
def _(mo, spike_run, spike_sequences, variant_names):
    mo.stop(
        not spike_run.value,
        mo.md("***Waiting — click the button above to align the spike S1 sequences.***"),
    )
    spike_distances = get_distance_matrix(spike_sequences)
    mo.md(distance_matrix_to_markdown(variant_names, spike_distances))
    return (spike_distances,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, let's use the `build_tree` function to build a neighbor-joining tree
    relating the spike S1 sequences, and the `draw_tree` function to visualize the
    tree. **Note**: You do not need to edit the next cell
    """)
    return


@app.cell
def _(spike_distances, variant_names):
    spike_tree = build_tree(variant_names, spike_distances)
    draw_tree(spike_tree, "Spike S1")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Connecting the tree to the pandemic

    The table below lists what we know about each of our samples.
    Each variant has a WHO name (like "Alpha") and a **Pango lineage** name.
    Pango lineage names are hierarchical, like an address: `B.1.1.7` is a
    descendant of `B.1.1`, which is a descendant of `B.1`, which is a descendant of
    `B`.
    Very long names get a shorter alias; Gamma's lineage `P.1` is short for
    `B.1.1.28.1`.

    | Sample | Pango lineage | First detected |
    |:--|:--|:--|
    | Wuhan reference | B | China, December 2019 |
    | Alpha | B.1.1.7 | United Kingdom, September 2020 |
    | Delta | B.1.617.2 | India, October 2020 |
    | Gamma | P.1 (B.1.1.28.1) | Brazil, November 2020 |
    | Omicron | B.1.1.529 | Southern Africa, November 2021 |

    ## <font color=red> Challenge 6: Reading the spike tree (3 points) </font>

    Double-click this cell and answer the questions below.

    1.  **We rooted the tree with the Wuhan reference genome. Based on the table
        above, why is that a reasonable choice?**

        **Answer**:

    2.  **Of the remaining four variants, which three group together in your tree,
        separate from the fourth? Is that grouping consistent with their Pango
        lineage names? Explain.**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 5: Does the N gene tell the same story?

    Now, let's repeat the analysis for the N gene.

    ## <font color=red> Challenge 7: Get the distance matrix for the N gene (1 point) </font>

    In the second cell below (the one under the button), replace the
    `n_distances = []` line with your code to get the distance matrix for the
    `n_sequences` (the sequences from the N gene).
    The N gene is shorter than the spike S1 region, so this should run a bit faster.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    n_run = mo.ui.run_button(label="Align the N gene sequences", kind="success")
    n_run
    return (n_run,)


@app.cell
def _(mo, n_run, variant_names):
    mo.stop(
        not n_run.value,
        mo.md("***Waiting — click the button above to align the N gene sequences.***"),
    )

    # Replace the line below with your code!
    n_distances = []

    mo.stop(
        not n_distances,
        mo.md(
            "***Waiting — replace the `n_distances = []` line above with your code.***"
        ),
    )
    mo.md(distance_matrix_to_markdown(variant_names, n_distances))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 8: Build and show the phylogeny for the N gene (2 points) </font>

    In the Python cell below, replace the "`# Add your code here!`" comment with
    your code to build the neighbor-joining tree using the `n_distances` distance
    matrix you created above.
    After you get the neighbor-joining tree for the N gene sequences, use the
    appropriate function from above to visualize it.

    /// note
    You only need to provide the variant names and distance matrix to the
    `build_tree` function.
    *I.e.*, you can use the defaults for the `method` and `outgroup` arguments,
    because we want to use the neighbor-joining algorithm and the Wuhan sequence as
    the outgroup.
    ///
    """)
    return


@app.cell
def _():
    # Add your code here!
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 9: Comparing the two genes (4 points) </font>

    Compare your spike S1 tree to your N gene tree.
    The numbers on the branches are branch lengths, which represent the number of
    differences that accumulated along each branch.

    Double-click this cell and answer the questions below.

    1.  **Do the two trees agree about which variants group together?**

        **Answer**:

    2.  **Look at the length of Omicron's branch in each tree. How does it
        differ between the spike S1 tree and the N gene tree?**

        **Answer**:

    3.  **Using what you learned about the spike protein in Part 1, propose a
        biological explanation for this difference. (Hint: Omicron appeared in
        November 2021, nearly two years into the pandemic. What had happened to
        the immune systems of much of the world's population by then?)**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Extra credit challenge (3 points) </font>

    Neighbor-joining is not the only way to build a tree from a distance matrix.
    A simpler method called ***UPGMA*** repeatedly joins whichever two tips are
    closest (have the smallest distance), without adjusting for how far each tip is
    from everything else.
    That simplicity comes with a hidden assumption: That every lineage has
    accumulated changes at the **same rate** and for the **same amount of time**.

    In the cell below, **build** and **draw** a UPGMA tree from the spike S1
    distances by using the appropriate functions from above.
    When you use the `build_tree` function, you will need to "tell it"
    to use the UPGMA algorithm, rather than neighbor-joining.
    Look at the docstring of that function for how to do this correctly.

    /// tip
    The UPGMA tree will be different from the neighbor-joining tree you built from
    the spike S1 distances.
    If your tree below looks the same as the neighbor-joining tree above, you did
    not correctly "tell" the `build_tree` function to use the UPGMA algorithm.
    ///

    After you draw the UPGMA tree, answer the following questions.
    One of the three extra credit points is for your code, and one is for each of
    your answers below.

    1.  **Where does the Wuhan virus end up? Does that make sense, given that it is
        the oldest sample?**

        **Answer**:

    2.  **Which of our variants break the assumption of the UPGMA algorithm, and
        how?**

        **Answer**:
    """)
    return


@app.cell
def _():
    # Write your extra credit code here
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    Starting from five raw genome sequences, you:

    -   Used a **string search** to extract the same two genes from each genome
    -   **Aligned** every pair of sequences with your Needleman-Wunsch code
    -   Built a **distance matrix** that ignores missing data and gaps
    -   Estimated **phylogenies** with the neighbor-joining algorithm, one of the
        most cited methods in all of biology!!

    Your trees recovered the relationships among the variants that are encoded in
    their lineage names, and they revealed that the Omicron lineage's evolution was
    concentrated in the spike gene, the part of the genome under the strongest
    pressure from our immune systems.
    That is the same kind of analysis that genomic surveillance teams around the
    world ran throughout the pandemic to track new variants as they emerged.
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

    I used Anthropic's Claude (Opus 5 model) to generate a draft of this capstone
    project.
    """)
    return


@app.cell(hide_code=True)
def _():
    # You can ignore this cell

    # This cell contains hidden code to make sure any files we use in this
    # notebook are present.
    # If you are curious, when you see the `local_files` variable in the
    # notebook, it gets created in this cell and its sole purpose is to ensure
    # files are present before we try to work with them.

    def setup_local_file(file_name):
        import os
        import urllib.request

        url = f"https://raw.githubusercontent.com/phyletica/intro-to-comp-bio/refs/heads/main/notebooks/data/{file_name}"

        # Download the file if it doesn't already exist in the environment
        if not os.path.exists(file_name):
            try:
                urllib.request.urlretrieve(url, file_name)
            except Exception as e:
                print(f"Failed to download file: {url}")
                raise e
        return file_name

    file_names = [
        "SARS-CoV-2-unaligned.fasta",
    ]
    local_files = [setup_local_file(f) for f in file_names]
    return (local_files,)


if __name__ == "__main__":
    app.run()
