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

with app.setup:
    # These imports are available to every cell and function in the notebook
    import math
    import random

    import matplotlib.pyplot as plt

    # The four DNA bases
    BASES = "ACGT"


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Modeling sequence evolution

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How much evolution?

    Several times this semester, we have measured how different two sequences are
    by **counting the positions where they differ**.
    We wrote a Hamming distance function in the complexity exercise, and we used
    distances like these to build a tree of SARS-CoV-2 variants in the capstone
    project.

    But the number of differences between two sequences is not the same thing as
    the **amount of evolution** that separates them.
    A site can change more than once, and a later change can hide an earlier one.
    If we want to measure evolution (to estimate a tree, date a divergence, or
    compare rates among genes), we need to account for the changes we cannot see
    in the aligned sequences.

    In this exercise, we will do that the way computational biologists do: With a
    **model** of how sequences evolve.
    Here's the plan:

    1.  **Simulate** evolution with a simple random process, one step at a time
    2.  Watch what that process does to a **single site** over a long time
    3.  Watch what it does to the **differences** between an ancestor and its
        descendant
    4.  Use the **Jukes-Cantor model** to correct for the changes we cannot see by
        comparing the sequences
    5.  Apply the correction to a real gene from two species of yeast
    6.  See where the Jukes-Cantor correction comes from: **Likelihood**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: Mutation as a random process

    We cannot predict exactly which nucleotide bases will change in a lineage, or
    when.
    But we can describe the **probabilities** of change, and that is what a model of
    sequence evolution does.

    We will use the simplest possible model, from Jukes and Cantor (1969).
    We chop time into many tiny steps, and in each step, every base in the DNA
    sequence follows the same rule:

    1.  With a small probability (the ***rate***; say 1%), the base is replaced by
        a different base (a ***substitution***)
    2.  If it is replaced, the new base is one of the other three, **each equally
        likely**

    That's the entire model!

    ### Randomness in Python

    To simulate this rule, we need random numbers.
    As in the BLAST exercise, we will create a ***random number generator*** with
    Python's `random` module (already imported for you at the top of this
    notebook): `rng = random.Random(seed)`.
    A generator has two methods we will use:

    -   `rng.random()` returns a random number between 0 and 1, with every value
        equally likely.
        That means `rng.random() < 0.01` is `True` 1% of the time.
    -   `rng.choice(a_list)` returns one item from a list at random, with every item
        equally likely.

    The ***seed*** sets the generator's starting point.
    Two generators created with the same seed produce exactly the same "random"
    numbers, which lets us (and you) repeat a simulation and get the same results.
    If you leave out the seed (`random.Random()`), you get different numbers every
    time.

    Run the cell below a few times (**you don't need to edit the code**).
    The numbers from the seeded generators never change, but the ones from the
    unseeded generator do.
    """)
    return


@app.cell
def _():
    _rng_1 = random.Random(42)
    _rng_2 = random.Random(42)
    _rng_3 = random.Random()
    print("Seed 42:     ", _rng_1.random(), _rng_1.choice(["A", "C", "G", "T"]))
    print("Seed 42 too: ", _rng_2.random(), _rng_2.choice(["A", "C", "G", "T"]))
    print("No seed:     ", _rng_3.random(), _rng_3.choice(["A", "C", "G", "T"]))
    print()

    # Count how often rng.random() is less than 0.01 in 100,000 tries
    _count = 0
    for _ in range(100_000):
        if _rng_3.random() < 0.01:
            _count += 1
    print(f"rng.random() < 0.01 was True {_count:,} times out of 100,000")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### One generator per experiment

    In this notebook, every function that needs random numbers takes a generator as
    an argument called "`rng`".
    Each experiment creates **one** generator and passes it to every function it
    calls, so the whole experiment draws from a single stream of random numbers.
    This is considered best practice for coding randomness in Python.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 1: Picking a different base </font>

    Complete the `get_different_base` function below.
    Given a base and a random number generator (`rng`), it should return one of the
    **other three** bases at random.

    A recipe:

    1.  Create an empty list called `other_bases`
    2.  Loop over `BASES`, and append every base that is **not** equal to `base`
        to `other_bases`
    3.  Set `new_base` to a random choice from `other_bases`, using
        `rng.choice()`

    /// note
    `BASES` is a variable holding the string `"ACGT"`.
    It is defined at the top of the notebook, so you can use it anywhere.
    A `for` loop over a string visits each of its letters, so `for base in BASES:`
    visits `"A"`, `"C"`, `"G"`, and `"T"`.
    ///
    """)
    return


@app.function
def get_different_base(base, rng):
    """Pick one of the three bases that differ from `base`, at random.

    Each of the three other bases is equally likely, as in the Jukes-Cantor
    model.

    Args:
        base (str): A single DNA base ("A", "C", "G", or "T").
        rng (random.Random): The random number generator to use.

    Returns:
        str: A base that is different from `base`.

    Examples:
        >>> get_different_base("A", random.Random(1)) in ["C", "G", "T"]
        True
    """
    new_base = base
    # Add your code here!
    return new_base


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function by calling it 3,000 times for each base and
    counting what comes back.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _rng = random.Random(1)
    get_different_base_works = True
    for _base in BASES:
        _counts = {"A": 0, "C": 0, "G": 0, "T": 0}
        for _ in range(3000):
            _counts[get_different_base(_base, _rng)] += 1
        print(f"Starting from {_base}: {_counts}")
        if _counts[_base] > 0:
            get_different_base_works = False
        for _other in BASES:
            # Each other base should come up about 1,000 times
            if (_other != _base) and not (800 < _counts[_other] < 1200):
                get_different_base_works = False

    print()
    if get_different_base_works:
        print("Yay, your function passed the test!")
    else:
        print("""Sorry, get_different_base should never return the base it was
    given, and it should return each of the other three bases about equally often.
    Please try again!""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 2: One step of evolution </font>

    Now, use your `get_different_base` function to complete `evolve_one_step` below.
    The `evolve_one_step` function applies the model's rule to **every base** of a
    sequence, once.
    It should return two things: the new sequence, and the number of substitutions
    that happened.

    A recipe:

    1.  Loop over every `base` in `sequence`
    2.  If `rng.random() < rate`, this base gets substituted: Add
        `get_different_base(base, rng)` to the end of `new_sequence`, and add 1 to
        `number_of_substitutions`
    3.  Otherwise (`else`), add the same `base` (unchanged) to the end of
        `new_sequence`

    /// tip
    You can add a character to the end of a string with `+=`.
    For example, `new_sequence += "A"`.
    ///

    /// note
    Notice that `evolve_one_step` passes its `rng` along to `get_different_base`.
    That way, every random number in a step comes from the same generator.
    ///
    """)
    return


@app.function
def evolve_one_step(sequence, rate, rng):
    """Evolve a sequence for one small step of time under the Jukes-Cantor model.

    Each base is independently substituted with probability `rate`. A
    substituted base is replaced by one of the other three bases at random.

    Args:
        sequence (str): The sequence at the start of the step.
        rate (float): The probability that each base is substituted during
            this step.
        rng (random.Random): The random number generator to use.

    Returns:
        tuple[str, int]: The sequence at the end of the step, and the number of
            substitutions that happened during the step.

    Examples:
        >>> evolve_one_step("ACGT", 0.0, random.Random(1))
        ('ACGT', 0)
    """
    new_sequence = ""
    number_of_substitutions = 0
    # Add your code here!
    return new_sequence, number_of_substitutions


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _rng = random.Random(2)
    _test_sequence = "ACGT" * 2500
    _same, _same_count = evolve_one_step(_test_sequence, 0.0, _rng)
    _all, _all_count = evolve_one_step(_test_sequence, 1.0, _rng)
    _some, _some_count = evolve_one_step(_test_sequence, 0.1, _rng)

    evolve_one_step_works = True
    _messages = []
    if (_same != _test_sequence) or (_same_count != 0):
        evolve_one_step_works = False
        _messages.append("With rate = 0, the sequence should not change at all.")
    if (len(_all) != len(_test_sequence)) or (_all_count != len(_test_sequence)):
        evolve_one_step_works = False
        _messages.append(
            "With rate = 1, every base should be substituted, and the new "
            + "sequence should be the same length as the old one."
        )
    elif any(_all[_i] == _test_sequence[_i] for _i in range(len(_all))):
        evolve_one_step_works = False
        _messages.append("A substituted base should always change to a different base.")
    if not (850 < _some_count < 1150):
        evolve_one_step_works = False
        _messages.append(
            f"With rate = 0.1, about 1,000 of 10,000 bases should change, but "
            + f"{_some_count:,} did."
        )

    print(f"rate = 0.0: {_same_count:,} substitutions")
    print(f"rate = 1.0: {_all_count:,} substitutions")
    print(f"rate = 0.1: {_some_count:,} substitutions")
    print()
    if evolve_one_step_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your evolve_one_step function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (evolve_one_step_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Many steps of evolution

    The function below calls your `evolve_one_step` over and over, passing it the
    same random number generator (`rng`) every time, and keeps a record of the
    sequence every few steps.
    **You do not need to edit it.**

    Each record is a dictionary with three entries:

    -   "`time`": How long the sequence has evolved, measured as the number of steps
        times the rate.
        This is the **expected number of substitutions per site**, which is how
        evolutionary biologists usually measure the divergence between sequences and
        the length of a branch in a phylogenetic tree.
        A time of 1 means that, on average, each site has been substituted once.
    -   "`substitutions_per_site`": The number of substitutions that actually
        happened, divided by the length of the sequence.
        Because the process is random, this will be close to "`time`", but not
        exactly equal.
    -   "`sequence`": The sequence at that time.

    /// note
    In a real lineage, we would never see the `"substitutions_per_site"` value, only
    the sequences.
    Knowing the true answer is one of the great advantages of a simulation: We can
    check whether our methods get the right answer!
    ///
    """)
    return


@app.function
def simulate_history(
    ancestor,
    number_of_steps,
    rate,
    rng,
    record_every = 10,
    step_function = None,
):
    """Evolve a sequence for many steps and record it along the way.

    Args:
        ancestor (str): The sequence at time 0.
        number_of_steps (int): How many steps to evolve the sequence.
        rate (float): The probability that each base is substituted in each
            step.
        rng (random.Random): The random number generator to use for every step.
        record_every (int): Record the sequence every this many steps.
        step_function (function): The function that evolves the sequence by one
            step, called as `step_function(sequence, rate, rng)`. If None,
            `evolve_one_step` is used.

    Returns:
        list[dict]: One record per recorded time point (including time 0), each
            with the keys "time", "substitutions_per_site", and "sequence".
    """
    if step_function is None:
        step_function = evolve_one_step
    sequence = ancestor
    total_substitutions = 0
    history = [{"time": 0.0, "substitutions_per_site": 0.0, "sequence": ancestor}]
    for step in range(1, number_of_steps + 1):
        sequence, number_of_substitutions = step_function(sequence, rate, rng)
        total_substitutions += number_of_substitutions
        if step % record_every == 0:
            history.append({
                "time": step * rate,
                "substitutions_per_site": total_substitutions / len(ancestor),
                "sequence": sequence,
            })
    return history


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 2: Following a site through time

    Let's start with the simplest possible experiment.
    What happens to a site that starts out as an `A`?

    Every site in our model evolves **independently**, following the same rule.
    So a sequence of 1,000 `A`s is really 1,000 separate runs of the same experiment.
    The cell below evolves `"AAAA...A"` for 300 steps with a rate of 0.01 (so, up to
    a time of 3 expected substitutions per site), then plots the fraction of sites
    that are `A`, `C`, `G`, and `T` over time.
    """)
    return


@app.cell
def _(evolve_one_step_works, mo):
    mo.stop(
        not evolve_one_step_works,
        mo.md("***Waiting — Get your `evolve_one_step` function working first.***"),
    )

    # One generator, with a seed, for this whole experiment
    _rng = random.Random(2026)
    history_from_a = simulate_history(
        "A" * 1000,
        number_of_steps = 300,
        rate = 0.01,
        rng = _rng,
        record_every = 5,
    )

    _times = [record["time"] for record in history_from_a]
    _figure, _axes = plt.subplots(figsize = (7, 4))
    for _base in BASES:
        _fractions = []
        for _record in history_from_a:
            _fractions.append(_record["sequence"].count(_base) / 1000)
        _axes.plot(_times, _fractions, label = _base, linewidth = 2)
    _axes.axhline(0.25, color = "gray", linestyle = ":", linewidth = 1)
    _axes.set_xlabel("Time (expected substitutions per site)")
    _axes.set_ylabel("Fraction of sites")
    _axes.set_title("1,000 sites that all started as A")
    _axes.set_ylim(0, 1)
    _axes.legend()
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 3: The long run </font>

    Double-click this cell and answer the questions below.

    1.  **By the end of the simulation, roughly what fraction of the sites are `A`?
        What about `C`, `G`, and `T`? Why does the model end up here, and would the
        answer be different if every site had started as `G`?**

        **Answer**:

    2.  **When your `evolve_one_step` function decides what happens to a base, what
        information does it use? What information about the site does it NOT use?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A random process in which the next step depends **only on the current state**,
    and not on how the process got there, is called a ***Markov chain***.
    Our model is a Markov chain, and most models of sequence evolution used
    in biology are as well.

    # Part 3: Differences can hide substitutions

    Now, let's evolve an ancestral sequence, and ask how different its descendant is
    as time goes on.

    ## <font color=red> Challenge 4: The p-distance </font>

    The ***p-distance*** between two aligned sequences is the **proportion** of
    sites that differ.
    It is the Hamming distance divided by the number of sites compared.

    Real alignments contain gaps (`-`) and unknown bases (`N`), so we will only
    compare sites where **both** sequences have one of the four bases (`A`, `C`,
    `G`, or `T`).

    Complete the `p_distance` function below.
    A recipe:

    1.  Loop over every index of `seq_1` (we assume the sequences are aligned, so
        the same index works for both)
    2.  If **both** bases at that index are in `BASES`, add 1 to `number_compared`
    3.  If they are both in `BASES` **and** they are different, also add 1 to
        `number_different`

    /// tip
    The `in` operator works on strings: `"A" in BASES` is `True`, and
    `"-" in BASES` is `False`.
    ///
    """)
    return


@app.function
def p_distance(seq_1, seq_2):
    """Calculate the proportion of sites that differ between two aligned sequences.

    Only sites where both sequences have one of the four DNA bases are compared;
    gaps and ambiguous bases are skipped.

    Args:
        seq_1 (str): The first aligned sequence.
        seq_2 (str): The second aligned sequence, the same length as `seq_1`.

    Returns:
        float: The number of sites that differ divided by the number of sites
            compared, or 0.0 if no sites could be compared.

    Examples:
        >>> p_distance("ACGT", "ACGA")
        0.25
        >>> p_distance("AC-T", "ACGA")
        0.3333333333333333
    """
    number_compared = 0
    number_different = 0
    # Add your code here!

    if number_compared == 0:
        return 0.0
    return number_different / number_compared


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _p_test_cases = [
        (("ACGT", "ACGT"), 0.0),
        (("ACGT", "ACGA"), 0.25),
        (("ACGT", "TGCA"), 1.0),
        (("AC-T", "ACGA"), 1 / 3),
        (("ACNTG", "AC-TC"), 0.25),
    ]
    _p_failures = []
    for (_seq_1, _seq_2), _expected in _p_test_cases:
        _found = p_distance(_seq_1, _seq_2)
        if abs(_found - _expected) > 1e-9:
            _p_failures.append(
                f"  {_seq_1} vs {_seq_2}: expected {_expected:.4f}, got {_found:.4f}"
            )

    p_distance_works = len(_p_failures) == 0
    if p_distance_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, p_distance failed these cases:\n" + "\n".join(_p_failures))
    return (p_distance_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Evolving an ancestor

    The cell below creates a random 1,000-base ancestral sequence and evolves it for
    300 steps with a rate of 0.01, recording the descendant every 10 steps.

    The second cell displays the results of the simulation for the first 60 bases of
    the ancestor and its descendant at different recorded time points (every 10
    steps).

    The third cell provides a slider to control the recorded time point displayed by
    the second cell.
    *E.g.*, increasing the "Record number" slider by one shows the state of the
    simulation after 10 more steps.

    **You don't need to edit the next three cells**.
    """)
    return


@app.cell
def _(evolve_one_step_works, mo):
    mo.stop(
        not evolve_one_step_works,
        mo.md("***Waiting — Get your `evolve_one_step` function working first.***"),
    )

    # One generator, with a seed, for this whole experiment
    _rng = random.Random(1969)
    ancestor = ""
    for _ in range(1000):
        ancestor += _rng.choice(BASES)
    history = simulate_history(
        ancestor,
        number_of_steps = 300,
        rate = 0.01,
        rng = _rng,
        record_every = 10,
    )
    return ancestor, history


@app.cell
def _(ancestor, history, mo, record_slider):
    _record = history[record_slider.value]
    _descendant = _record["sequence"]
    _match_line = ""
    for _i in range(60):
        if ancestor[_i] == _descendant[_i]:
            _match_line += "|"
        else:
            _match_line += " "

    mo.md(
        f"""
    **Time** (expected substitutions per site): {_record["time"]:.2f}

    **Substitutions that actually happened** (per site): {_record["substitutions_per_site"]:.3f}

    **p-distance** (proportion of sites that differ): {p_distance(ancestor, _descendant):.3f}

    ```
    Ancestor:   {ancestor[:60]}
                {_match_line}
    Descendant: {_descendant[:60]}
    ```
    """
    )
    return


@app.cell(hide_code=True)
def _(history, mo):
    record_slider = mo.ui.slider(
        start = 0,
        stop = len(history) - 1,
        step = 1,
        value = 5,
        label = "Record number (drag to move through time)",
    )
    record_slider
    return (record_slider,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below shows the results of your simulation above as a graph of the
    p-distance between the ancestor and its descendant against the number of
    substitutions that actually happened.
    If every substitution produced one new observable difference, the points would
    fall on the dashed line.
    (**You don't need to edit the next cell**.)
    """)
    return


@app.cell
def _(ancestor, history, mo, p_distance_works):
    mo.stop(
        not p_distance_works,
        mo.md("***Waiting — Get your `p_distance` function working first.***"),
    )

    true_distances = []
    observed_p = []
    for _record in history:
        true_distances.append(_record["substitutions_per_site"])
        observed_p.append(p_distance(ancestor, _record["sequence"]))

    _figure, _axes = plt.subplots(figsize = (6, 5))
    _axes.scatter(true_distances, observed_p, color = "black", s = 15,
                  label = "Simulation")
    _axes.plot([0, 3], [0, 3], color = "gray", linestyle = "--",
               label = "One difference per substitution")
    _axes.axhline(0.75, color = "firebrick", linestyle = ":", label = "0.75")
    _axes.set_xlim(0, 3.1)
    _axes.set_ylim(0, 1.2)
    _axes.set_xlabel("Substitutions per site that actually happened")
    _axes.set_ylabel("p-distance (proportion of sites that differ)")
    _axes.set_title("Differences between an ancestor and its descendant")
    _axes.legend(loc = "lower right")
    _figure
    return observed_p, true_distances


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 5: Saturation </font>

    Double-click this cell and answer the questions below.

    1.  **Early on, the points follow the dashed line, but then they fall further and
        further below it.
        In other words, some substitutions do not add a new difference between the
        sequences.
        Describe two ways this can happen. (The slider above might help!)**

        **Answer**:

    2.  **The p-distance levels off near 0.75, even as the number of substitutions
        keeps climbing.
        Why does it plateau at 0.75, and not 1?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 4: Correcting for what we cannot see

    Counting differences **underestimates** the amount of evolution that has
    occurred in a sequence's lineage, and the longer the time, the worse this bias
    gets.
    The good news is that our model tells us exactly how many differences to
    ***expect*** after any amount of time $t$.
    Jukes and Cantor worked out that the probability that a site differs from its
    ancestor after time $t$ is:

    $$
    P(\text{different}) = \frac{3}{4}\left(1 - e^{-\frac{4}{3}t}\right)
    $$

    To get a sense of how this equation works,
    let's look at the two ends of the time ($t$) continuum.
    When $t = 0$, $e^{0} = 1$, so the probability the site differs is $0$.
    As $t$ gets large, $e^{-\frac{4}{3}t}$ shrinks toward $0$, so the probability
    the site differs approaches $\frac{3}{4}$, which is exactly what our simulation
    did.

    /// details | Deriving the Jukes and Cantor equation (optional)
    To derive the equation of Jukes and Cantor,
    let's follow one site through our simulation, one step at a time.
    Each step, the site is substituted with probability $r$ (the rate), and a
    substituted base becomes each of the other three bases with probability
    $\frac{1}{3}$.

    Let $s_n$ be the probability that the site **matches** its ancestral base after
    $n$ steps.
    There are two ways the site can match after the next step ($n + 1$):

    1.  It matches now (probability $s_n$) and is not substituted in the next step
        (probability $1 - r$)
    2.  It does not match now (probability $1 - s_n$), is substituted (probability
        $r$), **and** the new base happens to be the ancestral one (probability
        $\frac{1}{3}$)

    Adding these up to get the probability that the site matches its ancestral base
    after $n+1$ steps ($s_{n+1}$):

    $$
    s_{n+1} = s_n (1 - r) + (1 - s_n)\frac{r}{3}
    $$

    Now, if we subtract $\frac{1}{4}$ from both sides and do some simplifying, we
    get:

    $$
    s_{n+1} - \frac{1}{4} = \left(1 - \frac{4}{3}r\right)\left(s_n - \frac{1}{4}\right)
    $$

    This tells us that the gap between $s_n$ and $\frac{1}{4}$ shrinks by the same
    factor, $1 - \frac{4}{3}r$, every time step.
    (This is why the simulation in Part 2 settled at $\frac{1}{4}$.)
    The site starts out matching, so $s_0 = 1$, and the starting gap between $s_0$
    and $\frac{1}{4}$ is $1 - \frac{1}{4} = \frac{3}{4}$.
    After $n$ steps, the gap between $s_n$ and $\frac{1}{4}$ has shrunk $n$ times:

    $$
    s_n = \frac{1}{4} + \frac{3}{4}\left(1 - \frac{4}{3}r\right)^{n}
    $$

    Time is $t = n r$ (the expected number of substitutions per site), so
    $n = t / r$.
    Real evolution happens in continuous time, not discrete steps, so imagine making
    the steps tiny ($r \to 0$) while keeping $t$ the same.
    A famous limit from calculus says that
    $\left(1 + \frac{a}{m}\right)^{m} \to e^{a}$ as $m$ gets large, so

    $$
    \left(1 - \frac{4}{3}r\right)^{t / r} \to e^{-\frac{4}{3}t}
    $$

    That gives the probability that the site matches its ancestor,
    $\frac{1}{4} + \frac{3}{4}e^{-\frac{4}{3}t}$, and the probability that it
    differs is one minus that:

    $$
    P(\text{different}) = \frac{3}{4} - \frac{3}{4}e^{-\frac{4}{3}t} = \frac{3}{4}\left(1 - e^{-\frac{4}{3}t}\right)
    $$

    Our simulation uses $r = 0.01$, which is small enough that the formula with
    steps and the formula with continuous time (with $e$) agree to within about
    0.002.
    ///

    The function below calculates this probability.
    The cell after it adds the prediction to the plot of our simulation.
    **You do not need to edit the next two cells**.
    """)
    return


@app.function
def jc_prob_different(t):
    """Probability that a site differs from its ancestor after time `t` (JC69).

    Args:
        t (float): Time, in expected substitutions per site.

    Returns:
        float: The probability that the site's base differs from the ancestral
            base.

    Examples:
        >>> jc_prob_different(0.0)
        0.0
    """
    return 0.75 * (1 - math.exp(-4 * t / 3))


@app.cell
def _(mo, observed_p, true_distances):
    _curve_t = [_i / 100 for _i in range(0, 311)]
    _curve_p = [jc_prob_different(_t) for _t in _curve_t]

    _figure, _axes = plt.subplots(figsize = (6, 5))
    _axes.scatter(true_distances, observed_p, color = "black", s = 15,
                  label = "Simulation")
    _axes.plot(_curve_t, _curve_p, color = "steelblue", linewidth = 2,
               label = "Jukes-Cantor prediction")
    _axes.plot([0, 3], [0, 3], color = "gray", linestyle = "--",
               label = "One difference per substitution")
    _axes.axhline(0.75, color = "firebrick", linestyle = ":", label = "0.75")
    _axes.set_xlim(0, 3.1)
    _axes.set_ylim(0, 1.2)
    _axes.set_xlabel("Substitutions per site")
    _axes.set_ylabel("p-distance (proportion of sites that differ)")
    _axes.set_title("The model predicts saturation")
    _axes.legend(loc = "lower right")
    mo.vstack([_figure])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Turning it around

    The equation above tells us about expected differences from time.
    But with real sequences, we observe the differences (the p-distance, $p$) and
    want to know the time or the amount of evolution that has occurred between the
    sequences.
    Setting $P(\text{different}) = p$ and solving for $t$ gives the
    ***Jukes-Cantor (JC) distance***:

    $$
    d = -\frac{3}{4}\ln\left(1 - \frac{4}{3}p\right)
    $$

    where $\ln$ is the natural logarithm (`math.log` in Python).
    This is our estimate of the number of substitutions per site, **including the
    ones we cannot see** when we compare the sequences.

    /// details | Deriving the JC distance (optional)
    Start from $p = \frac{3}{4}\left(1 - e^{-\frac{4}{3}t}\right)$.
    Multiply both sides by $\frac{4}{3}$ and rearrange to get
    $e^{-\frac{4}{3}t} = 1 - \frac{4}{3}p$.
    Take the natural log of both sides: $-\frac{4}{3}t = \ln\left(1 - \frac{4}{3}p\right)$.
    Multiply both sides by $-\frac{3}{4}$ to get $t$.
    ///

    ## <font color=red> Challenge 6: The Jukes-Cantor distance </font>

    Complete the `jc_distance` function below, which converts a p-distance into a
    Jukes-Cantor distance.

    There is a gotcha in this calculation.
    If $p \geq 0.75$, then $1 - \frac{4}{3}p$ is zero or negative, and the logarithm
    of zero or a negative number is undefined (Python will give you an error).
    Biologically, it means the sequences are saturated, and we cannot tell how much
    time has passed (or how much evolution has happened).
    So:

    1.  If `p` is greater than or equal to 0.75, set `distance` to `math.inf`
        (Python's value for infinity)
    2.  Otherwise, set `distance` using the equation above

    /// tip
    Be careful with the parentheses:
    $\frac{4}{3}p$ can be written as `(4 / 3) * p`.
    ///
    """)
    return


@app.function
def jc_distance(p):
    """Convert a p-distance into a Jukes-Cantor (JC69) distance.

    Args:
        p (float): The proportion of sites that differ between two sequences.

    Returns:
        float: The estimated number of substitutions per site, or `math.inf` if
            `p` is 0.75 or greater (the sequences are saturated).

    Examples:
        >>> round(jc_distance(0.3), 4)
        0.3831
        >>> jc_distance(0.8)
        inf
    """
    distance = 0.0
    # Add your code here!
    return distance


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _jc_test_cases = [
        (0.0, 0.0),
        (0.1, 0.107326),
        (0.3, 0.383119),
        (0.6, 1.207078),
        (0.75, math.inf),
        (0.9, math.inf),
    ]
    _jc_failures = []
    for _p, _expected in _jc_test_cases:
        _found = jc_distance(_p)
        if _expected == math.inf:
            _ok = _found == math.inf
        else:
            _ok = abs(_found - _expected) < 1e-5
        if not _ok:
            _jc_failures.append(f"  p = {_p}: expected {_expected}, got {_found}")

    jc_distance_works = len(_jc_failures) == 0
    if jc_distance_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, jc_distance failed these cases:\n" + "\n".join(_jc_failures))
    return (jc_distance_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now let's see how well the correction works on our simulation.
    The plot below compares the raw p-distance and your Jukes-Cantor distance to the
    number of substitutions that actually happened.
    A perfect estimate would fall on the dashed line.
    """)
    return


@app.cell
def _(jc_distance_works, mo, observed_p, true_distances):
    mo.stop(
        not jc_distance_works,
        mo.md("***Waiting — Get your `jc_distance` function working first.***"),
    )

    _jc_estimates = [jc_distance(_p) for _p in observed_p]

    _figure, _axes = plt.subplots(figsize = (6, 5))
    _axes.scatter(true_distances, observed_p, color = "black", s = 15,
                  label = "p-distance")
    _axes.scatter(true_distances, _jc_estimates, color = "steelblue", s = 15,
                  label = "Jukes-Cantor distance")
    _axes.plot([0, 3], [0, 3], color = "gray", linestyle = "--",
               label = "Perfect estimate")
    _axes.set_xlim(0, 3.1)
    _axes.set_ylim(0, 3.1)
    _axes.set_xlabel("Substitutions per site that actually happened")
    _axes.set_ylabel("Estimated distance")
    _axes.set_title("Correcting for multiple hits")
    _axes.legend(loc = "upper left")

    _rows = []
    for _i in range(0, len(true_distances), 5):
        _rows.append(
            f"| {true_distances[_i]:.3f} | {observed_p[_i]:.3f} "
            + f"| {_jc_estimates[_i] + 0.0:.3f} |"
        )
    _table = mo.md(
        "| Substitutions per site | p-distance | Jukes-Cantor distance |\n"
        + "|--:|--:|--:|\n"
        + "\n".join(_rows)
    )
    mo.hstack([_figure, _table], align = "center")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 7: How well does the correction work? </font>

    Double-click this cell and answer the questions below.

    1.  **When fewer than one substitution per site has happened, how do the
        p-distance and the Jukes-Cantor distance compare to the truth?**

        **Answer**:

    2.  **As the true distance gets larger (say, above 2), the Jukes-Cantor
        estimates get noisier. Looking at the equation, why does a small amount of
        random noise in $p$ cause a big error in $d$ when $p$ is close to 0.75?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 5: A real gene

    Now, let's apply the Jukes-Cantor evolutionary distance correction to real
    sequences.
    The file
    [`SSA3.fasta`](https://github.com/phyletica/intro-to-comp-bio/blob/main/notebooks/data/SSA3.fasta)
    contains an alignment of the *SSA3* gene from two species of yeast:
    *Saccharomyces eubayanus* and *Saccharomyces paradoxus*.
    *SSA3* encodes a heat-shock protein (Hsp70) that helps other proteins fold.

    *SSA3* is a protein-coding gene, and this alignment starts at its start codon,
    so every third base is the first position of a codon.
    Recall that because the genetic code is redundant, many substitutions at the
    **third** position of a codon do not change the amino acid (they are
    ***synonymous*** substitutions), while most substitutions at the first and
    second positions do change the amino acid (**nonsynonymous** substitutions).

    We can pull out the bases at each codon position with a slice that has a
    ***step*** argument (an integer after a second colon).
    *E.g.*, `sequence[0::3]` takes every third base starting at index 0, and
    `sequence[2::3]` takes every third base starting at index 2.
    For example, `"ATGGCTTAA"[2::3]` is `"GTA"`.

    The `parse_fasta_url` function below is the one from the string search
    exercise.
    We will use it in the second Python cell below to read the alignment straight
    from our course's GitHub repository.
    **You do not need to edit the next two cells**.
    """)
    return


@app.function
def parse_fasta_url(fasta_url):
    """Download a FASTA file from a URL and parse it into a dictionary.

    Reads the response one line at a time instead of downloading the whole file
    into memory first. Lines beginning with ">" start a new record; every other
    line is treated as sequence, converted to uppercase, and joined onto the
    record currently being read.

    Args:
        fasta_url (str): The URL of a FASTA file, for example a link to the
            NCBI efetch service.

    Returns:
        dict[str, str]: Maps the description line of each record, with the
            leading ">" removed, to that record's sequence. The dictionary is
            empty if the file contains no records.

    Raises:
        urllib.error.URLError: If the URL cannot be reached.
    """
    import urllib.request

    sequences = {}
    # Variables to keep track of the current sequence and its name
    current_name = None
    current_seq = ""

    # Open the URL and read it one line at a time, so we never hold the whole
    # file in memory at once
    with urllib.request.urlopen(fasta_url) as response:
        for raw_line in response:
            # Each line is in raw bytes, so we need to decode it into text
            decoded_line = raw_line.decode("utf-8")
            # Strip off the newline character
            line = decoded_line.strip()
            if not line:
                continue  # Line is empty, skip it!
            if line[0] == ">":
                # A ">" starts a new record, so first store the record we just
                # finished reading (if there was one)
                if current_name is not None:
                    sequences[current_name] = current_seq
                # Extract the sequence name (removing the ">" symbol
                current_name = line[1:]
                # Remove any space that was between the ">" and the name
                current_name = current_name.strip()
                # Reset current_seq to an empty string
                current_seq = ""
            else:
                # A sequence line, so add it to the sequence we are building
                current_seq += line.upper()
    # The last record has no ">" after it, so store it once the loop ends
    if current_name is not None:
        sequences[current_name] = current_seq

    return sequences


@app.cell
def _():
    ssa3_url = (
        "https://raw.githubusercontent.com/phyletica/intro-to-comp-bio/"
        + "refs/heads/main/notebooks/data/SSA3.fasta"
    )
    ssa3_sequences = parse_fasta_url(ssa3_url)
    for _name in ssa3_sequences:
        print(f"{_name}: {len(ssa3_sequences[_name]):,} aligned positions")

    eubayanus = ssa3_sequences["Seub_SSA3"]
    paradoxus = ssa3_sequences["Spar_SSA3"]

    # Split each sequence by codon position
    site_sets = {
        "Whole gene": (eubayanus, paradoxus),
        "1st codon positions": (eubayanus[0::3], paradoxus[0::3]),
        "2nd codon positions": (eubayanus[1::3], paradoxus[1::3]),
        "3rd codon positions": (eubayanus[2::3], paradoxus[2::3]),
    }
    return eubayanus, paradoxus, site_sets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below uses your `p_distance` and `jc_distance` functions to compare the
    two species, for the whole gene and for each codon position.
    **You do not need to edit this cell.**
    """)
    return


@app.cell
def _(jc_distance_works, mo, p_distance_works, site_sets):
    mo.stop(
        not (p_distance_works and jc_distance_works),
        mo.md("***Waiting — Get `p_distance` and `jc_distance` working first.***"),
    )

    _rows = []
    for _label in site_sets:
        _seq_1, _seq_2 = site_sets[_label]
        _p = p_distance(_seq_1, _seq_2)
        _d = jc_distance(_p)
        _rows.append(
            f"| {_label} | {_p:.3f} | {_d:.3f} | {100 * (_d - _p) / _p:.0f}% |"
        )

    mo.md(
        "| Sites | p-distance | Jukes-Cantor distance | Increase |\n"
        + "|:--|--:|--:|--:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Transitions and transversions

    The four bases of DNA come in two chemical types:
    The ***purines*** (`A` and `G`)
    and
    the ***pyrimidines*** (`C` and `T`).
    A substitution within a type (`A` ↔ `G` or `C` ↔ `T`) is a ***transition***.
    A substitution between types (*e.g.*, `A` ↔ `C`) is a ***transversion***.

    The cell below counts how many of the differences between the two yeast
    sequences are transitions and how many are transversions.
    **You do not need to edit this cell.**
    """)
    return


@app.cell
def _(mo, site_sets):
    _purines = "AG"
    _pyrimidines = "CT"
    _rows = []
    for _label in site_sets:
        _seq_1, _seq_2 = site_sets[_label]
        _transitions = 0
        _transversions = 0
        for _i in range(len(_seq_1)):
            _b1 = _seq_1[_i]
            _b2 = _seq_2[_i]
            if (_b1 in BASES) and (_b2 in BASES) and (_b1 != _b2):
                _same_type = ((_b1 in _purines) and (_b2 in _purines)) or (
                    (_b1 in _pyrimidines) and (_b2 in _pyrimidines)
                )
                if _same_type:
                    _transitions += 1
                else:
                    _transversions += 1
        _rows.append(f"| {_label} | {_transitions} | {_transversions} |")

    mo.md(
        "| Sites | Transitions | Transversions |\n"
        + "|:--|--:|--:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 8: Interpreting the yeast results </font>

    Double-click this cell and answer the questions below.

    1.  **Looking at the table of p-distances and Jukes-Cantor distances above,
        which codon position differs the most between the two species?
        Why do you think that is?**

        **Answer**:

    2.  **For which codon position does the Jukes-Cantor correction make the biggest
        difference? Why that position?**

        **Answer**:

    3.  **Under the Jukes-Cantor model of sequence evolution, a base is equally
        likely to change to any of the other three.
        For any base, only one of those three changes is a transition, so the model
        expects about one transition for every two transversions.
        Compare this expectation of the Jukes-Cantor model to the table of the
        number of observed transition and transversion differences between the yeast
        sequences.
        What does this tell you about the Jukes-Cantor model for these sequences?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 6: Where does the correction come from? Likelihood

    We have been treating the Jukes-Cantor distance as a handy formula, but it is
    actually the answer to a question:
    **What amount of time $t$ makes the sequences we observed most probable?**

    ### A coin-flipping warm-up example

    Suppose you flip a coin 10 times and get 7 heads.
    If the probability of heads is $\theta$, the probability of that result (in the
    order it happened) is:

    $$
    L(\theta) = \theta^{7} (1 - \theta)^{3}
    $$

    We can try different values of $\theta$ to see how the probability of the
    coin-flip data changes:

    | $\theta$ | 0.3 | 0.5 | 0.7 | 0.9 |
    |:--|--:|--:|--:|--:|
    | $L(\theta)$ | 0.000075 | 0.00098 | **0.0022** | 0.00048 |

    When we treat this probability as a function of $\theta$, with the data fixed,
    we call it the ***likelihood***.
    The value of $\theta$ that makes the data most probable ($\theta = 0.7$ here) is
    the ***maximum likelihood estimate***.

    ### Sites are coin flips

    Two aligned sequences work the same way.
    Under the Jukes-Cantor model, each site is like a coin flip that comes up
    "different" with probability $P(\text{different})$, which depends on $t$.
    If we compared $n$ sites and $k$ of them differ, the likelihood of $t$ is:

    $$
    L(t) = P(\text{different})^{k} \times \big(1 - P(\text{different})\big)^{n - k}
    $$

    /// note
    The full Jukes-Cantor likelihood also includes the probability of the particular
    bases we see at each site, but those extra terms do not depend on $t$, so they do
    not change which value of $t$ is best.
    ///

    ### The computer challenge with multiplying probabilities

    To get the likelihood, we multiply one probability per site (column of the
    aligned sequences).
    The cell below does exactly that for the whole yeast gene, using $t = 0.18$, and
    prints the running product along the way.
    **You do not need to edit this cell.**
    """)
    return


@app.cell
def _(eubayanus, mo, paradoxus):
    _prob_different = jc_prob_different(0.18)
    _product = 1.0
    _lines = []
    _checkpoints = [100, 500, 1000, 1500, len(eubayanus)]
    for _i in range(len(eubayanus)):
        if (eubayanus[_i] in BASES) and (paradoxus[_i] in BASES):
            if eubayanus[_i] != paradoxus[_i]:
                _product *= _prob_different
            else:
                _product *= 1 - _prob_different
        if (_i + 1) in _checkpoints:
            _lines.append(f"| {_i + 1:,} | {_product} |")

    mo.md(
        "| After this many alignment positions | Running product (likelihood) |\n"
        + "|--:|:--|\n"
        + "\n".join(_lines)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The likelihood of the whole gene is about $10^{-361}$, a ***very*** small
    number!
    The smallest positive number Python can store is about $5 \times 10^{-324}$, so
    the product silently becomes **0.0**.
    With thousands of sites, likelihoods are usually ***very small***, so we need
    another approach.

    The fix is to work with the ***log-likelihood*** instead.
    Because $\ln(a \times b) = \ln(a) + \ln(b)$, the log of a product is a **sum** of
    logs, and sums of moderately sized numbers are no problem for a computer.
    Taking the log of both sides of our $L(t)$ equation above, we get:

    $$
    \ln L(t) = k \ln\big(P(\text{different})\big) + (n - k)\ln\big(1 - P(\text{different})\big)
    $$

    The logarithm always increases when its input increases, so the value of $t$ that
    maximizes $\ln L(t)$ also maximizes $L(t)$.

    ## <font color=red> Challenge 9: The log-likelihood </font>

    Complete the `log_likelihood` function below using the $\ln L(t)$ equation
    above.
    The function already calculates $P(\text{different})$ for you with
    `jc_prob_different`.
    In the function, $n$ is `number_of_sites` and $k$ is `number_of_differences`.

    /// tip
    `math.log(x)` is the natural log of `x` in Python.
    ///
    """)
    return


@app.function
def log_likelihood(t, number_of_sites, number_of_differences):
    """Log-likelihood of time `t` given the number of sites that differ
    (assuming the JC69 model of sequence evolution).

    Args:
        t (float): Time, in expected substitutions per site. Must be greater
            than 0.
        number_of_sites (int): The number of sites compared (n).
        number_of_differences (int): The number of those sites that differ (k).

    Returns:
        float: The natural log of the likelihood of `t`.

    Examples:
        >>> round(log_likelihood(0.5, 100, 30), 4)
        -62.0231
    """
    probability_different = jc_prob_different(t)
    log_like = 0.0
    # Add your code here!
    return log_like


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _ll_test_cases = [
        ((0.5, 100, 30), -62.023096),
        ((0.1, 50, 5), -16.265905),
        ((1.0, 200, 100), -139.729672),
    ]
    _ll_failures = []
    for _args, _expected in _ll_test_cases:
        _found = log_likelihood(*_args)
        if abs(_found - _expected) > 1e-4:
            _ll_failures.append(
                f"  log_likelihood{_args}: expected {_expected:.4f}, got {_found:.4f}"
            )

    log_likelihood_works = len(_ll_failures) == 0
    if log_likelihood_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, log_likelihood failed these cases:\n" + "\n".join(_ll_failures))
    return (log_likelihood_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Finding the best time

    Now let's use your function on the **3rd codon positions** of the yeast gene.
    The first cell below creates a slider for adjusting the value of $t$.
    The second cell below counts the sites and differences, and then the plot shows
    the log-likelihood for many values of $t$.
    Drag the slider to move the red point along the curve.
    (**You do not need to edit the next two cells**)
    """)
    return


@app.cell
def _(mo):
    t_slider = mo.ui.slider(
        start = 0.2,
        stop = 1.5,
        step = 0.01,
        value = 0.2,
        label = "Time, $t$ (expected substitutions per site)",
        show_value = True,
    )
    return (t_slider,)


@app.cell
def _(log_likelihood_works, mo, site_sets, t_slider):
    # Make sure the `log_likelihood` function is working before proceeding
    mo.stop(
        not log_likelihood_works,
        mo.md("***Waiting — Get your `log_likelihood` function working first.***"),
    )

    _seq_1, _seq_2 = site_sets["3rd codon positions"]
    third_sites = 0
    third_differences = 0
    for _i in range(len(_seq_1)):
        if (_seq_1[_i] in BASES) and (_seq_2[_i] in BASES):
            third_sites += 1
            if _seq_1[_i] != _seq_2[_i]:
                third_differences += 1

    # Evaluate the log-likelihood at t = 0.001, 0.002, ..., 1.5
    _grid = [_i / 1000 for _i in range(1, 1501)]
    _curve = [log_likelihood(_t, third_sites, third_differences) for _t in _grid]

    # Find the value of t on the grid with the largest log-likelihood
    best_t = _grid[0]
    _best_ll = _curve[0]
    for _i in range(len(_grid)):
        if _curve[_i] > _best_ll:
            best_t = _grid[_i]
            _best_ll = _curve[_i]

    _slider_ll = log_likelihood(t_slider.value, third_sites, third_differences)

    _figure, _axes = plt.subplots(figsize = (7, 4))
    _axes.plot(_grid, _curve, color = "steelblue", linewidth = 2)
    _axes.scatter([t_slider.value], [_slider_ll], color = "firebrick", s = 60,
                  zorder = 3)
    _axes.set_xlim(0, 1.55)
    _axes.set_ylim(_best_ll - 100, _best_ll + 10)
    _axes.set_xlabel("Time, $t$ (expected substitutions per site)")
    _axes.set_ylabel("Log-likelihood")
    _axes.set_title(
        f"3rd codon positions: {third_differences} of {third_sites} sites differ"
    )

    mo.vstack([
        _figure,
        mo.md(
            f"At $t$ = {t_slider.value:.2f}, the log-likelihood is "
            + f"**{_slider_ll:.2f}**.  \n"
            + f"The best value of $t$ we found on the grid is **{best_t:.3f}**."
        ),
        t_slider
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 10: The maximum likelihood estimate </font>

    Double-click this cell and answer the questions below.

    1.  **Compare the best value of $t$ from the plot above to the Jukes-Cantor
        distance for the 3rd codon positions from Part 5.
        What do you notice?**

        **Answer**:

    2.  **For the simple Jukes-Cantor model, we have a distance formula, so we did
        not need to search for the best $t$.
        Why is it still worth knowing how to find the maximum likelihood estimate by
        searching?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 7: When the model is wrong

    In Challenge 8, you saw that transitions happen much more often than the
    Jukes-Cantor model assumes.
    In this section, we will explore what happens to the Jukes-Cantor distance when
    the model is wrong in this way.

    The function below is like your `get_different_base`, but it returns the
    transition partner of a base (`A` ↔ `G`, `C` ↔ `T`) 80% of the time, and one of
    the two transversions the rest of the time.
    **You do not need to edit it.**
    """)
    return


@app.function
def get_transition_biased_base(base, rng, transition_probability = 0.8):
    """Pick a different base, favoring the transition partner of `base`.

    Args:
        base (str): A single DNA base ("A", "C", "G", or "T").
        rng (random.Random): The random number generator to use.
        transition_probability (float): The probability of returning the
            transition partner (A <-> G, C <-> T). Otherwise, one of the two
            transversions is returned, each equally likely.

    Returns:
        str: A base that is different from `base`.
    """
    transition_partner = {"A": "G", "G": "A", "C": "T", "T": "C"}
    if rng.random() < transition_probability:
        return transition_partner[base]
    transversions = []
    for possible_base in BASES:
        if (possible_base != base) and (possible_base != transition_partner[base]):
            transversions.append(possible_base)
    return rng.choice(transversions)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 11: Making `evolve_one_step` transition-biased </font>

    In the cell below, write a new function called `evolve_one_step_biased` that is
    exactly like your `evolve_one_step`, except that it uses
    `get_transition_biased_base` instead of `get_different_base`.

    Your function must take the same three arguments as `evolve_one_step`
    (`sequence`, `rate`, and `rng`, in that order) and return the same two values
    (the new sequence and the number of substitutions), because `simulate_history`
    will call it the same way.

    /// tip
    Start by copying your `evolve_one_step` function (from the `def` line to the
    `return` line, including its docstring) into the cell below.
    Then make three changes:

    1.  Change the function's name to `evolve_one_step_biased`
    2.  Change the one function it calls, from `get_different_base` to
        `get_transition_biased_base`
    3.  Update the docstring so that it describes what your new function does
        (*e.g.*, that a substituted base usually changes by a transition), and
        update the example so that it calls `evolve_one_step_biased`
    ///

    /// note
    The line `evolve_one_step_biased = None` in the cell is a placeholder.
    It lets the rest of the notebook wait patiently until your function exists.
    Write your function **below** that line, and your `def` will replace the
    placeholder.
    ///
    """)
    return


@app.cell
def _():
    # A placeholder until you write your function (leave this line in place)
    evolve_one_step_biased = None

    # Write your evolve_one_step_biased function below
    return (evolve_one_step_biased,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(evolve_one_step_biased):
    def _run_biased_step(sequence, rate, rng):
        # Call the student's function, catching any error so we can report it
        try:
            return evolve_one_step_biased(sequence, rate, rng), None
        except Exception as error:
            return None, f"{type(error).__name__}: {error}"

    def _is_transition(base_1, base_2):
        return ({base_1, base_2} == {"A", "G"}) or ({base_1, base_2} == {"C", "T"})

    evolve_one_step_biased_works = False
    _messages = []
    _test_sequence = "ACGT" * 2500

    if evolve_one_step_biased is None:
        _messages.append(
            "You have not written your evolve_one_step_biased function yet."
        )
    else:
        _result, _error = _run_biased_step(_test_sequence, 0.0, random.Random(3))
        if _error is not None:
            _messages.append(f"Calling your function gave an error: {_error}")
        elif not (isinstance(_result, tuple) and len(_result) == 2):
            _messages.append(
                "Your function should return two values: the new sequence and "
                + "the number of substitutions."
            )
        else:
            evolve_one_step_biased_works = True

    if evolve_one_step_biased_works:
        # Test 1: With rate = 0, nothing should change
        _same, _same_count = _result
        if (_same != _test_sequence) or (_same_count != 0):
            evolve_one_step_biased_works = False
            _messages.append("With rate = 0, the sequence should not change at all.")

        # Test 2: With rate = 1, every base should change, mostly by transitions
        _all, _all_count = evolve_one_step_biased(_test_sequence, 1.0, random.Random(4))
        if (len(_all) != len(_test_sequence)) or (_all_count != len(_test_sequence)):
            evolve_one_step_biased_works = False
            _messages.append(
                "With rate = 1, every base should be substituted, and the new "
                + "sequence should be the same length as the old one."
            )
        else:
            _transitions = 0
            _unchanged = 0
            for _i in range(len(_all)):
                if _all[_i] == _test_sequence[_i]:
                    _unchanged += 1
                elif _is_transition(_all[_i], _test_sequence[_i]):
                    _transitions += 1
            _transition_fraction = _transitions / len(_all)
            print(f"rate = 1.0: {_all_count:,} substitutions, "
                  + f"{100 * _transition_fraction:.1f}% transitions")
            if _unchanged > 0:
                evolve_one_step_biased_works = False
                _messages.append(
                    "A substituted base should always change to a different base."
                )
            elif not (0.75 < _transition_fraction < 0.85):
                evolve_one_step_biased_works = False
                _messages.append(
                    "About 80% of substitutions should be transitions, but "
                    + f"{100 * _transition_fraction:.1f}% were. Are you using "
                    + "get_transition_biased_base?"
                )

        # Test 3: With rate = 0.1, about 10% of bases should change
        _some, _some_count = evolve_one_step_biased(
            _test_sequence, 0.1, random.Random(5)
        )
        print(f"rate = 0.1: {_some_count:,} substitutions")
        if not (850 < _some_count < 1150):
            evolve_one_step_biased_works = False
            _messages.append(
                f"With rate = 0.1, about 1,000 of 10,000 bases should change, but "
                + f"{_some_count:,} did."
            )

        # Test 4: The same seed should give the same result (uses rng, not random)
        _first = evolve_one_step_biased(_test_sequence, 0.5, random.Random(6))
        _second = evolve_one_step_biased(_test_sequence, 0.5, random.Random(6))
        if _first != _second:
            evolve_one_step_biased_works = False
            _messages.append(
                "Two generators with the same seed should give exactly the same "
                + "result. Make sure your function uses rng.random(), and passes "
                + "rng to get_transition_biased_base."
            )

    print()
    if evolve_one_step_biased_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your evolve_one_step_biased function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (evolve_one_step_biased_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 12: Simulating transition-biased evolution</font>

    The cell below currently creates two empty variables (value of `None`): `new_rng`
    and `biased_history`.
    Update the code in the cell below so that `new_rng` is a new random number
    generator (with any seed you like) and `biased_history` is the output of
    `simulate_history`.

    Use the same settings as our simulation in Part 3, so we can compare the
    results:

    -   Evolve the same `ancestor` sequence from Part 3
    -   `number_of_steps = 150`
    -   `rate = 0.01`
    -   `rng = new_rng` (your new random number generator)
    -   `record_every = 10`
    -   `step_function = evolve_one_step_biased` (your new function above)

    /// note
    The cell will wait to run until your `evolve_one_step_biased` function passes
    its tests. Leave the `mo.stop(...)` lines at the top of the cell in place.
    ///
    """)
    return


@app.cell
def _(evolve_one_step_biased_works, mo):
    # Wait until evolve_one_step_biased passes its tests (leave this in place)
    mo.stop(
        not evolve_one_step_biased_works,
        mo.md(
            "***Waiting — Get your `evolve_one_step_biased` function working "
            + "first.***"
        ),
    )

    # Replace the code below with code described above
    new_rng = None
    biased_history = None
    return (biased_history,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The code in the cell below creates a plot similar to the one we saw after
    Challenge 6.
    It will plot the Jukes-Cantor distance against the true number of substitutions
    per site over time from your simulation above.
    **You do not need to edit the next cell**.
    """)
    return


@app.cell
def _(ancestor, biased_history, jc_distance_works, mo, p_distance_works):
    # Using `mo.stop` to make sure the functions this plot uses are working
    mo.stop(
        not (p_distance_works and jc_distance_works),
        mo.md("***Waiting — Get `p_distance` and `jc_distance` working first.***"),
    )

    # Using `mo.stop` to make sure the simulation above was run before proceeding
    mo.stop(
        biased_history is None,
        mo.md("***Waiting — Get your simulation above working first.***"),
    )

    # Make sure `biased_history` looks like the output of `simulate_history`
    _looks_right = isinstance(biased_history, list) and (len(biased_history) > 1)
    if _looks_right:
        for _record in biased_history:
            if not (
                isinstance(_record, dict)
                and ("substitutions_per_site" in _record)
                and ("sequence" in _record)
            ):
                _looks_right = False
    mo.stop(
        not _looks_right,
        mo.md(
            "***Waiting — `biased_history` should be the list of records returned "
            + "by `simulate_history`. Check your code above.***"
        ),
    )

    # The code below plots the results of your simulation above
    # You do not need to edit it
    _true = [_record["substitutions_per_site"] for _record in biased_history]
    _jc = [jc_distance(p_distance(ancestor, _record["sequence"]))
           for _record in biased_history]

    _figure, _axes = plt.subplots(figsize = (6, 5))
    _axes.scatter(_true, _jc, color = "steelblue", s = 15,
                  label = "Jukes-Cantor distance")
    _max_true = max(_true)
    _axes.plot([0, _max_true], [0, _max_true], color = "gray", linestyle = "--",
               label = "Perfect estimate")
    _axes.set_xlabel("Substitutions per site that actually happened")
    _axes.set_ylabel("Jukes-Cantor distance")
    _axes.set_title("When transitions are more common than JC assumes")
    _axes.legend(loc = "upper left")
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 13: Interpreting the results </font>

    Double-click this cell and answer the question below.

    **Does the Jukes-Cantor distance overestimate or underestimate the true distance
    when transitions are more common than the model assumes? Why?**

    **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    -   A ***model of sequence evolution*** describes the probabilities of
        substitution; the Jukes-Cantor model is the simplest one
    -   It is a ***Markov chain***: What happens next depends only on the current
        base
    -   Counting observable differences **underestimates** evolution, because of
        ***multiple hits***, and observed differences ***saturate*** at 0.75
    -   The ***Jukes-Cantor distance*** corrects for the hidden substitutions, but it
        gets noisy near saturation and is infinite beyond it
    -   Real genes break the model's assumptions (*e.g.*, transitions are more common
        than transversions), which is why richer models exist
    -   The Jukes-Cantor distance is a ***maximum likelihood estimate***, and
        likelihood is how we will fit richer models and trees, where there is no
        simple formula
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

    The *SSA3* alignment and some of the ideas in this exercise are from the
    [Jupyter notebooks](https://github.com/fayjustin/computational_biology/tree/main/Labs)
    written by [Justin Fay](https://fayjustin.github.io/).
    I used Anthropic's Claude (Opus 5.5 model) to draft this notebook.
    """)
    return


if __name__ == "__main__":
    app.run()
