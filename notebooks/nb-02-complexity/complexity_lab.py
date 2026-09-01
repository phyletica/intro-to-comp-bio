# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.0",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Measuring Complexity

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### **Claim**: An algorithm's *complexity class* matters more than the speed of your laptop

    Today we check this claim.

    The method we use to check this claim throughout this note book is the same:
    **double the input, look at the ratio of the running times.**

    | If the algorithm is... | doubling $n$ multiplies the time by... |
    |------------------------|-----------------------------------------|
    | $O(1)$                 | 1 |
    | $O(n)$                 | 2 |
    | $O(n \log n)$          | a little more than 2 |
    | $O(n^2)$               | 4 |
    | $O(n^3)$               | 8 |

    You never need to know how many operations per second your machine does.
    The ratio cancels all of that out.
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    # Import some Python modules we'll use below
    import random
    import sys
    import time

    return random, sys, time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Learning more Python

    In the next section, we will define some functions we will use to measure and
    report the runtime of algorithms.
    In doing so, we will use some features of the Python language we haven't seen
    yet.
    Let's look at some of those features first, so the functions in the next section
    won't seem so cryptic.

    ### Python's `range` function

    The `range` function in Python generates a sequence of integers,
    and is often used for controlling iterations in `for` loops.

    The basic syntax is `range(start, stop, step)`.

    Let's look at some examples.
    """)
    return


@app.cell
def _():
    # `range` assumes start = 0, stop = 5, step = 1
    for num_1 in range(5):
        print(num_1)
    return


@app.cell
def _():
    # `range` assumes start = 2, stop = 6, step = 1
    for num_2 in range(2, 6):
        print(num_2)
    return


@app.cell
def _():
    # Start at 2, increase by 2, up to 8
    for num_3 in range(2, 8, 2):
        print(num_3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If we don't need to use the the number within the `for` loop, programmers often
    give the loop variable the name "`_`".
    This is just a convention to let the reader know the loop variable isn't used
    within the loop.
    For example:
    """)
    return


@app.cell
def _():
    for _ in range(3):
        print("Hello!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Randomness in Python

    The `random` module that we imported above is useful for doing things that
    appear random.
    Below, we will use this module to create (pseudo-)random DNA sequences.
    To do so, we will create an instance of the `random.Random` Python class
    using the following syntax:

    ```python
    rand_num_gen = random.Random(seed)
    ```

    At its core, the `random.Random` class is a random number generator,
    but it also has many useful methods we can use to do stuff that appears random.

    Let's try it out.
    """)
    return


@app.cell
def _(random):
    # Create `random.Random` object initialized (seeded) with 0
    rand_num_gen = random.Random(0)
    # Print 3 random numbers between 0 and 1
    for _ in range(3):
        print(rand_num_gen.random())
    return (rand_num_gen,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The numbers above are not truly random. To see this, let's reinitialize
    (re-seed) `rand_num_gen` with zero again and generate three more random numbers.
    We get the same numbers!
    """)
    return


@app.cell
def _(rand_num_gen):
    rand_num_gen.seed(0)
    for _ in range(3):
        print(rand_num_gen.random())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Later in this exercise, we will use the `.choice()` method of the
    `random.Random` class to randomly choose nucleotides to build up random DNA
    sequences.
    Let's try that now.
    """)
    return


@app.cell
def _(rand_num_gen):
    rand_seq = ""
    for _ in range(10):
        next_rand_nuc = rand_num_gen.choice("ACGT")
        rand_seq += next_rand_nuc
    rand_seq
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Re-run the cell above several times.
    You get a different random sequence each time!

    ### Python docstrings

    Python has a really nice feature that allows you to embed documentation right
    into your code using what are called ***docstrings***.
    Docstrings are just plain-old strings put in the right location for Python to
    use them as documentation.
    One of these locations is the first line inside a function definition.

    Let's define a `hello` function with a docstring.
    """)
    return


@app.function
def hello(name):
    "Print greeting to `name`." # This is the docstring!
    print(f"Hello, {name}")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, we can use Python's `help` function to view the docstring as the documentation for our new `hello` function.
    """)
    return


@app.cell
def _():
    help(hello)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Triple quotes

    Triple quotes are often used for docstrings, so the documentation can take up
    multiple lines.
    Triple quotes in Python provide a way to create a string that spans multiple
    lines.
    """)
    return


@app.cell
def _():
    long_string = """A long
    string that
    spans several
    lines"""
    print(long_string)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### `.join()` method of strings

    All strings in python have a `.join()` method for concatenating lists of other
    strings.
    This is best understood by experimenting.
    Try replacing the `---` below and see how the output changes.
    """)
    return


@app.cell
def _():
    some_strings = ["my", "name", "is", "fred"]
    "---".join(some_strings)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Typing large numbers in Python

    Python offers a convenient way of typing large numbers.
    You can put underscore characters (`_`) in place of commas.
    For example.
    """)
    return


@app.cell
def _():
    ten_k_1 = 10000
    ten_k_2 = 10_000
    # Confirm these two numbers are equal
    ten_k_1 == ten_k_2
    return (ten_k_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You can also use the "`:,`" syntax of an f-string to add commas in string
    representations of large numbers.
    """)
    return


@app.cell
def _(ten_k_1):
    # Create a string including our `ten_k_1` variable from above
    # Notice the `:,` syntax in the curly braces
    ten_k_string = f"A pretty number: {ten_k_1:,}"
    ten_k_string
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Python sets

    We've used strings, lists, and dictionaries as "containers" in Python.
    A `set` is another type of Python container.
    You can think of a set as a dictionary without values, only keys.
    That might not sound useful, but they can be.

    First, let's create a set of gene names, test it for membership, and loop over
    it.
    """)
    return


@app.cell
def _():
    # You create a set using curly braces and items separated by commas
    my_gene_set = {"cytb", "ND2", "CMOS", "cmyc"}

    if "cytb" in my_gene_set:
        print("cytb is in the set!")

    # Add one more gene
    my_gene_set.add("KRAS")

    for my_gene in my_gene_set:
        print(my_gene)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Note**, the order of items in a set does not matter (unlike a list!).

    Sets only hold unique items, so they can be useful for finding out how many
    unique items are in a list, for example.
    """)
    return


@app.cell
def _():
    my_list = ["a", "a", "b", "b", "c"]
    print(len(my_list))
    # Create a set from the items in the list
    my_set = set(my_list)
    print(len(my_set))
    print(my_set)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sets are also (unsurprisingly) good for set operations like union and
    intersection.
    """)
    return


@app.cell
def _():
    cancer_genes = {"MYC", "IDH1", "IDH2", "TP53"}
    metabolic_genes = {"GBA", "IDH1", "IDH2", "PAH"}
    metab_cancer_genes = cancer_genes.intersection(metabolic_genes)
    metab_cancer_genes
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Creating helper functions

    Let's define some functions we will use to measure and report the runtime of
    algorithms.
    We will use these later to empirically compare the runtime of algorithms against
    our expectations based on their complexity class.

    You don't need to 100% understand how these functions work, but I recommend you
    read through the code to reinforce your learning of the Python language.

    First, let's define a function that creates a given number of random DNA
    sequences of a given length.

    Notice, for the `seed` argument of the function, we specify a default value of
    `seed = None`.
    When using the function, this allows us to choose whether to specify a seed or
    not.
    """)
    return


@app.cell
def _(random):
    def random_dna_sequences(count, length, seed = None):
        """Generate `count` random DNA sequences of the given length."""
        # If a seed isn't given, get a random number based on the computer's clock
        if seed is None:
            seed = random.random()
        # Create a (pseudo-)random number generator
        rng = random.Random(seed)
        # Create an empty list to store the random sequences
        dna_seqs = []
        for _ in range(count):
            # Start with an empty string
            seq = ""
            for _ in range(length):
                # Randomly pick a nucleotide and stick it on the end of `seq`
                next_nucleotide = rng.choice("ACGT")
                seq += next_nucleotide
            # Add sequence to our list
            dna_seqs.append(seq)
        # Deliver the random sequences
        return dna_seqs

    return (random_dna_sequences,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's try it out!

    Run the cell below several times and notice you get different sequences each
    time.

    ### <font color=red> Challenge 1 </font>

    Try changing the code below to specify a seed.
    For example, `random_dna_sequences(4, 10, 1)`.

    After specifying the seed, run the cell several times.
    Do the sequences change?
    """)
    return


@app.cell
def _(random_dna_sequences):
    some_random_seqs = random_dna_sequences(4, 10)
    some_random_seqs
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next, let's create a `get_best_runtime` function that runs any given function
    several times and keeps the **fastest** run.
    That may look like cheating, but it isn't.
    A run can only be slowed down by background noise (another process, garbage
    collection, your browser), never sped up.
    The minimum is the cleanest estimate of the work the code actually does.

    **Note**: The `get_best_runtime` function uses the asterisk (`*`) notation to
    allow a variable number of positional arguments to be given to the function.
    This is an advanced Python feature you don't need to worry about for now.
    """)
    return


@app.cell
def _(time):
    def get_best_runtime(func, *args, trials=3):
        """Return the fastest of `trials` runs of func(*args), in seconds."""
        fastest = float("inf")
        for _ in range(trials):
            start = time.perf_counter()
            func(*args)
            elapsed = time.perf_counter() - start
            fastest = min(fastest, elapsed)
        return fastest

    return (get_best_runtime,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's try it out by timing our `random_dna_sequences` function:
    """)
    return


@app.cell
def _(get_best_runtime, random_dna_sequences):
    rand_seq_run_time = get_best_runtime(random_dna_sequences, 20, 1000, trials = 5)
    rand_seq_run_time
    return (rand_seq_run_time,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next, we define `format_seconds` which simply takes a number representing
    seconds and reports it in a unit of time that is easy for us humans to read.
    """)
    return


@app.function
def format_seconds(seconds):
    """Human-readable duration."""
    if seconds < 1e-3:
        return f"{seconds * 1e6:.0f} \u00b5s"
    if seconds < 1:
        return f"{seconds * 1e3:.1f} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"
    if seconds < 3600:
        return f"{seconds / 60:.1f} min"
    if seconds < 86400:
        return f"{seconds / 3600:.1f} hr"
    if seconds < 86400 * 365:
        return f"{seconds / 86400:.1f} days"
    return f"{seconds / (86400 * 365):.1f} yr"


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's test it out using our `rand_seq_run_time` from above.
    """)
    return


@app.cell
def _(rand_seq_run_time):
    pretty_rand_seq_run_time = format_seconds(rand_seq_run_time)
    pretty_rand_seq_run_time
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Last, we define a function that creates a table in Markdown syntax.
    We will use this later to create some pretty tables of our results.
    """)
    return


@app.function
def markdown_table(headers, rows):
    """Build a markdown table from a header list and a list of row lists."""
    head = "| " + " | ".join(headers) + " |"
    rule = "|" + "|".join(["---"] * len(headers)) + "|"
    body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return "\n".join([head, rule, body])


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's create some fake data to test it out.
    """)
    return


@app.cell
def _(mo):
    table_headers = ["Name", "Height (cm)"]
    # Create a list of lists to be the table's rows
    table_rows = [
        ["Bob", 203],
        ["Sam", 153],
        ["Jane", 211],
    ]

    pretty_table = markdown_table(table_headers, table_rows)

    # Print the table as plain text
    print(pretty_table)

    # Use marimo's `mo.md()` function to render the table as Markdown-formatted HTML
    mo.md(pretty_table)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Calibration: an $O(n)$ baseline

    Before measuring anything interesting, let's confirm our functions above work,
    using an algorithm whose complexity we already know.

    The `gc_content` function below looks at each base exactly once, so its
    complexity is $O(n)$, where $n$ is the length of the sequence.
    We will define this function a little differently than in our last exercise to
    make the `for` loop over each base more explicit.
    """)
    return


@app.function
def gc_content(seq):
    gc = 0
    for base in seq:
        if base in "GC":
            gc += 1
    return gc / len(seq)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The code below will run `gc_content` several times, doubling the length of the
    sequence each time.
    The results will be presented in a Markdown-formatted table below the cell after
    you run it.
    The last column of the table will have the ratio of runtime of the current
    sequence length over the previous sequence length (which was half as long).

    ### <font color=red> Challenge 2 </font>

    Before you run the cell below, predict what that ratio should be for this
    algorithm.

    Double-click this cell and type your prediction below.

    **Your predicted ratio**: ???
    """)
    return


@app.cell
def _(get_best_runtime, mo, random_dna_sequences):
    gc_table_rows = []
    previous_run_time = None
    for dna_seq_length in [12_500, 25_000, 50_000, 100_000, 200_000, 400_000]:
        random_seq = random_dna_sequences(1, dna_seq_length)[0]
        run_time = get_best_runtime(gc_content, random_seq)
        pretty_seq_len = f"{dna_seq_length:,}"
        pretty_run_time = format_seconds(run_time)
        if previous_run_time is None:
            pretty_ratio = "\u2014" # Unicode for em dash
        else:
            ratio = run_time / previous_run_time
            pretty_ratio = f"**{ratio:.2f}**"
        row = [pretty_seq_len, pretty_run_time, pretty_ratio]
        gc_table_rows.append(row)
        previous_run_time = run_time

    mo.md(
        "### `gc_content` \u2014 doubling the sequence length\n\n"
        + markdown_table(["sequence length", "time", "ratio to previous"], gc_table_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// tip | What you should see

    Ratios clustered around **2.00**. Not exactly 2 — you will see 1.85 or 2.15
    — because timing on a real machine is noisy. The signal is the *pattern*,
    not any single number.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. An $O(n^2)$ algorithm

    Now something with real teeth: **all pairwise distances** among a set of
    sequences. This is the first step of **many** genetic methods.

    With $n$ sequences there are $n(n-1)/2$ pairs, so the work grows like $n^2$.
    Notice, that for this problem, $n$ is now the number of sequences (not the
    sequence length).

    Below, we define two functions:

    1.  `hamming_distance`: Count the differences between two sequences
    2.  `pairwise_distances`: Get the Hamming distance between every pair of
        sequences; store as a dictionary
    """)
    return


@app.cell
def _():
    def hamming_distance(seq_a, seq_b):
        """Count of positions where two equal-length strings differ."""
        dist = 0
        # Make sure the sequences have equal length
        assert len(seq_a) == len(seq_b)
        # Loop over each base
        for base_index in range(len(seq_a)):
            if seq_a[base_index] != seq_b[base_index]:
                # The sequences differ, so add to the distance
                dist += 1
        return dist

    def pairwise_distances(seqs):
        """Get a dict of the distances between all pairs of sequences."""
        distances = {}
        # Nested for loop to get distance of all pairs of sequences
        for i in range(len(seqs)):
            for j in range(i + 1, len(seqs)):
                distances[(i, j)] = hamming_distance(seqs[i], seqs[j])
        return distances

    return (pairwise_distances,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Below, we do our timing experiment of the `pairwise_distances` function.

    We will hold the sequence length (50 bases) constant and **double the number of
    sequences** between each test.

    ### <font color=red> Challenge 3 </font>

    Before running the experiment below, please predict the factor by which the
    runtime will increase each time we double the number of sequences.

    Double-click this cell and type your prediction below.

    **Your predicted ratio**: ???
    """)
    return


@app.cell
def _(
    get_best_runtime,
    mo,
    pairwise_distances,
    quad_run,
    random_dna_sequences,
):
    mo.stop(
        not quad_run.value,
        mo.md("***Waiting \u2014 This task is slow enough that we don't want it re-running every time you interact with the notebook. Please run the next cell and then click button to run the experiment.***"),
    )

    pw_dist_table_rows = []
    prev_runtime = None
    last_runtime = None
    last_num_sequences = None
    for num_seqeunces in [50, 100, 200, 400, 800]:
        rand_seqs = random_dna_sequences(num_seqeunces, 50)
        dist_run_time = get_best_runtime(pairwise_distances, rand_seqs, trials=2)
        pw_dist_table_rows.append(
            [
                f"{num_seqeunces:,}",
                f"{num_seqeunces * (num_seqeunces - 1) // 2:,}",
                format_seconds(dist_run_time),
                "\u2014" if prev_runtime is None else f"**{dist_run_time / prev_runtime:.2f}**",
            ]
        )
        prev_runtime = dist_run_time
        last_runtime = dist_run_time
        last_num_sequences = num_seqeunces

    mo.md(
        "### `pairwise_distances` \u2014 doubling the number of sequences\n\n"
        + markdown_table(
            ["sequences", "pairs", "time", "ratio to previous"], pw_dist_table_rows
        )
    )
    return last_num_sequences, last_runtime


@app.cell(hide_code=True)
def _(mo):
    quad_run = mo.ui.run_button(label="Run the pairwise timing", kind="success")
    quad_run
    return (quad_run,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// tip | What you should see

    Ratios clustered around **4.00**. You did not derive this from the source
    code — you measured it. That is what makes big-O an empirical claim about a
    program and not just a piece of notation.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Make a prediction

    You now have a measured time at 800 sequences and a measured ratio of 4.

    ### <font color=red> Challenge 4 </font>

    **Before running anything else**, work out on paper how long 1,600 sequences
    should take.

    The code below will perform the test with 1,600 sequences.
    Run the next two cells, enter your prediction below, and then click the button
    to run the test.
    """)
    return


@app.cell
def _(
    get_best_runtime,
    mo,
    pairwise_distances,
    predict_run,
    prediction,
    random_dna_sequences,
):
    mo.stop(
        not predict_run.value,
        mo.md("***Waiting \u2014 Run the cell below, make a prediction, then click the button to run the experiment.***"),
    )

    check_seqs = random_dna_sequences(1600, 50)
    check_t = get_best_runtime(pairwise_distances, check_seqs, trials=1)
    check_error = abs(check_t - prediction.value) / check_t * 100

    mo.md(
        f"""
    | | |
    |---|---|
    | Your prediction | {format_seconds(prediction.value)} |
    | Actual | **{format_seconds(check_t)}** |
    | Off by | {check_error:.0f}% |

    Arithmetic you can do in your head predicted the behavior of a real program
    on a real machine. That is the whole value of complexity analysis.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    prediction = mo.ui.number(
        start=0.0,
        stop=100000.0,
        step=0.1,
        value=1.0,
        label="**My prediction for n = 1,600 sequences (in seconds)**:",
    )
    predict_run = mo.ui.run_button(label="Now actually run it", kind="warn")
    mo.vstack([prediction, predict_run])
    return predict_run, prediction


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Where it falls over

    Keep going. The table below extrapolates from your own measurement — no new
    timing runs, just $t \times (n_{\text{new}} / n_{\text{old}})^2$.

    Realistic numbers for context: a genus-level phylogenetic study might have
    a few hundred sequences. A 16S survey has tens of thousands. A large viral
    surveillance dataset has millions.
    """)
    return


@app.cell
def _(last_num_sequences, last_runtime, mo):
    mo.stop(
        last_runtime is None,
        mo.md("*Run the timing in section 3 first.*"),
    )

    extrap_rows = []
    for extrap_n, extrap_label in [
        (1_600, ""),
        (10_000, "16S survey"),
        (100_000, "large alignment"),
        (10_000_000, "viral surveillance"),
    ]:
        extrap_t = last_runtime * (extrap_n / last_num_sequences) ** 2
        extrap_rows.append(
            [f"{extrap_n:,}", extrap_label, f"**{format_seconds(extrap_t)}**"]
        )

    mo.md(
        "### Projected runtime of `pairwise_distances`\n\n"
        + markdown_table(["sequences", "roughly", "projected time"], extrap_rows)
        + "\n\nA faster computer will only help that viral survey so much!"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// warning | The point

    Nothing is wrong with this code. It is clear, correct, and about as fast as
    plain Python gets. It is simply $O(n^2)$, and no amount of tuning changes
    that. Getting past this wall requires a **different algorithm**, not a
    better implementation.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Escape hatch one: stop redoing work

    Naive recursive Fibonacci recomputes the same values an exponential number of
    times. But, we can turn $O(2^n)$ into $O(n)$ by spending a little memory on a
    list of previous answers.
    The $n$ in calculating Fibonacci numbers is simply the number in the Fibonacci
    sequence that we want, because we need to calculate $n$ sums to calculate it.

    Let's define the two functions for calculating Fibonacci number that we saw in
    lecture.
    The first one uses recursion, and the second one builds a list storing the
    results of previous calculations.

    The second function is an example of ***dynamic programming***.
    """)
    return


@app.cell
def _():
    def fib_slow(n):
        if n < 2:
            return n
        return fib_slow(n - 1) + fib_slow(n - 2)


    def fib_fast(n):
        if n < 2:
            return n
        fib_nums = [0] * (n + 1) # Create list of n+1 zeros
        fib_nums[1] = 1
        for i in range(2, n + 1):
            fib_nums[i] = fib_nums[i - 1] + fib_nums[i - 2]
        return fib_nums[n]

    return fib_fast, fib_slow


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The code below compares the runtime of the two algorithms (`fib_slow` and
    `fib_fast`) for a given value of $n$.

    ### <font color=red> Challenge 5 </font>

    Predict how many times faster the `fib_fast` algorithm will be compared to
    `fib_slow`.

    Double-click this cell and type your prediction below.

    **`fib_fast` will be how many times faster**: ???
    """)
    return


@app.cell
def _(fib_fast, fib_n, fib_run, fib_slow, get_best_runtime, mo):
    mo.stop(not fib_run.value, mo.md("***Waiting \u2014 To run the Fibonacci experiment, run the cell below, pick an $n$ using the slider, and then click the button. Try a few different $n$ values and watch how the speed-up changes!***"))

    fib_t_slow = get_best_runtime(fib_slow, fib_n.value, trials=1)
    fib_t_fast = get_best_runtime(fib_fast, fib_n.value, trials=100)

    mo.md(
        f"""
    | version | complexity | time |
    |---|---|---|
    | `fib_slow({fib_n.value})` | $O(2^n)$ | {format_seconds(fib_t_slow)} |
    | `fib_fast({fib_n.value})` | $O(n)$ | {format_seconds(fib_t_fast)} |

    **Speedup: {fib_t_slow / fib_t_fast:,.0f}\u00d7**

    Same recurrence, same answer, a few extra lines of code. The `fib_nums` list is
    the memory you spend to buy that speedup.
    ***This is dynamic programming in action!***
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    fib_n = mo.ui.slider(
        start=20, stop=38, value=30, label="n =", show_value=True
    )
    fib_run = mo.ui.run_button(label="Time both versions", kind="success")
    mo.vstack([fib_n, fib_run])
    return fib_n, fib_run


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Escape hatch two: spend memory deliberately

    Membership testing in a `list` is $O(n)$: Python scans the list until it finds a
    match.

    For a `set` in Python, membership testing is $O(1)$: Python hashes the value and
    can jump straight to its location in memory.

    The `set` is not free. It stores a hash table, so it costs more memory for
    exactly the same contents.

    The code in the next cell creates a `list` and a `set` of 200,000 fake Gene IDs,
    and compares how much time it takes to lookup an ID in both.
    It also compares how much memory is used by the `list` and `set`.
    """)
    return


@app.cell
def _(lookup_run, mo, sys, time):
    mo.stop(not lookup_run.value, mo.md("***Waiting \u2014 To run the list vs set lookup experiment, please run the cell below and then click the button.***"))

    # Create a list of 200,000 fake Gene IDs
    lookup_ids = [f"GENE{i:07d}" for i in range(200_000)]
    # Turn the list into a set
    lookup_set = set(lookup_ids)
    lookup_missing = "GENE9999999"

    # Measure time to lookup an ID in the list of 200k Gene IDs
    lookup_t0 = time.perf_counter()
    for _ in range(20):
        _ = lookup_missing in lookup_ids
    lookup_t_list = (time.perf_counter() - lookup_t0) / 20

    # Measure time to lookup an ID in the set of 200k Gene IDs
    lookup_t0b = time.perf_counter()
    for _ in range(20_000):
        _ = lookup_missing in lookup_set
    lookup_t_set = (time.perf_counter() - lookup_t0b) / 20_000

    lookup_mb_list = sys.getsizeof(lookup_ids) / 1e6
    lookup_mb_set = sys.getsizeof(lookup_set) / 1e6

    mo.md(
        f"""
    | container | lookup | time per lookup | container memory |
    |---|---|---|---|
    | `list` | $O(n)$ | {format_seconds(lookup_t_list)} | {lookup_mb_list:.1f} MB |
    | `set`  | $O(1)$ | {format_seconds(lookup_t_set)} | {lookup_mb_set:.1f} MB |

    **{lookup_t_list / lookup_t_set:,.0f}\u00d7 faster for {lookup_mb_set / lookup_mb_list:.1f}\u00d7 the memory.**

    (Only the memory of the container is measured here; the ID strings themselves
    are shared between the two and counted in neither.)

    The conclusion is ***NOT*** "sets are better." If you do one lookup, building
    the set costs more than it saves. If you do a million, it pays for itself
    immediately. **How many times you will do the thing is part of the algorithm
    choice.**
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    lookup_run = mo.ui.run_button(
        label="Build 200,000 gene IDs and compare", kind="success"
    )
    lookup_run
    return (lookup_run,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How to submit your notebook on Canvas

    Once you've completed this notebook. Follow these steps to submit
    it on Canvas.

    1. Save the notebook by clicking the the disk icon near the bottom-right of
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

    I used Anthropic's Claude (Opus 5 model) to generate early drafts of
    some parts of this lab exercise.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
