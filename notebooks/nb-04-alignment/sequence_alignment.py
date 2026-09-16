# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.0",
#     "matplotlib",
# ]
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Aligning sequences

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sequence alignment

    Last time, we searched a long sequence for **exact** matches to a shorter
    subsequence.
    Every method we built depended on an exact, character-for-character match.

    Evolution does not cooperate with that assumption.
    Two copies of the same gene in two individuals or species have accumulated
    substitutions, insertions, and deletions since they diverged.
    To compare them, we first have to decide **which position in one sequence
    corresponds to which position in the other**.
    We call this an ***alignment***, which is a hypothesis about which nucleotide
    residues descend from the same nucleotide residue in a shared ancestor.
    This is a hypothesis of **homology**.

    In this exercise, you will build a working global aligner from scratch, in four
    pieces:

    1.  A function that **scores** an alignment between two sequences
    2.  Functions that build and display a ***dotplot***, so we can visualize
        homology between two sequences
    3.  A function that fills the **Needleman-Wunsch scoring matrix**
    4.  A function that **traces back** through that matrix to produce the alignment
        between the two sequences

    Our goal is that,
    by the end, you will be able to use your own code and get an optimal global
    alignment between two sequences of DNA.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: Scoring an alignment

    Before we can look for the *best* alignment, we need to be able to say what
    "best" means.
    We do that with a ***scoring scheme***: A rule that assigns a number to every
    column (nucleotide position) of an alignment.
    The score of the whole alignment is the sum of its column scores.

    We will use the simple scoring scheme from lecture:

    | Column | Score |
    |:--|--:|
    | Match | $+1$ |
    | Mismatch | $-1$ |
    | Gap | $-2$ |

    The function below scores a single column of an alignment.
    Notice that the scoring scheme is entirely determined by this one small
    function.
    The rest of our code today is agnostic about what a nucleotide is; that is
    all handled by `score_pair`.
    This is a design choice that will make it possible to easily align protein
    sequences with the same code later on.
    We would just need to swap `score_pair` for a function that encodes an amino
    acid scoring scheme, and the rest of our code would remain the same.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's try it out. Run the cell below.

    **Note**: The `match`, `mismatch`, and `gap` arguments have **default values**,
    so we can leave them out and get the scheme from lecture.
    If we want a different scheme, we can pass our own values.
    We will do exactly that at the end of the notebook.
    """)
    return


@app.cell
def _():
    print("A vs A:", score_pair("A", "A"))
    print("A vs G:", score_pair("A", "G"))
    print("A vs -:", score_pair("A", "-"))
    print()
    # The same column, scored under a harsher gap penalty
    print("A vs - (gap = -5):", score_pair("A", "-", gap = -5))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 1: Scoring an alignment </font>

    An **aligned** pair of sequences is just two strings of the *same length*, where
    gap characters (`-`) have been inserted so that the columns line up.
    For example:

        A C G T C A
        A C - T G A

    Below, I have started a function called `score_alignment` that should add up the
    score of every column.

    Replace the `# Add your code here!` comment with a `for` loop that visits every
    column and adds that column's score to `total_score`.
    **Use the `score_pair` function above** to score each column; do not rewrite the
    match/mismatch/gap logic.

    /// tip
    Both sequences have the same length, so a loop over
    `range(len(aligned_seq_1))` gives you an index you can use in **both**
    strings.
    ///

    /// note
    Because the list of arguments for the `score_alignment` function is quite long,
    I have put each one on its own line to make the function definition easier to
    read.
    This is just a formatting choice and does not affect how Python interprets the
    function.
    ///
    """)
    return


@app.function
def score_alignment(
    aligned_seq_1,
    aligned_seq_2,
    match = 1,
    mismatch = -1,
    gap = -2,
):
    """Score a pairwise alignment by summing the scores of its columns.

    Args:
        aligned_seq_1 (str): The first aligned sequence, possibly containing
            gap characters ("-").
        aligned_seq_2 (str): The second aligned sequence, the same length as
            `aligned_seq_1`.
        match (int): The score for two identical bases.
        mismatch (int): The score for two different bases.
        gap (int): The score for a column containing a gap.

    Returns:
        int: The sum of the scores of every column of the alignment.

    Raises:
        AssertionError: If the two aligned sequences are not the same length.

    Examples:
        >>> score_alignment("ACGTCA", "AC-TGA")
        1
        >>> score_alignment("ACGTCA", "ACTGA-")
        -3
    """
    # Aligned sequences must be the same length, or they are not aligned!
    assert len(aligned_seq_1) == len(aligned_seq_2)
    total_score = 0
    # Add your code here!
    return total_score


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function above. **Note**: You do not need to edit the
    code in the cell below.

    Once your function above is working correctly, the output of the test code below
    should be "Yay, your function passed the test!"
    """)
    return


@app.cell
def _():
    test_alignment_1 = ("ACGTCA", "AC-TGA")
    test_alignment_2 = ("ACGTCA", "ACTGA-")
    test_score_1 = score_alignment(test_alignment_1[0], test_alignment_1[1])
    test_score_2 = score_alignment(test_alignment_2[0], test_alignment_2[1])

    if (test_score_1 == 1) and (test_score_2 == -3):
        _message = "Yay, your function passed the test!"
    else:
        _message = f"""Sorry, your score_alignment function should have returned
    1 and -3, but it returned {test_score_1} and {test_score_2}. Please try again!"""

    print("Alignment 1:")
    print(test_alignment_1[0])
    print(test_alignment_1[1])
    print("Score:", test_score_1)
    print()
    print("Alignment 2:")
    print(test_alignment_2[0])
    print(test_alignment_2[1])
    print("Score:", test_score_2)
    print()
    print(_message)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note: The two alignments in the output above are two different hypotheses about
    the evolutionary history of the same two sequences,
    and our scoring scheme prefers the first one.

    ## <font color=red> Challenge 2: The scoring scheme is a model </font>

    Double-click this cell and write your answer to the question below.

    **Our scheme charges $-2$ for a gap but only $-1$ for a mismatch. What
    biological claim are we making when we make gaps more expensive than
    mismatches?**

    **Answer**: 
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 2: Seeing homology with a dotplot

    Before running an alignment algorithm on two sequences, it is worth **looking**
    at them in a way that aids your ability to "see" their homology (shared
    evolutionary history).

    A ***dotplot*** is the simplest way to do that.
    To create a dotplot,
    we write one sequence down the rows and the other across the columns, and put a
    dot in every cell where the two bases are the same between the sequences.
    For example, the sequences `ACGTCA` and `ACTGA` would have the following
    dotplot:

    |   | A | C | T | G | A |
    |:--|:-:|:-:|:-:|:-:|:-:|
    | **A** | ● |   |   |   | ● |
    | **C** |   | ● |   |   |   |
    | **G** |   |   |   | ● |   |
    | **T** |   |   | ● |   |   |
    | **C** |   | ● |   |   |   |
    | **A** | ● |   |   |   | ● |

    Isolated dots are noise; with only four bases, one in four cells matches by
    chance.
    What matters is **diagonal runs** of dots, because a diagonal run represents a
    stretch of consecutive positions that match between the two sequences.

    A dotplot will not give you an alignment, but it will tell you, at a glance,
    whether homology runs the whole length of both sequences (one long diagonal from
    corner to corner) or is confined to a region (a short diagonal somewhere else).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 3: Building a dotplot </font>

    We will represent a dotplot as a ***list of lists***: the outer list holds the
    rows, and each inner list holds the cells of that row.
    A cell is `1` if the two bases match and `0` if they do not.

    For example, `get_dotplot("ACG", "AG")` should return:

        [[1, 0],
         [0, 0],
         [0, 1]]

    To make this clearer, I will annotate the list of lists with the sequences
    (these annotations would not be part of what the function returns):

            A  G
        A [[1, 0],
        C  [0, 0],
        G  [0, 1]]

    Replace the `# Add your code here!` comment below with a **nested loop**:
    An outer `for` loop over the bases of `seq_1` (the rows), and an inner `for`
    loop over the bases of `seq_2` (the columns).

    A recipe:

    1.  For each base in `seq_1`, create an empty list called `row`
    2.  For each base in `seq_2`, append `1` to `row` if the two bases match and `0`
        if they do not
    3.  After the inner loop finishes, append `row` to `dotplot`

    /// tip
    1.  Watch your indentation. Step 3 happens once per *row*, so it belongs in the
        outer loop, not the inner one.
    2.  You do not need to use `range()` in either `for` loop; just loop over the
        letters themselves.
    ///
    """)
    return


@app.function
def get_dotplot(seq_1, seq_2):
    """Build a dotplot matrix comparing every base of two sequences.

    Args:
        seq_1 (str): The sequence to place along the rows.
        seq_2 (str): The sequence to place along the columns.

    Returns:
        list[list[int]]: A list with one inner list per base of `seq_1`. Each
            inner list has one entry per base of `seq_2`, which is 1 where the
            two bases match and 0 where they do not.

    Examples:
        >>> get_dotplot("ACG", "AG")
        [[1, 0], [0, 0], [0, 1]]
    """
    # Create an empty list to hold the rows (lists) of the dotplot
    dotplot = []
    # Add your code here!
    return dotplot


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The function below turns a dotplot into a Markdown table so we can actually look
    at it. **You do not need to edit or understand this function**, but read it if
    you are curious; it is just string building.
    """)
    return


@app.function
def dotplot_to_markdown(dotplot, seq_1, seq_2, dot = "●"):
    """Render a dotplot as a Markdown table.

    Args:
        dotplot (list[list[int]]): A dotplot, as returned by `get_dotplot`.
        seq_1 (str): The sequence along the rows.
        seq_2 (str): The sequence along the columns.
        dot (str): The character to show in cells where the bases match.

    Returns:
        str: Markdown-formatted text that renders as a table.
    """
    # The header row is the bases of seq_2
    header = "|   | " + " | ".join(seq_2) + " |"
    # Markdown needs a row of dashes under the header
    rule = "|:--|" + ":-:|" * len(seq_2)
    lines = [header, rule]
    for row_index in range(len(dotplot)):
        cells = []
        for cell in dotplot[row_index]:
            if cell == 1:
                cells.append(dot)
            else:
                cells.append(" ")
        lines.append(f"| **{seq_1[row_index]}** | " + " | ".join(cells) + " |")
    return "\n".join(lines)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your `get_dotplot` function and then draws the dotplot of
    the two sequences.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(mo):
    small_test_dotplot = get_dotplot("ACG", "AG")
    expected_dotplot = [[1, 0], [0, 0], [0, 1]]

    if small_test_dotplot == expected_dotplot:
        _message = "Yay, your function passed the test!"
    else:
        _message = f"""Sorry, your get_dotplot function should have returned
    {expected_dotplot}
    but it returned
    {small_test_dotplot}
    Please try again!"""

    print(_message)

    global_seq_1 = "ACTGCATA"
    global_seq_2 = "ACTGATA"
    global_dotplot = get_dotplot(global_seq_1, global_seq_2)

    mo.md(dotplot_to_markdown(global_dotplot, global_seq_1, global_seq_2))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In your dotplot above, look for the diagonal runs.
    There is one in the top-left corner (the `ACTG` shared by both sequences) and
    another running down to the bottom-right corner (the `ATA` shared by both
    sequences).
    Between them, the diagonal **shifts down by one row**.
    That shift could be due to an insertion of a "C" in the longer sequence, or
    the deletion of a "C" from the shorter sequence.
    The dotplot is NOT an alignment, but it allows you to visualize shared
    nucleotides between the sequences and start hypothesizing about their
    evolutionary history (a hypothesis about their evolutionary history IS an
    alignment).

    ## Two sequences that share only a region

    Now, let's look at the pair of sequences from the end of lecture, where the two
    sequences share a six-base stretch, but at opposite ends.
    """)
    return


@app.cell
def _(mo):
    local_seq_1 = "TTTTACGTCA"
    local_seq_2 = "ACGTCAGGGG"
    local_dotplot = get_dotplot(local_seq_1, local_seq_2)

    mo.md(dotplot_to_markdown(local_dotplot, local_seq_1, local_seq_2))
    return local_seq_1, local_seq_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 4: Reading a dotplot </font>

    Double-click this cell and write your answers to the questions below.

    1.  **There is one obvious diagonal run of six dots. Where does it start and
        end, and what does it mean biologically?**

        **Answer**:

    2.  **A global alignment tries to run a single path from the top-left corner to
        the bottom-right corner. Looking at this dotplot, why is that going to be a
        problem here?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 3: The Needleman-Wunsch scoring matrix

    A dotplot shows you where the matches are, but it will not choose among the
    enormous number of possible alignments.
    For that we can use the Needleman-Wunsch algorithm from lecture.

    Recall the recurrence from lecture.
    $F(i,j)$ is the score of the best alignment of the first
    $i$ bases of `seq_1` with the first $j$ bases of `seq_2`:

    $$
    F(i,j) = \max
    \begin{cases}
    F(i-1,\,j-1) + s(A_i, B_j) & \text{(match/mismatch)}\\
    F(i-1,\,j) + g & \text{(gap in } B)\\
    F(i,\,j-1) + g & \text{(gap in } A)
    \end{cases}
    $$

    where $A$ is `seq_1` (rows),
    $B$ is `seq_2` (columns),
    $s$ is the `score_pair` function,
    $g$ is the gap penalty,
    and `i` and `j` represent the index of the row and column in the scoring matrix,
    respectively.

    Like the dotplot, the scoring matrix is a list of lists.
    However, the scoring matrix has **one extra row and one extra column**, because
    row 0 and column 0
    represent aligning a sequence against nothing but gaps at the beginning of the
    other sequence.

    /// note
    Be careful with indices.
    Because of that extra row and column, the base compared in cell `matrix[i][j]`
    is `seq_1[i - 1]` and `seq_2[j - 1]`, not `seq_1[i]` and `seq_2[j]`.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The function below builds the matrix and fills in row 0 and column 0, which is
    the base case of the recurrence.
    **You do not need to edit this function.**
    Aligning $i$ bases against nothing but gaps in the other sequence requires $i$
    gaps, so cell `[i][0]` is just `i * gap`.
    """)
    return


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The function below creates a table of a scoring matrix in Markdown syntax so we
    can easily visualize the scoring matrices we create using the Needleman-Wunsch
    algorithm.
    **Note: You do not need to edit this function.**
    """)
    return


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Run the cell below to see the initialized matrix for the two sequences we
    aligned "by hand" in lecture.
    Every cell that still holds a 0 is one we have not computed yet.
    """)
    return


@app.cell
def _(mo):
    lecture_seq_1 = "ACGTCA"
    lecture_seq_2 = "ACTGA"
    initial_matrix = get_initial_matrix(lecture_seq_1, lecture_seq_2)

    mo.md(matrix_to_markdown(initial_matrix, lecture_seq_1, lecture_seq_2))
    return lecture_seq_1, lecture_seq_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 5: Filling the scoring matrix </font>

    This is the heart of the Needleman-Wunsch algorithm,
    and it is a **nested loop**,
    just like the one you wrote for the dotplot.
    The difference is what happens inside the `for` loops.
    Instead of comparing two bases,
    you compute three candidate scores and keep the largest.

    Replace the `# Add your code here!` comment below with a nested loop that visits
    every cell that is not in row 0 or column 0.
    For each cell, compute three scores:

    -   `diagonal`: `matrix[i - 1][j - 1]` plus the score of pairing `seq_1[i - 1]`
        with `seq_2[j - 1]` (use the `score_pair` function for this latter part!)
        -   This is the score for aligning the next nucleotides from both
            sequences
    -   `up`: the score in `matrix[i - 1][j]` plus the `gap` score
        -   This is the score of adding a gap to the sequence along the columns
    -   `left`: the score in `matrix[i][j - 1]` plus the `gap` score
        -   This is the score of adding a gap to the sequence along the rows

    then set `matrix[i][j]` to the largest of the three.
    **To reiterate**: We are using `i` to represent the row index and `j` to
    represent the column index in the scoring matrix (called `matrix` in the
    function below).

    /// tip
    Python's built-in `max()` function takes any number of arguments and returns
    the largest, so `max(diagonal, up, left)` does the last step for you.
    ///

    /// warning
    Your `for` loops need to start at 1, not 0, because row 0 and column 0 are already
    filled in. `range(1, number_of_rows)` gives you 1, 2, 3, ... up to
    `number_of_rows - 1`.
    ///

    /// warning
    Reiterating from above,
    be careful with indices.
    Because of the extra "all gaps" row and column, the base compared in cell
    `matrix[i][j]` is `seq_1[i - 1]` and `seq_2[j - 1]`, not `seq_1[i]` and
    `seq_2[j]`.
    *I.e.*, you will want to provide `seq_1[i - 1]` and `seq_2[j - 1]` to the
    `score_pair` function inside the `for` loops.
    ///
    """)
    return


@app.function
def fill_scoring_matrix(seq_1, seq_2, match = 1, mismatch = -1, gap = -2):
    """Fill a Needleman-Wunsch scoring matrix for two sequences.

    Every cell holds the score of the best global alignment of the prefix of
    `seq_1` ending at that row with the prefix of `seq_2` ending at that column.
    The bottom-right cell therefore holds the score of the best global alignment
    of the two complete sequences.

    Args:
        seq_1 (str): The sequence along the rows.
        seq_2 (str): The sequence along the columns.
        match (int): The score for two identical bases.
        mismatch (int): The score for two different bases.
        gap (int): The score for a column containing a gap.

    Returns:
        list[list[int]]: The completed scoring matrix.

    Examples:
        >>> fill_scoring_matrix("AC", "A")
        [[0, -2], [-2, 1], [-4, -1]]
    """
    matrix = get_initial_matrix(seq_1, seq_2, gap)
    # Adding 1 to the number or rows/columns for the first "all gaps" row/column
    number_of_rows = len(seq_1) + 1
    number_of_columns = len(seq_2) + 1
    # Add your code here!
    return matrix


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function against the matrix we filled in by hand
    during lecture. **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(lecture_seq_1, lecture_seq_2, mo):
    filled_matrix = fill_scoring_matrix(lecture_seq_1, lecture_seq_2)
    expected_matrix = [
        [0, -2, -4, -6, -8, -10],
        [-2, 1, -1, -3, -5, -7],
        [-4, -1, 2, 0, -2, -4],
        [-6, -3, 0, 1, 1, -1],
        [-8, -5, -2, 1, 0, 0],
        [-10, -7, -4, -1, 0, -1],
        [-12, -9, -6, -3, -2, 1],
    ]

    if filled_matrix == expected_matrix:
        _message = "Yay, your function passed the test!"
    else:
        _message = """Sorry, your fill_scoring_matrix function did not produce the
    matrix from lecture. Compare your table below to the one on the slides and find
    the first cell that disagrees. Please try again!"""

    print(_message)

    mo.md(matrix_to_markdown(filled_matrix, lecture_seq_1, lecture_seq_2))
    return (filled_matrix,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The bottom-right cell is the score of the best possible global alignment of these
    two sequences: **1**.

    Notice what we have *not* done yet. We know the best score, but we do not know
    the alignment that achieves it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 4: Traceback

    To recover the alignment, we start in the bottom-right cell and walk backward,
    asking at each step: **which of the three options did this cell's score come
    from?**

    - A **diagonal** step means the two bases were aligned to each other
    - An **up** step means a base of `seq_1` was aligned to a gap in `seq_2`
    - A **left** step means a base of `seq_2` was aligned to a gap in `seq_1`

    We rebuild the alignment from right to left, sticking each new character onto the
    **front** of the strings we are building.

    ## <font color=red> Challenge 6: Tracing back </font>

    I have written the diagonal branch of the function below for you as a model.
    Your job is to fill in the two gap branches.
    Each one needs exactly two lines: one that adds a character to the **front** of
    `aligned_1`, and one that adds a character to the **front** of `aligned_2`.
    In each branch, one of those characters is a base and the other is a gap ("`-`").

    The lines that move `i` (row) and `j` (column) are already written for you, and they tell you
    which branch you are in:

    -   The branch that does `i = i - 1` moves **up** a row, so it consumes a base
        from `seq_1`
    -   The branch that does `j = j - 1` moves **left** a column, so it consumes a
        base from `seq_2`

    /// tip
    To stick a character onto the front of a string, use `+` with the new
    character first.
    For example: `aligned_1 = seq_1[i - 1] + aligned_1`.
    ///
    """)
    return


@app.function
def traceback_alignment(
    matrix,
    seq_1,
    seq_2,
    match = 1,
    mismatch = -1,
    gap = -2,
):
    """Recover the optimal global alignment from a filled scoring matrix.

    Starts in the bottom-right cell and walks backward to the top-left corner,
    at each step determining which of the three options produced that cell's
    score, and building the two aligned sequences from right to left.

    Args:
        matrix (list[list[int]]): A completed scoring matrix, as returned by
            `fill_scoring_matrix`.
        seq_1 (str): The sequence along the rows.
        seq_2 (str): The sequence along the columns.
        match (int): The score for two identical bases.
        mismatch (int): The score for two different bases.
        gap (int): The score for a column containing a gap.

    Returns:
        tuple[str, str]: The two aligned sequences, of equal length, with gap
            characters ("-") inserted.

    Examples:
        >>> traceback_alignment(fill_scoring_matrix("ACGTCA", "ACTGA"),
        ...                     "ACGTCA", "ACTGA")
        ('ACGTCA', 'AC-TGA')
    """
    # Create empty strings to hold the aligned sequences
    aligned_1 = ""
    aligned_2 = ""
    # Start in the bottom-right corner of the matrix
    i = len(seq_1)
    j = len(seq_2)
    # Keep looping until we reach the top-left corner (i == 0 and j == 0)
    while (i > 0) or (j > 0):
        # Could this cell have come from the diagonal?
        pair_score = 0
        if (i > 0) and (j > 0):
            pair_score = score_pair(
                seq_1[i - 1], seq_2[j - 1], match, mismatch, gap
            )
        if (i > 0) and (j > 0) and (matrix[i][j] == matrix[i - 1][j - 1] + pair_score):
            # Diagonal step: the two bases are aligned to each other.
            # This branch is written for you as a model for the other two.
            aligned_1 = seq_1[i - 1] + aligned_1
            aligned_2 = seq_2[j - 1] + aligned_2
            i = i - 1
            j = j - 1
        elif (i > 0) and (matrix[i][j] == matrix[i - 1][j] + gap):
            # Up step: a base of seq_1 is aligned to a gap in seq_2
            # Add your code here!
            i = i - 1
        else:
            # Left step: a base of seq_2 is aligned to a gap in seq_1
            # Add your code here!
            j = j - 1
    return aligned_1, aligned_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function. **Note**: You do not need to edit the code in
    the cell below.

    Notice the second test: we score the alignment your traceback produced with the
    `score_alignment` function you wrote in Challenge 1, and check that it agrees
    with the number in the bottom-right corner of the matrix.
    Those two numbers are computed in completely different ways, so agreement is good
    evidence that both functions are right.
    """)
    return


@app.cell
def _(filled_matrix, lecture_seq_1, lecture_seq_2):
    test_aligned_1, test_aligned_2 = traceback_alignment(
        filled_matrix, lecture_seq_1, lecture_seq_2
    )
    corner_score = filled_matrix[-1][-1]
    align_score = score_alignment(test_aligned_1, test_aligned_2)

    print(test_aligned_1)
    print(test_aligned_2)
    print()
    print("Score from the matrix:   ", corner_score)
    print("Score of this alignment: ", align_score)
    print()

    if (test_aligned_1, test_aligned_2) != ("ACGTCA", "AC-TGA"):
        print("""Sorry, your traceback_alignment function should have returned
    ACGTCA and AC-TGA. Please try again!""")
    elif corner_score != align_score:
        print("""Your alignment does not score the same as the matrix says it
    should. Either your score_alignment function or Needleman-Wunsch functions are
    not working. Please try again!""")
    else:
        print("Yay, your function passed the test!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Putting it together into one function

    You have created a working global sequence aligner.
    The function below just bundles your two functions into one function for
    convenience.
    **You do not need to edit it.**
    """)
    return


@app.function
def align_sequences(seq_1, seq_2, match = 1, mismatch = -1, gap = -2):
    """Compute the optimal global alignment of two sequences.

    Args:
        seq_1 (str): The first sequence.
        seq_2 (str): The second sequence.
        match (int): The score for two identical bases.
        mismatch (int): The score for two different bases.
        gap (int): The score for a column containing a gap.

    Returns:
        tuple[str, str, int]: The two aligned sequences and the score of the
            alignment.

    Examples:
        >>> align_sequences("ACGTCA", "ACTGA")
        ('ACGTCA', 'AC-TGA', 1)
    """
    matrix = fill_scoring_matrix(seq_1, seq_2, match, mismatch, gap)
    aligned_1, aligned_2 = traceback_alignment(
        matrix, seq_1, seq_2, match, mismatch, gap
    )
    return aligned_1, aligned_2, matrix[-1][-1]


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The function below prints an alignment with a middle line marking the matching
    columns, the way most alignment tools display their output.
    **You do not need to edit it** and you will use it in the next challenge.
    """)
    return


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 7: When global alignment fails </font>

    Run the cell below, which aligns the two sequences whose dotplot you interpreted
    in Challenge 4, then answer the questions underneath.
    """)
    return


@app.cell
def _(local_seq_1, local_seq_2):
    local_aligned_1, local_aligned_2, local_score = align_sequences(
        local_seq_1, local_seq_2
    )
    print_alignment(local_aligned_1, local_aligned_2, local_score)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Double-click this cell and write your answers to the questions below.

    1.  **The two sequences share the six-base stretch `ACGTCA`. Did the alignment
        line those two copies up with each other?**

        **Answer**:

    2.  **Lining the two copies up would require four gaps in each sequence. Work
        out what that alignment would score under our scheme. Is it better or worse
        than what the algorithm returned?**

        **Answer**:

    3.  **So did the algorithm fail? Explain what actually went wrong.**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 5: A real deletion

    Above, we used "toy" sequences so we could easily visualize the process and
    apply the algorithm "by hand".
    Next, let's work with some real sequences.

    The SARS-CoV-2 Alpha variant carries a well-known six-nucleotide deletion in the
    spike gene, which removes two amino acids (histidine 69 and valine 70).
    Below we load the genomes of several SARS-CoV-2 variants and pull out the region
    of the spike gene containing that deletion from the original Wuhan reference
    sequence and from the Alpha variant.

    The `parse_fasta_file` function is the one we wrote in our first notebook.
    """)
    return


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
    Notice how we find the matching region in the Alpha genome below.
    We take the first and last 15 bases of the Wuhan fragment and use Python's
    built-in `.find()` string method to locate them in the Alpha genome.
    That is a linear search, exactly like the `linear_search` function you wrote last
    time; the two genomes do not line up by position, so we have to search.
    """)
    return


@app.cell
def _(local_files):
    local_files  # Ignore this line; it just ensures the FASTA file is present
    covid_sequences = parse_fasta_file("SARS-CoV-2-unaligned.fasta")
    for covid_name in covid_sequences:
        print(f"{covid_name}: {len(covid_sequences[covid_name])} bases")

    wuhan_genome = covid_sequences["Wuhan-gi-1798174254-ref-NC_045512.2"]
    alpha_genome = covid_sequences["Alpha-gi-2055420694-emb-OU207378.1"]

    # A 60-base window of the spike gene from the reference genome
    wuhan_fragment = wuhan_genome[21740:21800]

    # Find the same region in the Alpha genome by searching for the sequences
    # flanking our window
    start_anchor = wuhan_fragment[:15]
    end_anchor = wuhan_fragment[-15:]
    alpha_start = alpha_genome.find(start_anchor)
    alpha_end = alpha_genome.find(end_anchor) + len(end_anchor)
    alpha_fragment = alpha_genome[alpha_start:alpha_end]

    print()
    print(f"Wuhan fragment ({len(wuhan_fragment)} bases): {wuhan_fragment}")
    print(f"Alpha fragment ({len(alpha_fragment)} bases): {alpha_fragment}")
    return alpha_fragment, wuhan_fragment


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The two fragments are not the same length, so there is an indel somewhere between
    them.

    A 60 by 54 dotplot is too big to read as a table, so the cell below uses the
    matplotlib library to plot it instead.
    However, it still uses your `get_dotplot` function to build the matrix.
    **You do not need to edit this cell.**
    """)
    return


@app.cell
def _(alpha_fragment, wuhan_fragment):
    import matplotlib.pyplot as plt

    covid_dotplot = get_dotplot(wuhan_fragment, alpha_fragment)

    # Collect the coordinates of every cell holding a 1
    dot_rows = []
    dot_columns = []
    for _row in range(len(covid_dotplot)):
        for _column in range(len(covid_dotplot[_row])):
            if covid_dotplot[_row][_column] == 1:
                dot_rows.append(_row)
                dot_columns.append(_column)

    # Create a figure and a pair of axes using matplotlib
    covid_figure, covid_axes = plt.subplots(figsize=(6, 6))
    # Plot the match (1) cells with black dots
    covid_axes.scatter(dot_columns, dot_rows, s = 6, color = "black")
    # Label the X and Y axes
    covid_axes.set_xlabel("Alpha variant")
    covid_axes.set_ylabel("Wuhan reference")
    covid_axes.set_title("Dotplot of the spike gene fragments")
    # Put position 0 in the top-left, to match how we drew the tables above
    covid_axes.invert_yaxis()
    covid_figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The scatter of isolated dots is the background noise you expect from a
    four-letter alphabet
    (there's roughly a 25% chance of a match anywhere).
    What matters is the long diagonal line from the top-left to about the middle,
    then a **step down**, followed by another diagonal to the lower-right corner.
    That step down is the deletion from the Alpha variant.

    ## <font color=red> Challenge 8: Align the viral fragments </font>

    In the Python cell below, use the `align_sequences` function to align the
    `wuhan_fragment` and `alpha_fragment` sequences and get the alignment score.
    Use the variables `wuhan_aligned`, `alpha_aligned`, and `covid_score` to hold
    the results of the `align_sequences` function.
    Then, use the `print_alignment` function to visualize the aligned sequences and
    score.
    """)
    return


@app.cell
def _(alpha_fragment, wuhan_fragment):
    # Add your code below to align and visualize the wuhan and alpha fragments
    # First, replace `"", "", 0` with the a call to `align_sequences(...)`.
    # Second, use the `print_alignment(...)` function to view the results.
    wuhan_aligned, alpha_aligned, covid_score = "", "", 0
    return (covid_score,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 9: One deletion or three? </font>

    The (most likely) true history here is a **single deletion of six consecutive
    bases**.
    Your aligner did not report it that way.
    In your alignment above,
    the six gaps are split into three two-base gaps.

    The cell below scores the alignment your code produced and compares it to the
    alignment with one clean six-base gap.
    **You do not need to edit the cell below.**
    Just run the next cell and then answer the question underneath.
    """)
    return


@app.cell
def _(covid_score):
    # The biologically correct alignment, with the six-base deletion in one block
    true_wuhan_aligned = "CCAATGTTACTTGGTTCCATGCTATACATGTCTCTGGGACCAATGGTACTAAGAGGTTTG"
    true_alpha_aligned = "CCAATGTTACTTGGTTCCATGCTAT------CTCTGGGACCAATGGTACTAAGAGGTTTG"
    true_score = score_alignment(true_wuhan_aligned, true_alpha_aligned)

    print("Score of the alignment your code found: ", covid_score)
    print("Score of the single six-base deletion:  ", true_score)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Double-click this cell and write your answers to the questions below.

    1.  **The two alignments score the same. Why does our scoring scheme have no
        preference between one six-base gap and three two-base gaps?**

        **Answer**:

    2.  **Biologically, one six-base deletion is far more plausible than three
        separate two-base deletions. How would you change the scoring scheme so the
        algorithm prefers the biologically plausible alignment?**

        **Answer**:

    3.  **This is the second time in the exercise an algorithm has given us an
        answer we did not want. What do both cases have in common?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Stretch goal </font>

    If you finish early, try the following experiment.

    Every one of your functions takes `match`, `mismatch`, and `gap` as arguments, so
    you can change the scoring scheme without changing a line of code.

    Go back to the pair of sequences from Challenge 7, the one where global
    alignment failed to find the shared `ACGTCA`.
    In the cell below, align `local_seq_1` and `local_seq_2` again, but make gaps
    cheaper by trying `gap = -1`.

    What happens, and why? And is making gaps cheap a good general fix?

    **Answer**:
    """)
    return


@app.cell
def _(local_seq_1, local_seq_2):
    # Write your stretch goal code here
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    You built an optimal global sequence aligner:

    -   `score_alignment` turns a hypothesis about homology into a number
    -   `get_dotplot` lets you see the homology before using any alignment algorithm
    -   `fill_scoring_matrix` is the core of the Needleman-Wunsch algorithm: Every
        cell computed once, from cells already filled (dynamic programming!)
    -   `traceback_alignment` recovers an alignment that has the best score

    Two things to think about:

    1.  The only part of our code that "knows" it is looking at DNA is
        `score_pair`. You can replace `score_pair` with a function that looks
        up a 20x20 matrix of amino acid scores and the rest of your code
        aligns proteins, unchanged.
    2.  Every "wrong" answer you saw today came from the scoring scheme or from
        the global assumption, not from the algorithm.
        The algorithms we used guarantee optimality, but the optimal solution is
        with respect to our assumptions (our model).
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

    I used Anthropic's Claude (Opus 5 model) to draft sections of the notebook and
    to proofread and test the notebook.
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
