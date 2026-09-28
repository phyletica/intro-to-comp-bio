# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.0",
#     "matplotlib",
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
    # Building a simple BLAST

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Searching large databases

    Many of you have used the
    [Basic Local Alignment Search Tool (BLAST)](https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGETYPE=BLASTHome)
    to search
    [GenBank](https://www.ncbi.nlm.nih.gov/genbank/).
    BLAST lets you paste in a sequence, click a button, and, a few seconds later,
    get a list of similar sequences from a database containing tens of
    trillions of nucleotides.

    In the last exercise, you built an **optimal** sequence aligner.
    Today, you will see why an optimal aligner cannot scale to search such large
    databases, and you will build a simplified version of the heuristic that BLAST
    uses instead.
    The pleasing thing is that you have already written nearly every piece of it:

    -   From the string search exercise: The **$k$-mer dictionary**, which lets us
        look up short exact matches instantly
    -   From the alignment exercise: The **Needleman-Wunsch** aligner, which we will
        turn into a **Smith-Waterman** local aligner today

    Our plan for this exercise is to:

    1.  Turn your global aligner into a **local** aligner (Smith-Waterman)
    2.  Use it to search a small database of viral genomes, and time it
    3.  Find **seeds**: Short exact matches between a query sequence and the
        database
    4.  **Extend** the seeds into alignments, and compare to the optimal search
    5.  Explore the trade-off between **speed and sensitivity**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: From Needleman-Wunsch to Smith-Waterman

    Recall from lecture that a local alignment finds the best-scoring alignment
    between **any part** of one sequence and **any part** of the other.
    That is exactly the question BLAST asks: "Is there some region of this database
    sequence that is similar to some region of my query sequence?"

    To do such a local alignment, the Smith-Waterman algorithm makes three changes
    to Needleman-Wunsch:

    | Change | Needleman-Wunsch (global) | Smith-Waterman (local) |
    |:--|:--|:--|
    | 1 | Cell scores can be negative | A cell score can never drop below **0** |
    | 2 | Traceback starts in the bottom-right cell | Traceback starts at the **highest-scoring cell** |
    | 3 | Traceback stops at the top-left cell | Traceback stops at the first cell holding **0** |

    You will make all three changes to your code from the sequence alignment
    exercise.

    First, some helper functions from last time.
    **You do not need to edit these**.
    """)
    return


@app.function
def score_pair(base_1, base_2, match = 1, mismatch = -1, gap = -2):
    """Score a single column of an alignment.

    Args:
        base_1 (str): A single character from the first sequence, which may be
            a gap character ("-").
        base_2 (str): A single character from the second sequence, which may be
            a gap character ("-").
        match (int): The score for two identical bases.
        mismatch (int): The score for two different bases.
        gap (int): The score for a column containing a gap.

    Returns:
        int: The score of this column.

    Examples:
        >>> score_pair("A", "A")
        1
        >>> score_pair("A", "G")
        -1
        >>> score_pair("A", "-")
        -2
    """
    # A gap in either sequence costs the gap penalty
    if (base_1 == "-") or (base_2 == "-"):
        return gap
    # Two identical bases are a match
    if base_1 == base_2:
        return match
    # Anything else is a mismatch
    return mismatch


@app.function
def get_initial_matrix(seq_1, seq_2, gap = -2):
    """Create a scoring matrix with its first row and column filled in.

    The matrix has one more row than the length of `seq_1` and one more column
    than the length of `seq_2`. Row 0 and column 0 hold the score of aligning a
    prefix of one sequence against nothing but gaps.

    Args:
        seq_1 (str): The sequence along the rows.
        seq_2 (str): The sequence along the columns.
        gap (int): The score for a column containing a gap.

    Returns:
        list[list[int]]: The matrix, with row 0 and column 0 filled in and every
            other cell set to 0.

    Examples:
        >>> get_initial_matrix("AC", "A")
        [[0, -2], [-2, 0], [-4, 0]]
        >>> get_initial_matrix("AC", "A", gap = 0)
        [[0, 0], [0, 0], [0, 0]]
    """
    number_of_rows = len(seq_1) + 1
    number_of_columns = len(seq_2) + 1
    # Build a matrix of zeros, one row at a time
    matrix = []
    for i in range(number_of_rows):
        matrix.append([0] * number_of_columns)
    # Fill in the first column: aligning i bases of seq_1 against nothing but
    # gaps
    for i in range(1, number_of_rows):
        matrix[i][0] = i * gap
    # Fill in the first row: aligning j bases of seq_2 against nothing but gaps
    for j in range(1, number_of_columns):
        matrix[0][j] = j * gap
    return matrix


@app.function
def matrix_to_markdown(matrix, seq_1, seq_2):
    """Render a scoring matrix as a Markdown table.

    Args:
        matrix (list[list[int]]): A scoring matrix.
        seq_1 (str): The sequence along the rows.
        seq_2 (str): The sequence along the columns.

    Returns:
        str: Markdown-formatted text that renders as a table.
    """
    row_labels = "-" + seq_1
    column_labels = "-" + seq_2
    header = "|   | " + " | ".join(f"**{b}**" for b in column_labels) + " |"
    rule = "|:--|" + "--:|" * len(column_labels)
    lines = [header, rule]
    for row_index in range(len(matrix)):
        cells = " | ".join(str(value) for value in matrix[row_index])
        lines.append(f"| **{row_labels[row_index]}** | " + cells + " |")
    return "\n".join(lines)


@app.function
def print_alignment(aligned_1, aligned_2, score = None):
    """Print a pairwise alignment with a match line between the sequences.

    Args:
        aligned_1 (str): The first aligned sequence.
        aligned_2 (str): The second aligned sequence.
        score (int): The alignment score to print underneath, if any.
    """
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
    ## <font color=red> Challenge 1: Scores never drop below zero </font>

    The function below is the `fill_scoring_matrix` function from the alignment
    exercise, renamed to `fill_local_scoring_matrix`.
    Two things are different already:

    -   The initial scoring matrix is created using the `get_initial_matrix`
        function with `gap = 0`. This gets us the initial matrix we need, in which
        Row 0 and Column 0 are all zeros (rather than multiples of the gap penalty).
        In a local alignment, skipping over the beginning of either sequence is free,
        because the alignment can start anywhere!
    -   There is a place marked **Change 1** inside the nested loop.

    Change the line that sets `matrix[i][j]` to the maximum of the three
    Needleman-Wunsch options to ensure that 0 is the lowest possible score.

    That is all it takes!
    When a cell would go negative, the algorithm gives up on the alignment, rather
    than dragging a bad score forward.

    /// tip
    Think about what has to be true for `max(diagonal, up, left)` to return a
    negative number.
    How can you update it, so the smallest number it will ever return is zero?
    ///
    """)
    return


@app.function
def fill_local_scoring_matrix(seq_1, seq_2, match = 1, mismatch = -1, gap = -2):
    """Fill a Smith-Waterman (local alignment) scoring matrix for two sequences.

    Every cell holds the score of the best local alignment that ends at that
    row (base of `seq_1`) and column (base of `seq_2`), or 0 if every alignment
    ending there has a negative score.

    Args:
        seq_1 (str): The sequence along the rows.
        seq_2 (str): The sequence along the columns.
        match (int): The score for two identical bases.
        mismatch (int): The score for two different bases.
        gap (int): The score for a column containing a gap.

    Returns:
        list[list[int]]: The completed scoring matrix.

    Examples:
        >>> fill_local_scoring_matrix("AC", "A")
        [[0, 0], [0, 1], [0, 0]]
    """
    # For a local alignment, row 0 and column 0 are all zeros
    matrix = get_initial_matrix(seq_1, seq_2, gap = 0)
    # Adding 1 to the number of rows/columns for the first row/column
    number_of_rows = len(seq_1) + 1
    number_of_columns = len(seq_2) + 1
    for i in range(1, number_of_rows):
        for j in range(1, number_of_columns):
            diagonal = matrix[i - 1][j - 1] + score_pair(
                seq_1[i - 1], seq_2[j - 1], match, mismatch, gap
            )
            up = matrix[i - 1][j] + gap
            left = matrix[i][j - 1] + gap
            # Change 1: A cell score can never drop below 0
            # Modify the next line of code to enforce this rule!
            matrix[i][j] = max(diagonal, up, left)
    return matrix


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function using the two sequences from the end of
    the alignment lecture, which share `ACGTCA` at opposite ends.
    **Note**: You do not need to edit the code in the cell below.
    Compare your matrix to the one on the slides.
    """)
    return


@app.cell
def _(mo):
    local_seq_1 = "TTTTACGTCA"
    local_seq_2 = "ACGTCAGGGG"
    local_matrix = fill_local_scoring_matrix(local_seq_1, local_seq_2)
    expected_local_matrix = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 1, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 4, 2, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 2, 5, 3, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 3, 6, 4, 2, 0, 0],
    ]

    if local_matrix == expected_local_matrix:
        _message = "Yay, your function passed the test!"
    else:
        _message = """Sorry, your fill_local_scoring_matrix function did not produce
    the matrix from lecture. Find the first cell that disagrees with the slides.
    Please try again!"""

    print(_message)

    mo.md(matrix_to_markdown(local_matrix, local_seq_1, local_seq_2))
    return local_seq_1, local_seq_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 2: Tracing back a local alignment </font>

    The two remaining changes are both about the traceback.

    ### <font color=red> Part A: Find the highest-scoring cell (Change 2) </font>

    The best local alignment **ends** at the highest-scoring cell, wherever it is
    in the matrix.
    Complete the `find_best_cell` function below so that it returns the row index
    and column index of the largest value in the matrix.

    A recipe:

    1.  `best_i` and `best_j` start at 0, which means "the best cell I have seen so
        far is `matrix[0][0]`", which is always zero!
    2.  Write a **nested loop** that visits every cell, just like the loops you
        wrote for the dotplot and the scoring matrix in the last exercise, but here,
        start at 0, not 1.
    3.  Inside the inner loop, if `matrix[i][j]` is **greater than**
        `matrix[best_i][best_j]`, update `best_i` to `i` and `best_j` to `j`

    /// tip
    `len(matrix)` is the number of rows, and `len(matrix[i])` is the number of
    columns in row `i`.
    These pieces of code will be useful when you need to use the range function to
    loop over the rows and then the columns of each row.
    ///
    """)
    return


@app.function
def find_best_cell(matrix):
    """Find the row and column of the largest value in a matrix.

    If the largest value appears in more than one cell, the first one found
    (scanning row by row, from the top-left) is returned.

    Args:
        matrix (list[list[int]]): A scoring matrix.

    Returns:
        tuple[int, int]: The row index and column index of the largest value.

    Examples:
        >>> find_best_cell([[0, 0, 0], [0, 2, 0], [0, 0, 1]])
        (1, 1)
    """
    best_i = 0
    best_j = 0
    # Add your code here!
    return best_i, best_j


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your `find_best_cell` function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    best_cell_test_cases = [
        ([[0, 0, 0], [0, 2, 0], [0, 0, 1]], (1, 1)),
        ([[0, 0, 0], [0, 1, 0], [0, 0, 3]], (2, 2)),
        ([[0, 0, 5], [0, 1, 0], [0, 0, 3]], (0, 2)),
        ([[0, 0, 0], [0, 4, 0], [0, 0, 4]], (1, 1)),
    ]
    best_cell_failures = []
    for _matrix, _expected in best_cell_test_cases:
        _found = find_best_cell(_matrix)
        if _found != _expected:
            best_cell_failures.append(f"  expected {_expected}, got {_found}")

    if best_cell_failures:
        _message = "Sorry, find_best_cell failed these cases:\n" + "\n".join(
            best_cell_failures
        )
    else:
        _message = "Yay, your function passed the test!"

    print(_message)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### <font color=red> Part B: Stop at a zero (Change 3) </font>

    The function below is the `traceback_alignment` function from the alignment
    exercise, with two changes already made for you:

    -   It starts at the cell returned by your `find_best_cell` function
    -   The `while` loop stops at the top or left edge of the matrix (by using
        "`and`" instead of "`or`" in the `while` statement), because a local
        alignment never traces back along an edge.
        Remember, the edges (Row 0 and Column 0) are always zeros in the
        Smith-Waterman scoring matrix and negative numbers in the Needleman-Wunsch!

    Your job is to make one additional change to the `traceback_alignment` function.
    At the place marked with "`# Add your code here!`" in the `while` loop, add an
    `if` statement that uses the `break` keyword to stop the loop as soon as
    `matrix[i][j]` is `0`.
    A zero means "the local alignment started here," so there is nothing more to
    trace.

    /// note
    `break` immediately ends the loop it is in.
    When Python encounters `break`, it jumps to the first line after the loop.
    For example, this loop prints 0, 1, and 2 and then stops:

    ```python
    for number in range(10):
        if number == 3:
            break
        print(number)
    ```
    ///

    The function also returns `i` and `j` after the loop ends.
    Those are the (zero-based) positions where the local alignment **starts** in
    `seq_1` and `seq_2`, respectively, which we will need when we search a database.
    """)
    return


@app.function
def traceback_local_alignment(
    matrix,
    seq_1,
    seq_2,
    match = 1,
    mismatch = -1,
    gap = -2,
):
    """Recover the optimal local alignment from a filled scoring matrix.

    Starts at the highest-scoring cell and walks backward until it reaches a
    cell holding 0, building the two aligned sequences from right to left.

    Args:
        matrix (list[list[int]]): A completed local scoring matrix, as returned
            by `fill_local_scoring_matrix`.
        seq_1 (str): The sequence along the rows.
        seq_2 (str): The sequence along the columns.
        match (int): The score for two identical bases.
        mismatch (int): The score for two different bases.
        gap (int): The score for a column containing a gap.

    Returns:
        tuple[str, str, int, int]: The two aligned sequences (with gap
            characters inserted), followed by the zero-based positions in
            `seq_1` and `seq_2` where the local alignment starts.

    Examples:
        >>> traceback_local_alignment(
        ...     fill_local_scoring_matrix("TTTTACGTCA", "ACGTCAGGGG"),
        ...     "TTTTACGTCA", "ACGTCAGGGG")
        ('ACGTCA', 'ACGTCA', 4, 0)
    """
    # Create empty strings to hold the aligned sequences
    aligned_1 = ""
    aligned_2 = ""
    # Change 2: Start at the highest-scoring cell
    i, j = find_best_cell(matrix)
    # Keep looping until we reach the top or left edge of the matrix
    while (i > 0) and (j > 0):
        # Change 3: Stop tracing back when we reach a cell holding 0
        # Add your code here!
        pair_score = score_pair(seq_1[i - 1], seq_2[j - 1], match, mismatch, gap)
        if matrix[i][j] == matrix[i - 1][j - 1] + pair_score:
            # Diagonal step: the two bases are aligned to each other
            aligned_1 = seq_1[i - 1] + aligned_1
            aligned_2 = seq_2[j - 1] + aligned_2
            i = i - 1
            j = j - 1
        elif matrix[i][j] == matrix[i - 1][j] + gap:
            # Up step: a base of seq_1 is aligned to a gap in seq_2
            aligned_1 = seq_1[i - 1] + aligned_1
            aligned_2 = "-" + aligned_2
            i = i - 1
        else:
            # Left step: a base of seq_2 is aligned to a gap in seq_1
            aligned_1 = "-" + aligned_1
            aligned_2 = seq_2[j - 1] + aligned_2
            j = j - 1
    return aligned_1, aligned_2, i, j


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The function below bundles your three changes into one function, just like
    `align_sequences` did in the last notebook.
    **You do not need to edit it.**
    """)
    return


@app.function
def align_local(seq_1, seq_2, match = 1, mismatch = -1, gap = -2):
    """Compute the optimal local alignment of two sequences (Smith-Waterman).

    Args:
        seq_1 (str): The first sequence.
        seq_2 (str): The second sequence.
        match (int): The score for two identical bases.
        mismatch (int): The score for two different bases.
        gap (int): The score for a column containing a gap.

    Returns:
        tuple[str, str, int, int, int]: The two aligned sequences, the score
            of the alignment, and the zero-based positions in `seq_1` and
            `seq_2` where the alignment starts.

    Examples:
        >>> align_local("TTTTACGTCA", "ACGTCAGGGG")
        ('ACGTCA', 'ACGTCA', 6, 4, 0)
    """
    matrix = fill_local_scoring_matrix(seq_1, seq_2, match, mismatch, gap)
    best_i, best_j = find_best_cell(matrix)
    aligned_1, aligned_2, start_1, start_2 = traceback_local_alignment(
        matrix, seq_1, seq_2, match, mismatch, gap
    )
    return aligned_1, aligned_2, matrix[best_i][best_j], start_1, start_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your changes to the traceback.
    **Note**: You do not need to edit the code in the cell below.

    Last time, your global aligner could not find the `ACGTCA` shared by these two
    sequences.
    Let's see if your local aligner can!
    """)
    return


@app.cell
def _(local_seq_1, local_seq_2):
    local_result = align_local(local_seq_1, local_seq_2)
    print_alignment(local_result[0], local_result[1], local_result[2])
    print(f"Starts at position {local_result[3]} of seq_1 and position "
          f"{local_result[4]} of seq_2")
    print()

    if local_result == ("ACGTCA", "ACGTCA", 6, 4, 0):
        print("Yay, your local aligner passed the test!")
    else:
        print("""Sorry, align_local should have returned
    ('ACGTCA', 'ACGTCA', 6, 4, 0)
    but it returned
    """ + str(local_result) + """
    Check Change 3 (and Changes 1 and 2 if their tests failed). Please try again!""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Three small changes, and your aligner now finds the shared region that the
    global aligner did not.
    Smith and Waterman published this algorithm in 1981, and it is still the gold
    standard for finding the best local alignment between two sequences.

    # Part 2: Searching a database with an optimal local aligner

    Now, let's use your Smith-Waterman local aligner the way people use BLAST.

    Suppose you sequenced a sample from a patient with COVID-19 and one of the
    reads you got back is the 150-base sequence in the cell below,
    called `mystery_read`.
    We want to know which variant of SARS-CoV-2 it came from, and where in the
    genome it is.

    Our "database" is the five SARS-CoV-2 genomes you used in the alignment
    exercise.
    The next cell uses the `parse_fasta_file` function from above to get those
    genomes and stores them in the dictionary called `database`.
    It also creates our `mystery_read`.
    **You do not need to edit the next cell**.
    """)
    return


@app.cell
def _(local_files):
    local_files  # Ignore this line; it just ensures the FASTA file is present
    fasta_sequences = parse_fasta_file("SARS-CoV-2-unaligned.fasta")

    # Shorten the names to just the variant (e.g., "Wuhan-gi-1798..." -> "Wuhan")
    database = {}
    for _long_name in fasta_sequences:
        _short_name = _long_name.split("-")[0]
        database[_short_name] = fasta_sequences[_long_name]

    for _name in database:
        print(f"{_name}: {len(database[_name]):,} bases")

    mystery_read = (
        "GTTTTACATTCAACTCAGGACTTGTTCTTACCTTTCTTTTCCAATGTTACTTGGTTCCATGTTATCTCTG"
        + "GGACCAATGGTACTAAGAGGTTTGATAACCCTGTCCTACCATTTAATGATGGTGTTTATTTTGCTTCC"
        + "ATTGAGAAGTCT"
    )
    print()
    print(f"Mystery read ({len(mystery_read)} bases):")
    print(mystery_read)
    return database, mystery_read


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below uses your `align_local` function to find the best local alignment
    between the mystery read and **every whole viral genome** in our database, and
    times how long each one takes.
    This is a search using an optimal local aligner: It is guaranteed to find
    the best-scoring local alignment in each genome.

    Each genome is about 30,000 bases, so each scoring matrix has about
    $150 \times 30{,}000 = 4.5$ million cells.
    This will take a little while, so the cell will wait until you click the button.
    """)
    return


@app.cell
def _():
    import time

    return (time,)


@app.cell(hide_code=True)
def _(mo):
    sw_run = mo.ui.run_button(
        label="Run Smith-Waterman against every genome", kind="success"
    )
    sw_run
    return (sw_run,)


@app.cell
def _(database, mo, mystery_read, sw_run, time):
    mo.stop(
        not sw_run.value,
        mo.md("***Waiting — Click the button above to run the search.***"),
    )

    sw_rows = []
    sw_total_seconds = 0.0
    sw_total_bases = 0
    for _name in database:
        _start_time = time.perf_counter()
        _result = align_local(mystery_read, database[_name])
        _seconds = time.perf_counter() - _start_time
        sw_total_seconds += _seconds
        sw_total_bases += len(database[_name])
        sw_rows.append(
            f"| {_name} | {_result[2]} | {_result[4]:,} | {_seconds:.2f} |"
        )

    sw_seconds_per_million = sw_total_seconds / (sw_total_bases / 1_000_000)

    mo.md(
        "| Genome | Best local score | Starts at position | Seconds |\n"
        + "|:--|--:|--:|--:|\n"
        + "\n".join(sw_rows)
        + f"\n\n**Total**: {sw_total_bases:,} bases searched in "
        + f"**{sw_total_seconds:.1f} seconds**, which is about "
        + f"**{sw_seconds_per_million:.1f} seconds per million bases** of database."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 3: Scaling up to GenBank </font>

    Double-click this cell and answer the questions below.

    GenBank currently holds about **50 trillion** ($5 \times 10^{13}$) bases of
    sequence.
    There are about 31.5 million ($3.15 \times 10^{7}$) seconds in a year.

    1.  **Using your "seconds per million bases" from the table above, how many
        years would it take to search GenBank with this ONE 150-base read? Show your
        arithmetic.**

        **Answer**:

    2.  **Often we need to search GenBank for thousands of sequences.
        Would a faster computer solve this problem? Why or why not?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 3: $k$-mer seeds

    The key insight behind BLAST is simple:
    **Two homologous sequences almost always share at least one short stretch of
    identical bases.**
    So, rather than aligning the query against everything, BLAST first looks for
    short ($k \approx 11$) exact matches, called ***seeds***, and only does
    alignment work near these exact matches.

    And we already know how to find exact matches of length $k$ very fast:
    The $k$-mer dictionary from the string search exercise!
    We build a $k$-mer dictionary of each database sequence **once**, and then every
    lookup is essentially instantaneous.

    Below are the `get_kmer_dict` and `kmer_dict_search` functions you wrote in the
    string search exercise.
    **You do not need to edit these.**
    """)
    return


@app.function
def get_kmer_dict(sequence, k):
    """Build a dictionary of the positions of every k-mer in a sequence.

    Args:
        sequence (str): The sequence to index.
        k (int): The length of the k-mers to use as dictionary keys.

    Returns:
        dict[str, list[int]]: Maps each k-mer that occurs in `sequence` to the
            list of zero-based positions where that k-mer starts, in increasing
            order. The dictionary is empty if `k` is longer than `sequence`.

    Examples:
        >>> get_kmer_dict("ATCGATC", 3)
        {'ATC': [0, 4], 'TCG': [1], 'CGA': [2], 'GAT': [3]}
    """
    kmer_positions = {}
    for position in range(len(sequence) - k + 1):
        kmer = sequence[position:position + k]
        if kmer in kmer_positions:
            kmer_positions[kmer].append(position)
        else:
            kmer_positions[kmer] = [position]
    return kmer_positions


@app.function
def kmer_dict_search(kmer_dict, subsequence):
    """Look up every position of `subsequence` in a k-mer dictionary.

    Args:
        kmer_dict (dict[str, list[int]]): A k-mer dictionary, as returned by
            `get_kmer_dict`.
        subsequence (str): The sequence to look for. Its length must match the
            k that was used to build `kmer_dict`, otherwise it can never be
            found.

    Returns:
        list[int]: The zero-based positions where `subsequence` starts, in
            increasing order. The list is empty if `subsequence` is not one of
            the keys of `kmer_dict`.

    Examples:
        >>> kmer_dict = get_kmer_dict("ATCGATC", 3)
        >>> kmer_dict_search(kmer_dict, "ATC")
        [0, 4]
        >>> kmer_dict_search(kmer_dict, "GGG")
        []
    """
    if subsequence in kmer_dict:
        return kmer_dict[subsequence]
    return []


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 4: Finding seeds </font>

    Complete the `find_seeds` function below.
    It should loop over each position of the query sequence,
    look up the $k$-mer that starts at each position of the query sequence in the
    database's $k$-mer dictionary,
    and record every match as a seed.

    We will store each seed as a **tuple** of two positions:
    `(query_position, subject_position)`, where the "subject" is the database
    sequence.

    For example, with $k = 4$, the example from lecture gives:

        query:   TGCTTACCAGTCAGGT
        subject: GGATCCATGCTTACGAGTCATTGCAACGT

        query k-mer at 0: TGCT -> found at subject position 7  -> seed (0, 7)
        query k-mer at 1: GCTT -> found at subject position 8  -> seed (1, 8)
        ...
        query k-mer at 4: TACC -> not found                    -> no seed
        ...

    A recipe:

    1.  Loop over every starting position in the query sequence where a whole
        $k$-mer fits (the same `range` you used in `get_kmer_dict` from the string
        search exercise)
    2.  Slice out the $k$-mer at that position
    3.  Use `kmer_dict_search` to get the list of subject positions for that
        $k$-mer
    4.  Loop over that list of subject positions, and append the tuple
        `(query_position, subject_position)` to `seeds` for each one

    /// tip
    If a $k$-mer is not in the dictionary, `kmer_dict_search` returns an empty
    list, and a `for` loop over an empty list simply does nothing.
    So you do not need an `if` statement!
    ///
    """)
    return


@app.function
def find_seeds(query, kmer_dict, k):
    """Find every exact k-mer match (seed) between a query and a subject.

    Args:
        query (str): The query sequence.
        kmer_dict (dict[str, list[int]]): A k-mer dictionary of the subject
            (database) sequence, as returned by `get_kmer_dict`.
        k (int): The k-mer length that was used to build `kmer_dict`.

    Returns:
        list[tuple[int, int]]: One `(query_position, subject_position)` tuple
            for every seed, ordered by query position.

    Examples:
        >>> subject_kmers = get_kmer_dict("GGATCCATGCTTACGAGTCATTGCAACGT", 4)
        >>> find_seeds("TGCTTACCAGTCAGGT", subject_kmers, 4)
        [(0, 7), (1, 8), (2, 9), (3, 10), (8, 15), (9, 16)]
    """
    seeds = []
    # Add your code here!
    return seeds


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    seed_test_subject = "GGATCCATGCTTACGAGTCATTGCAACGT"
    seed_test_query = "TGCTTACCAGTCAGGT"
    seed_test_kmers = get_kmer_dict(seed_test_subject, 4)
    seed_test_found = find_seeds(seed_test_query, seed_test_kmers, 4)
    seed_test_expected = [(0, 7), (1, 8), (2, 9), (3, 10), (8, 15), (9, 16)]

    if seed_test_found == seed_test_expected:
        _message = (
            "Yay, your function passed the test!\n"
            "Here are the seeds it found:\n"
            f"{seed_test_found}"
        )
    else:
        _message = f"""Sorry, your find_seeds function should have returned
    {seed_test_expected}
    but it returned
    {seed_test_found}
    Please try again!"""

    print(_message)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice something about those six seeds.
    In every one of them, the subject position minus the query position is **7**.
    They all lie on the same **diagonal** of a dotplot.
    That is because they are all pieces of the same alignment, in which the query
    lines up with the subject starting at subject position 7.

    Now, let's find the seeds between our mystery read and the Wuhan reference
    genome,
    using $k = 11$ (the default word size of NCBI's `blastn` program).
    The cell below plots every seed as a dot, like a dotplot.
    The left panel shows the whole genome, and the right panel zooms in on the
    region with the most seeds (only the range of the X-axis is different!).
    **You do not need to edit this cell.**
    """)
    return


@app.cell
def _(database, mystery_read):
    import matplotlib.pyplot as plt

    word_size = 11
    wuhan_kmers = get_kmer_dict(database["Wuhan"], word_size)
    wuhan_seeds = find_seeds(mystery_read, wuhan_kmers, word_size)

    # Count how many seeds fall on each diagonal (subject_pos - query_pos)
    diagonal_counts = {}
    for _query_pos, _subject_pos in wuhan_seeds:
        _diagonal = _subject_pos - _query_pos
        if _diagonal in diagonal_counts:
            diagonal_counts[_diagonal] += 1
        else:
            diagonal_counts[_diagonal] = 1

    print(f"Number of seeds: {len(wuhan_seeds)}")
    print()
    print("Seeds per diagonal (subject position - query position):")
    for _diagonal in sorted(diagonal_counts):
        print(f"  {_diagonal:>6,}: {diagonal_counts[_diagonal]} seeds")


    # Get a list of only the Wuhan positions (for the X-axis)
    _seed_x = [_s for _q, _s in wuhan_seeds]
    # Get a list of only the query positions (for the Y-axis)
    _seed_y = [_q for _q, _s in wuhan_seeds]

    # Create a figure with 2 side-by-side subplots
    seed_figure, (seed_axes_1, seed_axes_2) = plt.subplots(
        1, 2, figsize = (10, 4)
    )

    # Create scatter plot of Wuhan genome vs query sequence
    seed_axes_1.scatter(_seed_x, _seed_y, s = 12, color = "black")
    seed_axes_1.set_xlim(0, len(database["Wuhan"]))
    seed_axes_1.set_title("Whole Wuhan genome")

    # Create scatter plot zoomed in around the diagonal with the most seeds
    if wuhan_seeds:
        # Get the key in `diagonal_counts` with the largest value (count). A
        # diagonal's key is the Wuhan position that lines up with the start of
        # the read, so the zoomed-in window starts just before it
        _longest_diag = max(diagonal_counts, key = diagonal_counts.get)
        seed_axes_2.scatter(_seed_x, _seed_y, s = 12, color = "black")
        # Zoom in around the longest diagonal of hits
        seed_axes_2.set_xlim(
            _longest_diag - 20,
            _longest_diag + len(mystery_read) + 20,
        )
    seed_axes_2.set_title("Zoomed in")
    for _axes in (seed_axes_1, seed_axes_2):
        _axes.set_xlabel("Position in Wuhan genome")
        _axes.set_ylabel("Position in mystery read")
        _axes.set_ylim(len(mystery_read), 0)
    seed_figure.tight_layout()
    seed_figure
    return (word_size,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 5: Reading the seeds </font>

    Double-click this cell and answer the questions below.

    1.  **Most seeds pile up on just two diagonals that are very close together.
        What do these seeds tell us about where the read came from?**

        **Answer**:

    2.  **In the zoomed-in panel, the diagonal of seeds takes a small step sideways
        partway down.
        What kind of mutation would cause that step, and where have you seen it
        before?**

        **Answer**:

    3.  **We also see a few isolated seeds, far from the others.
        What do you think best explains these isolated $k$-mer matches?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 4: Extending the seeds

    A seed only tells us where to look for homology (an alignment).
    Next, BLAST grows each seed into a longer alignment in two steps.

    ### Step 1: Ungapped extension

    Starting from a seed, keep adding the next pair of nucleotides to the right (and
    then to the left), adding each pair's score to a running total.
    Keep track of the best total score seen so far.
    Matches push the score up; mismatches pull it down.
    Once we walk into sequence that is not homologous, the score starts falling, so
    we **stop once it has dropped more than $X$ below the best total score seen**,
    then trim back to where the total score was best.
    This is called the ***X-drop*** rule.

    Here's the example from lecture, extending the seed `TGCT` to the right with
    $X = 2$:

    | | seed | | | | | | | | | | | | |
    |:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
    | query   | TGCT | T | A | C | C | A | G | T | C | A | G | G | T |
    | subject | TGCT | T | A | C | G | A | G | T | C | A | T | T | G |
    | running score | 4 | 5 | 6 | 7 | 6 | 7 | 8 | 9 | 10 | **11** | 10 | 9 | 8 |

    The first mismatch costs a point (the drop from 7 to 6), but the matches after
    it more than make up for it.
    After the best score of 11, the score drops to 8, which is more than 2 below the
    best, so we stop and keep everything up to the score of 11.
    Each extended seed is called a ***high-scoring segment pair***, or HSP.

    ### Step 2: Gapped extension with Smith-Waterman

    Ungapped extension is fast, but it cannot insert gaps, so an indel breaks it.
    Recall that the deletion split the seeds from Challenge 5 into **two**
    diagonals.
    Ungapped extension will turn them into two separate HSPs, one on either side
    of the deletion.

    The solution is to run an alignment algorithm that **can** add gaps, but only in
    the small neighborhood around the best HSP.
    And we have exactly the right algorithm: **your Smith-Waterman aligner!**
    Instead of aligning the read against all 30,000 bases of a genome, we align it
    against a window of about 190 bases.

    The functions below put all of this together.
    **You do not need to edit these functions**, but please read the comments in
    `simple_blast`, which are labeled with the steps above.
    """)
    return


@app.function
def extend_seed(
    query,
    subject,
    query_position,
    subject_position,
    k,
    x_drop = 10,
    match = 1,
    mismatch = -1,
):
    """Extend a seed in both directions without gaps, using the X-drop rule.

    Args:
        query (str): The query sequence.
        subject (str): The subject (database) sequence.
        query_position (int): Where the seed starts in `query`.
        subject_position (int): Where the seed starts in `subject`.
        k (int): The length of the seed.
        x_drop (int): Stop extending once the running score falls more than
            this far below the best score seen so far.
        match (int): The score for two identical bases.
        mismatch (int): The score for two different bases.

    Returns:
        tuple[int, int, int, int, int]: The high-scoring segment pair (HSP) as
            `(query_start, query_end, subject_start, subject_end, score)`,
            where the ends are exclusive, like the stop index of a slice.

    Examples:
        >>> extend_seed("TGCTTACCAGTCAGGT", "GGATCCATGCTTACGAGTCATTGCAACGT",
        ...             0, 7, 4, x_drop = 2)
        (0, 13, 7, 20, 11)
    """
    # Score the seed itself
    score = 0
    for offset in range(k):
        score += score_pair(
            query[query_position + offset],
            subject[subject_position + offset],
            match,
            mismatch,
        )
    best_score = score

    # Extend to the right
    right_length = 0
    steps = 0
    q = query_position + k
    s = subject_position + k
    while (q < len(query)) and (s < len(subject)):
        score += score_pair(query[q], subject[s], match, mismatch)
        steps += 1
        if score > best_score:
            best_score = score
            right_length = steps
        if best_score - score > x_drop:
            break
        q += 1
        s += 1

    # Extend to the left, starting from the best score on the right
    score = best_score
    left_length = 0
    steps = 0
    q = query_position - 1
    s = subject_position - 1
    while (q >= 0) and (s >= 0):
        score += score_pair(query[q], subject[s], match, mismatch)
        steps += 1
        if score > best_score:
            best_score = score
            left_length = steps
        if best_score - score > x_drop:
            break
        q -= 1
        s -= 1

    return (
        query_position - left_length,
        query_position + k + right_length,
        subject_position - left_length,
        subject_position + k + right_length,
        best_score,
    )


@app.function
def get_hsps(query, subject, kmer_dict, k, x_drop = 10):
    """Find seeds between a query and a subject and extend them into HSPs.

    A seed that falls inside an HSP already found on the same diagonal is
    skipped, because extending it would just find the same HSP again.

    Args:
        query (str): The query sequence.
        subject (str): The subject (database) sequence.
        kmer_dict (dict[str, list[int]]): A k-mer dictionary of `subject`.
        k (int): The k-mer length used to build `kmer_dict`.
        x_drop (int): The X-drop value for ungapped extension.

    Returns:
        tuple[list, int]: The list of HSPs (see `extend_seed`) and the number
            of seeds that were found.
    """
    seeds = find_seeds(query, kmer_dict, k)
    hsps = []
    for query_position, subject_position in seeds:
        # Skip seeds that are already inside an HSP on the same diagonal
        already_covered = False
        for hsp in hsps:
            same_diagonal = (hsp[2] - hsp[0]) == (subject_position - query_position)
            inside = (hsp[0] <= query_position) and (query_position + k <= hsp[1])
            if same_diagonal and inside:
                already_covered = True
                break
        if not already_covered:
            hsp = extend_seed(query, subject, query_position,
                              subject_position, k, x_drop)
            hsps.append(hsp)
    return hsps, len(seeds)


@app.function
def simple_blast(
    query,
    database,
    database_index,
    k,
    min_score = 20,
    x_drop = 10,
    padding = 20,
):
    """Search a database for local alignments to a query using seed-and-extend.

    Args:
        query (str): The query sequence.
        database (dict[str, str]): The database sequences, keyed by name.
        database_index (dict[str, dict]): A k-mer dictionary for each database
            sequence, keyed by the same names as `database`.
        k (int): The k-mer length used to build `database_index`.
        min_score (int): Only report hits with at least this score.
        x_drop (int): The X-drop value for ungapped extension.
        padding (int): Extra bases on either side of the gapped-extension
            window, which allows for indels.

    Returns:
        list[dict]: One hit per database sequence that has an alignment
            scoring at least `min_score`, sorted from best to worst score.
    """
    hits = []
    for name in database:
        subject = database[name]

        # Find seeds and extend them without gaps into HSPs (Step 1)
        hsps, number_of_seeds = get_hsps(
            query, subject, database_index[name], k, x_drop
        )
        if len(hsps) == 0:
            continue
        # Get the HSP with the highest score (the score is at index 4 of each
        # HSP tuple)
        best_hsp = max(hsps, key = lambda hsp: hsp[4])
        if best_hsp[4] < min_score:
            # The highest HSP score is low, so abort and move onto the next
            # subject sequence
            continue

        # Gapped extension (Step 2). Run Smith-Waterman on only the small window
        # of the subject where the whole query would land if the best HSP is
        # part of a real hit
        window_start = max(0, best_hsp[2] - best_hsp[0] - padding)
        window_end = min(
            len(subject),
            best_hsp[3] + (len(query) - best_hsp[1]) + padding,
        )
        window = subject[window_start:window_end]
        aligned_query, aligned_subject, score, query_start, subject_start = (
            align_local(query, window)
        )
        if score < min_score:
            # The gapped alignment score is low, so abort and move onto the
            # next subject sequence
            continue

        # Record the hit, converting window positions to genome positions
        hits.append({
            "subject": name,
            "score": score,
            "query_start": query_start,
            "query_end": query_start + len(aligned_query.replace("-", "")),
            "subject_start": window_start + subject_start,
            "subject_end": window_start + subject_start
                + len(aligned_subject.replace("-", "")),
            "aligned_query": aligned_query,
            "aligned_subject": aligned_subject,
            "number_of_seeds": number_of_seeds,
            "number_of_hsps": len(hsps),
        })
    # Sort the hits from highest to lowest score
    hits.sort(key = lambda hit: hit["score"], reverse = True)
    return hits


@app.function
def hits_to_markdown(hits):
    """Render a list of hits from `simple_blast` as a Markdown table."""
    lines = [
        "| Subject | Score | Query range | Subject range | Seeds | HSPs |",
        "|:--|--:|:-:|:-:|--:|--:|",
    ]
    for hit in hits:
        lines.append(
            f"| {hit['subject']} | {hit['score']} "
            f"| {hit['query_start']}–{hit['query_end']} "
            f"| {hit['subject_start']:,}–{hit['subject_end']:,} "
            f"| {hit['number_of_seeds']} | {hit['number_of_hsps']} |"
        )
    if len(hits) == 0:
        lines.append("| *No hits* | | | | | |")
    return "\n".join(lines)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, let's search the database with our mystery read.
    The cell below first builds the $k$-mer dictionaries for the whole database
    (this only has to be done once, no matter how many query sequences we search
    for), then runs the search.
    Both steps are timed.
    **You do not need to edit the next cell**.
    """)
    return


@app.cell
def _(database, mo, mystery_read, time, word_size):
    _start_time = time.perf_counter()
    database_index = {}
    for _name in database:
        database_index[_name] = get_kmer_dict(database[_name], word_size)
    index_seconds = time.perf_counter() - _start_time

    _start_time = time.perf_counter()
    blast_hits = simple_blast(mystery_read, database, database_index, word_size)
    blast_seconds = time.perf_counter() - _start_time

    mo.md(
        hits_to_markdown(blast_hits)
        + f"\n\nBuilding the index (once): **{index_seconds:.3f} seconds**  \n"
        + f"Searching with seed-and-extend: **{blast_seconds:.3f} seconds**"
    )
    return blast_hits, database_index


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below prints the alignment of each hit.
    The query (mystery read) is on top and the database genome is on the bottom.
    """)
    return


@app.cell
def _(blast_hits):
    for _hit in blast_hits:
        print(f"=== Mystery read vs {_hit['subject']} ===")
        print_alignment(_hit["aligned_query"], _hit["aligned_subject"], _hit["score"])
        print()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 6: Identifying the mystery read </font>

    Double-click this cell and answer the questions below.

    1.  **Which variant did the mystery read most likely come from? How do you
        know?**

        **Answer**:

    2.  **Look at the "Best local score" column from your Smith-Waterman search in
        Part 2.
        Did the seed-and-extend (BLAST) search find the same scores?
        Given that seed-and-extend is a heuristic, is this guaranteed?**

        **Answer**:

    3.  **Alpha is the second-best hit.
        Look at the Alpha alignment and compare it to the Wuhan alignment.
        What does Alpha share with the mystery read that Wuhan, Delta, and Gamma do
        not?**

        **Answer**:

    4.  **Compare the time of the seed-and-extend search to the total time of the
        Smith-Waterman search in Part 2.
        Roughly how many times faster was it?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 5: The price of speed

    Seed-and-extend is fast because it ignores every part of the database that does
    not share an exact $k$-mer with the query.
    But what if a homologous sequence does not share any exact $k$-mers with our
    query?
    Then BLAST will **never** find it, no matter how good the alignment would be.

    Let's test this.
    To simulate a homologous gene from a more distantly related virus,
    we will take a 300-base stretch of the Wuhan spike gene and randomly mutate a
    percentage of its bases.
    Then, we will search the Wuhan genome with it and see whether we find the right
    location.

    The first cell below defines a `mutate_sequence` function that randomly changes
    a certain fraction of bases in a sequence.
    The second cell performs the simulation experiment.
    Specifically, it:

    1.  Slices out a 300-nucleotide section of the spike gene from the
        genome of the Wuhan virus
    2.  Uses the `mutate_sequence` function to mutate a fraction of the nucleotides
        of the spike gene section
    3.  Builds a $k$-mer dictionary of the Wuhan genome
    4.  Uses the `get_hsps` function to do a "seed-and-extend" search of the Wuhan
        genome for a region homologous to the mutated spike gene (and times it!)
    5.  Summarizes the results

    The third cell gives you controls for changing the percentage of mutated bases
    (*i.e.*, the divergence of the simulated spike gene of a related virus) and the
    word size ($k$).
    The results will update automatically when you tinker with the controls.

    **You do not need to edit the next three cells**.
    """)
    return


@app.function
def mutate_sequence(sequence, divergence, random_seed = None):
    """Randomly substitute a fraction of the bases in a sequence.

    If the same `random_seed` is used, the same random numbers are drawn at
    every divergence, so the bases mutated at a lower divergence are also
    mutated (to the same base) at every higher divergence.

    Args:
        sequence (str): The sequence to mutate.
        divergence (float): The probability that each base is substituted.
        random_seed (int): Seed for the random number generator, so results
            are repeatable. If None (the default), a random seed is used.

    Returns:
        str: The mutated sequence, the same length as `sequence`.
    """
    import random

    if random_seed is None:
        random_seed = random.random()
    rng = random.Random(random_seed)
    mutated = ""
    for base in sequence:
        draw = rng.random()
        # Randomly choose one of the 3 other nucleotides
        replacement = rng.choice([b for b in "ACGT" if b != base])
        if draw < divergence:
            mutated += replacement
        else:
            mutated += base
    return mutated


@app.cell
def _(database, divergence_slider, mo, time, word_size_dropdown):
    experiment_k = int(word_size_dropdown.value)
    experiment_divergence = divergence_slider.value / 100

    # The 300-base stretch of the spike gene, and where it truly is
    true_start = 22885
    original_gene = database["Wuhan"][true_start:true_start + 300]
    divergent_gene = mutate_sequence(original_gene, experiment_divergence, 15)

    experiment_kmers = get_kmer_dict(database["Wuhan"], experiment_k)

    _start_time = time.perf_counter()
    experiment_hsps, experiment_seed_count = get_hsps(
        divergent_gene, database["Wuhan"], experiment_kmers, experiment_k
    )
    experiment_seconds = time.perf_counter() - _start_time

    # Seeds on the correct diagonal, and the best HSP at the correct location
    _true_seeds = 0
    for _query_pos, _subject_pos in find_seeds(
        divergent_gene, experiment_kmers, experiment_k
    ):
        if _subject_pos - _query_pos == true_start:
            _true_seeds += 1
    _true_score = 0
    for _hsp in experiment_hsps:
        if (_hsp[2] - _hsp[0] == true_start) and (_hsp[4] > _true_score):
            _true_score = _hsp[4]

    if _true_score >= 20:
        _verdict = f"**Found it!** Best HSP at the true location scores {_true_score}."
    else:
        _verdict = "**Missed it!** No HSP at the true location scores at least 20."

    mo.md(
        f"""
    | | |
    |:--|--:|
    | Word size ($k$) | {experiment_k} |
    | Divergence | {divergence_slider.value}% |
    | Total seeds | {experiment_seed_count:,} |
    | Seeds at the true location | {_true_seeds:,} |
    | Seeds anywhere else (chance) | {experiment_seed_count - _true_seeds:,} |
    | Time to find and extend seeds | {experiment_seconds * 1000:.2f} ms |

    {_verdict}
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    _header = mo.md("""***Tinker with the variables below and watch how the results above change!***""")
    divergence_slider = mo.ui.slider(
        start = 0,
        stop = 60,
        step = 5,
        value = 0,
        label = "Divergence (% of bases mutated)",
        show_value = True,
    )
    word_size_dropdown = mo.ui.dropdown(
        options = ["7", "11", "15", "20", "28"],
        value = "11",
        label = "Word size (k)",
    )
    mo.vstack([_header, divergence_slider, word_size_dropdown])
    return divergence_slider, word_size_dropdown


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 7: Speed versus sensitivity </font>

    Use the controls above to answer the questions below.
    Double-click this cell to write your answers.

    1.  **With the word size ($k$) at 11, increase the divergence one step at a
        time.
        What is the highest divergence at which the search still finds the gene?
        Do the same for word sizes 28 and 7.
        What trend do you notice across these values of $k$ and why?**

        **Answer**:

    2.  **When the gene is found, and holding the divergence constant, does the
        score of the best HSP depend on the word size ($k$)?
        What does the word size control, then?**

        **Answer**:

    3.  **Set the divergence to 0%. Compare the number of chance seeds and the run
        time for word sizes 7 and 11.
        Why don't BLAST programs just always use a small word size (*i.e.*, small
        $k$)?**

        **Answer**:

    4.  **NCBI's default nucleotide search, `megablast`, uses a word size of 28.
        Given this value of $k$, what kind of search do you think it is designed
        for?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Stretch goal </font>

    If you finish early, try this.

    DNA is double-stranded, and a sequencer reads whichever strand it happens to
    grab.
    So a sequence read returned by the sequencer might be the ***reverse
    complement*** of the genome sequence: The opposite strand, read in the opposite
    direction.
    (`A` pairs with `T`, and `C` pairs with `G`.)

    1.  In the cell below, write a function called `reverse_complement` that returns
        the reverse complement of a sequence. For example,
        `reverse_complement("AACG")` should return `"CGTT"`.

        /// tip
        A dictionary such as `{"A": "T", "T": "A", "C": "G", "G": "C"}` is handy for
        the complement, and the slice `sequence[::-1]` reverses an entire string.
        ///

    2.  Run `simple_blast` with the reverse complement of `mystery_read` as the query.
        What happens?

        **Answer**:

    3.  How could you change the search so that it finds reads from either strand?

        **Answer**:
    """)
    return


@app.cell
def _(database, database_index, mo, mystery_read, word_size):
    # Write your stretch goal code here
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    You built a (simple) version of one of the most widely used tools in all of
    biology, BLAST.
    Along the way we learned some important concepts:

    -   **Smith-Waterman**: Three small changes turn a global aligner into a local
        one, which finds the best alignment between *parts* of two sequences
    -   **Optimal is too slow**: Aligning against every base of a database has
        complexity of $O(mn)$, and for GenBank, $n$ is tens of trillions of bases!
    -   **Seeds**: Short exact matches can be looked up almost instantly with a
        $k$-mer dictionary that is built once
    -   **Extend**: Ungapped extension with the X-drop rule, then use the
        Smith-Waterman algorithm on only a small window to allow for indels
    -   **The trade-off**: Word size ($k$) controls how sensitive and how fast the
        search is. You cannot maximize both!

    BLAST gives up the guarantee of finding the best alignment in exchange for an
    answer in seconds rather than decades.
    That is the heuristic strategy we covered in our algorithms lecture, and it is
    why BLAST can miss things.
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

    I used Anthropic's Claude (Opus 5 model) to draft this notebook.
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
