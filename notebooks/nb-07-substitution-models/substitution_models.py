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
    import math
    import random

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
    # Richer models of sequence evolution

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## When the model is wrong

    At the end of the last exercise, we simulated sequences in which most
    substitutions were transitions (`A` ↔ `G`, `C` ↔ `T`), like we saw in the yeast
    *SSA3* gene.
    The Jukes-Cantor (JC) model assumes all substitutions are equally likely, so
    the JC distance **underestimated** how much evolution had happened.

    In this exercise, we will try to fix that bias by building richer models of
    sequence evolution.
    Here's our plan:

    1.  Use the **K80 model** to correct for transition bias
    2.  Describe a model as a **table of rates**, and simulate evolution in
        **continuous time**, without tiny steps
    3.  See what happens when the four bases are **not equally common**
    4.  Use NumPy and SciPy to calculate the **transition probabilities**, $P(t)$,
        for any model
    5.  Use likelihood to ask **which model fits the yeast gene better**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: The K80 model

    Kimura (1980) proposed a model with **two** rates of substitution: One for
    transitions and one for transversions.
    We will use ***kappa*** ($\kappa$) to represent the ratio of the two rates:

    $$
    \kappa = \frac{\text{rate of each transition}}{\text{rate of each transversion}}
    $$

    When $\kappa = 1$, all changes are equally likely, and the K80 model is
    the JC model.
    The bigger $\kappa$ is, the faster transitions occur relative to transversions.

    Recall that the four bases come in two chemical types, the ***purines***
    (`A` and `G`) and the ***pyrimidines*** (`C` and `T`).
    A ***transition*** is a change within a type, and a ***transversion*** is a
    change between types.
    The function below tells you whether a change between two different bases is a
    transition.
    **You do not need to edit it.**
    """)
    return


@app.function
def is_transition(base_1, base_2):
    """Check whether a change between two different bases is a transition.

    Args:
        base_1 (str): A DNA base ("A", "C", "G", or "T").
        base_2 (str): A different DNA base.

    Returns:
        bool: True if both bases are purines (A, G) or both are pyrimidines
            (C, T); False otherwise.

    Examples:
        >>> is_transition("A", "G")
        True
        >>> is_transition("A", "C")
        False
    """
    purines = "AG"
    pyrimidines = "CT"
    both_purines = (base_1 in purines) and (base_2 in purines)
    both_pyrimidines = (base_1 in pyrimidines) and (base_2 in pyrimidines)
    return both_purines or both_pyrimidines


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 1: Counting transitions and transversions </font>

    Complete the `count_transitions_transversions` function below.
    Like `p_distance` in the last exercise, it should only compare sites where
    **both** sequences have one of the four bases, but now it returns three
    counts: the number of sites compared, the number of transitions, and the number
    of transversions.

    A recipe:

    1.  Loop over every index of `seq_1`
    2.  If both bases at that index are in `BASES`, add 1 to `number_compared`
    3.  If they are both in `BASES` **and** they differ, use `is_transition` to
        decide whether to add 1 to `number_of_transitions` or to
        `number_of_transversions`
    """)
    return


@app.function
def count_transitions_transversions(seq_1, seq_2):
    """Count the transition and transversion differences between two sequences.

    Only sites where both sequences have one of the four DNA bases are compared;
    gaps and ambiguous bases are skipped.

    Args:
        seq_1 (str): The first aligned sequence.
        seq_2 (str): The second aligned sequence, the same length as `seq_1`.

    Returns:
        tuple[int, int, int]: The number of sites compared, the number of
            those sites that differ by a transition, and the number that differ
            by a transversion.

    Examples:
        >>> count_transitions_transversions("ACGT", "GCAT")
        (4, 2, 0)
        >>> count_transitions_transversions("AC-T", "ACGA")
        (3, 0, 1)
    """
    number_compared = 0
    number_of_transitions = 0
    number_of_transversions = 0
    # Add your code here!

    return number_compared, number_of_transitions, number_of_transversions


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _count_test_cases = [
        (("ACGT", "ACGT"), (4, 0, 0)),
        (("ACGT", "GCAT"), (4, 2, 0)),
        (("ACGT", "CATG"), (4, 0, 4)),
        (("AAAA", "AGCT"), (4, 1, 2)),
        (("AC-TN", "GCATA"), (3, 1, 0)),
    ]
    _count_failures = []
    for (_seq_1, _seq_2), _expected in _count_test_cases:
        try:
            _found = count_transitions_transversions(_seq_1, _seq_2)
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
        if _found != _expected:
            _count_failures.append(
                f"  {_seq_1} vs {_seq_2}: expected {_expected}, got {_found}"
            )

    count_works = len(_count_failures) == 0
    if count_works:
        print("Yay, your function passed the test!")
    else:
        print(
            "Sorry, count_transitions_transversions failed these cases:\n"
            + "\n".join(_count_failures)
        )
    return (count_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 2: The K80 distance </font>

    If $S$ is the proportion of sites that differ by a transition and $V$ is the
    proportion that differ by a transversion, the K80 distance is:

    $$
    d = -\frac{1}{2}\ln\left(1 - 2S - V\right) - \frac{1}{4}\ln\left(1 - 2V\right)
    $$

    Like the JC distance, this is an estimate of the number of substitutions per
    site, including the ones we cannot see.
    And like the JC distance, it is undefined when the sequences are saturated, which
    here means when either $1 - 2S - V$ or $1 - 2V$ is zero or negative.

    Complete the `k80_distance` function below.
    A recipe:

    1.  Use your `count_transitions_transversions` function to get the three counts
    2.  Calculate `s` (the proportion of transitions) and `v` (the proportion of
        transversions) by dividing by the number of sites compared
    3.  If `1 - 2 * s - v` or `1 - 2 * v` is less than or equal to 0, set
        `distance` to `math.inf`
    4.  Otherwise, set `distance` using the equation above

    /// tip
    Python can "unpack" the three values a function returns into three variables
    at once, for example:
    `n, transitions, transversions = count_transitions_transversions(seq_1, seq_2)`
    ///
    """)
    return


@app.function
def k80_distance(seq_1, seq_2):
    """Estimate the number of substitutions per site under the K80 model.

    Args:
        seq_1 (str): The first aligned sequence.
        seq_2 (str): The second aligned sequence, the same length as `seq_1`.

    Returns:
        float: The K80 distance, or `math.inf` if the sequences are saturated.

    Examples:
        >>> k80_distance("ACGT", "ACGT")
        0.0
        >>> k80_distance("AAAA", "CTCT")
        inf
    """
    distance = 0.0
    # Add your code here!

    return distance + 0.0


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(count_works):
    _k80_test_cases = [
        (("ACGT", "ACGT"), 0.0),
        (("A" * 20, "GG" + "C" + "A" * 17), 0.170181),
        (("A" * 10, "G" + "A" * 9), 0.111572),
        (("AAAA", "CTCT"), math.inf),
        (("AAAA", "GGGA"), math.inf),
    ]
    _k80_failures = []
    for (_seq_1, _seq_2), _expected in _k80_test_cases:
        try:
            _found = k80_distance(_seq_1, _seq_2)
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
        if _expected == math.inf:
            _ok = _found == math.inf
        else:
            _ok = isinstance(_found, float) and abs(_found - _expected) < 1e-5
        if not _ok:
            _k80_failures.append(
                f"  {_seq_1} vs {_seq_2}: expected {_expected}, got {_found}"
            )

    k80_distance_works = count_works and (len(_k80_failures) == 0)
    if not count_works:
        print("Get count_transitions_transversions working first!")
    elif k80_distance_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, k80_distance failed these cases:\n" + "\n".join(_k80_failures))
    return (k80_distance_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Estimating $\kappa$

    Kimura also showed how to estimate $\kappa$ from the same two proportions.
    The function below does that for you, along with the JC distance from the last
    exercise.
    **You do not need to edit these functions.**
    """)
    return


@app.function
def estimate_kappa(seq_1, seq_2):
    """Estimate the transition/transversion rate ratio (kappa) under K80.

    Args:
        seq_1 (str): The first aligned sequence.
        seq_2 (str): The second aligned sequence, the same length as `seq_1`.

    Returns:
        float: The estimate of kappa, or `math.inf` if it cannot be estimated
            (no transversions, or saturated sequences).
    """
    n, transitions, transversions = count_transitions_transversions(seq_1, seq_2)
    s = transitions / n
    v = transversions / n
    if (v == 0) or ((1 - 2 * s - v) <= 0) or ((1 - 2 * v) <= 0):
        return math.inf
    return (2 * math.log(1 - 2 * s - v) / math.log(1 - 2 * v)) - 1


@app.function
def jc_distance(p):
    """Convert a p-distance into a Jukes-Cantor (JC69) distance."""
    if p >= 0.75:
        return math.inf
    return -0.75 * math.log(1 - ((4 / 3) * p))


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Back to the simulation from last time

    The next two cells repeat the transition-biased simulation from the end of the last
    exercise:
    The same 1,000-base ancestor, evolved for 150 steps with a rate of 0.01, where
    80% of substitutions are transitions.
    It then compares the JC and K80 distances to the number of substitutions that
    actually happened.
    **You do not need to edit the next two cells**, but you will use the results of
    the simulation to answer questions in Challenge 3.
    """)
    return


@app.function
def simulate_biased_history(ancestor, number_of_steps, rate, rng, record_every):
    """The transition-biased simulation from the last exercise.

    Each step, each base is substituted with probability `rate`; a substituted
    base becomes its transition partner 80% of the time, and one of the two
    transversions otherwise.

    Returns:
        list[dict]: Records with the keys "substitutions_per_site" and
            "sequence".
    """
    transition_partner = {"A": "G", "G": "A", "C": "T", "T": "C"}
    sequence = ancestor
    total_substitutions = 0
    history = []
    for step in range(1, number_of_steps + 1):
        new_sequence = ""
        for base in sequence:
            if rng.random() < rate:
                total_substitutions += 1
                if rng.random() < 0.8:
                    new_sequence += transition_partner[base]
                else:
                    transversions = []
                    for other in BASES:
                        if (other != base) and (other != transition_partner[base]):
                            transversions.append(other)
                    new_sequence += rng.choice(transversions)
            else:
                new_sequence += base
        sequence = new_sequence
        if step % record_every == 0:
            history.append({
                "substitutions_per_site": total_substitutions / len(ancestor),
                "sequence": sequence,
            })
    return history


@app.cell
def _(k80_distance_works, mo):
    mo.stop(
        not k80_distance_works,
        mo.md("***Waiting — Get your `k80_distance` function working first.***"),
    )

    # The same ancestor and seeds as the last exercise
    _rng = random.Random(1969)
    biased_ancestor = ""
    for _ in range(1000):
        biased_ancestor += _rng.choice(BASES)
    _history = simulate_biased_history(
        biased_ancestor,
        number_of_steps = 150,
        rate = 0.01,
        rng = random.Random(1980),
        record_every = 10,
    )

    _true = []
    _jc = []
    _k80 = []
    _kappa = []
    for _record in _history:
        _n, _ts, _tv = count_transitions_transversions(
            biased_ancestor, _record["sequence"]
        )
        _true.append(_record["substitutions_per_site"])
        _jc.append(jc_distance((_ts + _tv) / _n))
        _k80.append(k80_distance(biased_ancestor, _record["sequence"]))
        _kappa.append(estimate_kappa(biased_ancestor, _record["sequence"]))

    _figure, _axes = plt.subplots(figsize = (6, 5))
    _axes.scatter(_true, _jc, color = "steelblue", s = 15, label = "JC distance")
    _axes.scatter(_true, _k80, color = "darkorange", s = 15, label = "K80 distance")
    _axes.plot([0, max(_true)], [0, max(_true)], color = "gray", linestyle = "--",
               label = "Perfect estimate")
    _axes.set_xlabel("Substitutions per site that actually happened")
    _axes.set_ylabel("Estimated distance")
    _axes.set_title("Transition-biased simulation")
    _axes.legend(loc = "upper left")

    _rows = []
    for _i in range(2, len(_true), 3):
        _rows.append(
            f"| {_true[_i]:.2f} | {_jc[_i]:.2f} | {_k80[_i]:.2f} | {_kappa[_i]:.1f} |"
        )
    _table = mo.md(
        "| True | JC | K80 | Estimated $\\kappa$ |\n"
        + "|--:|--:|--:|--:|\n"
        + "\n".join(_rows)
    )
    mo.hstack([_figure, _table], align = "center")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Back to the yeast gene

    Now let's compare the JC and K80 distances for the yeast *SSA3* gene from the
    last exercise.
    The `parse_fasta_url` function is the one from our previous notebooks.
    **You do not need to edit the next cell.**
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell downloads and parses the yeast *SSA3* sequence data (**you don't
    need to edit it**).
    It stores the data in a dictionary called "`site_sets`" as the sites from the
    whole gene and only the sites from each of the three codon positions.
    Please read the code and try to understand what it is doing.
    """)
    return


@app.cell
def _():
    ssa3_url = (
        "https://raw.githubusercontent.com/phyletica/intro-to-comp-bio/"
        + "refs/heads/main/notebooks/data/SSA3.fasta"
    )
    ssa3_sequences = parse_fasta_url(ssa3_url)
    eubayanus = ssa3_sequences["Seub_SSA3"]
    paradoxus = ssa3_sequences["Spar_SSA3"]

    site_sets = {
        "Whole gene": (eubayanus, paradoxus),
        "1st codon positions": (eubayanus[0::3], paradoxus[0::3]),
        "2nd codon positions": (eubayanus[1::3], paradoxus[1::3]),
        "3rd codon positions": (eubayanus[2::3], paradoxus[2::3]),
    }
    return (site_sets,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell calculates the JC and K80 distances for each codon position and the
    whole gene, and estimates $\kappa$ (the ratio of the rates of transitions to
    transversions).
    These are then summarized in a markdown-formatted table so that they are easy
    for us to read.
    **You don't need to edit the next cell**.
    """)
    return


@app.cell
def _(k80_distance_works, mo, site_sets):
    mo.stop(
        not k80_distance_works,
        mo.md("***Waiting — Get your `k80_distance` function working first.***"),
    )

    _rows = []
    for _label in site_sets:
        _seq_1, _seq_2 = site_sets[_label]
        _n, _ts, _tv = count_transitions_transversions(_seq_1, _seq_2)
        _rows.append(
            f"| {_label} | {jc_distance((_ts + _tv) / _n):.3f} "
            + f"| {k80_distance(_seq_1, _seq_2):.3f} "
            + f"| {estimate_kappa(_seq_1, _seq_2):.1f} |"
        )

    mo.md(
        "| Sites | JC distance | K80 distance | Estimated $\\kappa$ |\n"
        + "|:--|--:|--:|--:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 3: Is K80 an improvement? </font>

    Double-click this cell and answer the questions below.

    1.  **In the simulation, how do the JC and K80 distances compare to the number
        of substitutions that actually happened?
        Is the K80 distance perfect?**

        **Answer**:

    2.  **The simulation made transitions 80% of substitutions, and *each of the
        two* transversions 10%.
        What value of $\kappa$ does that correspond to, and how close are the
        estimates of $\kappa$ from the simulated data (*i.e.*, two tables up)?**

        **Answer**:

    3.  **For the yeast gene, for which sites does the K80 correction change the
        distance the most? What does the estimate of $\kappa$ say about the
        3rd codon positions?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 2: Evolution in continuous time

    ## A model is a table of rates

    In the last exercise, we chopped time into tiny steps.
    Instead, we can describe a model by the ***rate*** of each possible change:
    How often, per unit of time, a base changes into each of the other three.

    The function below builds a table of rates (a dictionary of dictionaries) for the
    K80 model, with an option for unequal base frequencies that we will use in
    Part 3.
    `rates["A"]["G"]` is the rate at which an `A` changes to a `G`.
    The rates are scaled so that, on average, a site has one substitution per unit
    of time, so time is still measured in expected substitutions per site.
    **You do not need to edit this function**.
    """)
    return


@app.function
def make_rate_table(kappa = 1.0, base_frequencies = None):
    """Build a table of substitution rates for the K80 or HKY model.

    The rate of change from base i to base j is proportional to the frequency
    of base j, times kappa if the change is a transition. The rates are scaled
    so that the expected number of substitutions per unit time is 1.

    Args:
        kappa (float): The transition/transversion rate ratio. With kappa = 1
            and equal base frequencies, this is the JC model.
        base_frequencies (dict[str, float]): The frequency of each base, which
            must sum to 1. If None, all four bases have frequency 0.25.

    Returns:
        dict[str, dict[str, float]]: `rates[i][j]` is the rate at which base i
            changes to base j (for i != j).

    Examples:
        >>> make_rate_table()["A"]["C"]
        0.3333333333333333
    """
    if base_frequencies is None:
        base_frequencies = {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}
    rates = {}
    for from_base in BASES:
        rates[from_base] = {}
        for to_base in BASES:
            if from_base != to_base:
                rate = base_frequencies[to_base]
                if is_transition(from_base, to_base):
                    rate = rate * kappa
                rates[from_base][to_base] = rate
    # Scale the rates so there is 1 expected substitution per unit of time
    average_rate = 0.0
    for from_base in BASES:
        total_rate_out = 0.0
        for to_base in rates[from_base]:
            total_rate_out += rates[from_base][to_base]
        average_rate += base_frequencies[from_base] * total_rate_out
    for from_base in BASES:
        for to_base in rates[from_base]:
            rates[from_base][to_base] = rates[from_base][to_base] / average_rate
    return rates


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `rate_table_to_markdown` function below takes a rate table returned by the
    `make_rate_table` function above and creates a markdown-formatted table that is
    easy for us to read.
    **You do not need to edit the next cell**.
    """)
    return


@app.function
def rate_table_to_markdown(rates):
    """Render a table of rates as a Markdown table."""
    lines = [
        "| From \\ To | " + " | ".join(f"**{b}**" for b in BASES) + " |",
        "|:-:|" + ":-:|" * len(BASES),
    ]
    for from_base in BASES:
        cells = []
        for to_base in BASES:
            if from_base == to_base:
                cells.append("—")
            else:
                cells.append(f"{rates[from_base][to_base]:.3f}")
        lines.append(f"| **{from_base}** | " + " | ".join(cells) + " |")
    return "\n".join(lines)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In the next cell, we use our `make_rate_table` function to create a table of
    rates for the JC and K80 models.
    **You do not need to edit this cell**, but the two tables printed below it
    are worth a careful look.
    """)
    return


@app.cell
def _(mo):
    jc_rates = make_rate_table()
    k80_rates = make_rate_table(kappa = 8)

    print("Here's what the JC rates look like to Python:")
    print("{")
    for _from_base in jc_rates:
        print(f"  {_from_base!r} : {jc_rates[_from_base]},")
    print("}")
    print()

    print("Here's what the K80 rates (kappa = 8) look like to Python:")
    print("{")
    for _from_base in k80_rates:
        print(f"  {_from_base!r} : {k80_rates[_from_base]},")
    print("}")

    mo.hstack([
        mo.vstack([
            mo.md("**JC rate table**"),
            mo.md("(`make_rate_table()`)"),
            mo.md(rate_table_to_markdown(jc_rates)),
        ]),
        mo.vstack([
            mo.md("**K80 rate table, $\\kappa = 8$**"),
            mo.md("(`make_rate_table(kappa = 8)`)"),
            mo.md(rate_table_to_markdown(k80_rates)),
        ]),
    ], justify = "space-around")
    return jc_rates, k80_rates


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In both tables, every row adds up to 1: Each base changes at a total rate of 1
    substitution per unit of time.
    The models only differ in **where** a base goes when it changes.
    Under JC, each of the other three bases is equally likely, and under K80 with
    $\kappa = 8$, the transition change gets 8 times the rate of each transversion
    (0.8 versus 0.1).

    ## Waiting for the next substitution

    If a base changes at a total rate of $\lambda$ per unit time, how long do we
    wait for the next substitution?
    The answer is random, and follows an ***exponential distribution*** with an
    average waiting time of $1 / \lambda$.
    Our random number generators can draw waiting times to the next substitution with
    `rng.expovariate(rate)`.

    The exponential distribution is ***memoryless***:
    No matter how long a site has already waited, the time until its next
    substitution has the same exponential distribution.
    That is the memoryless property of Markov chains from the last exercise, now in
    continuous time.

    To get a sense of exponential distributions of waiting times,
    the next cell draws 10,000 waiting times at two different substitution rates and
    plots both as a histogram.
    Notice, when we double the rate, we halve the waiting time, on average.
    Also notice, there is a lot of variation in waiting times under both rates!
    **You do not need to edit the next cell**.
    """)
    return


@app.cell
def _():
    _rng = random.Random(42)
    _figure, _axes = plt.subplots(figsize = (7, 4))
    for _rate in [1.0, 2.0]:
        _waits = []
        for _ in range(10_000):
            _waits.append(_rng.expovariate(_rate))
        _mean_wait = sum(_waits) / len(_waits)
        _axes.hist(_waits, bins = 60, range = (0, 5), alpha = 0.6,
                   label = f"rate = {_rate}, average wait = {_mean_wait:.3f}")
    _axes.set_xlabel("Waiting time until the next substitution")
    _axes.set_ylabel("Number of draws")
    _axes.set_title("Exponential waiting times")
    _axes.legend()
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 4: Simulating a site in continuous time </font>

    Now, we can simulate a site without any time steps.
    Starting from a base, we repeat three things:

    1.  Find the **total rate** of leaving the current base (the sum of its row of
        the rate table)
    2.  Draw a **waiting time** until the next substitution from an exponential
        distribution with that rate, and add it to a `clock` variable
    3.  If the clock has gone past the time `t` we were asked to simulate, stop.
        Otherwise, choose the **new base**, with each possible base chosen in
        proportion to its rate in the rate table

    The function below already has the loop, the clock, and the check for when to
    stop.
    Replace each of the three `None`s (`total_rate`, `waiting_time`, and
    `new_base`) with code that does what the comment above it says.

    /// tip
    1.  `rates[base]` is the dictionary of rates out of the current base, so
        `rates[base].values()` are the rates, and you can use the `sum()` function
        to add them up
    2.  `rng.expovariate(total_rate)` draws a random waiting time
    3.  `rng.choices(options, weights = rates)` picks from a list of `options`, each
        in proportion to its weight, and returns a **list** containing **one**
        choice, so add `[0]` at the end to get the choice itself.
        For example, `rng.choices(["A", "G"], weights = [1, 3])[0]` returns `"G"`
        three times as often as `"A"`.
        The options you need are `list(rates[base].keys())` and the weights are
        `list(rates[base].values())`.
    ///

    /// warning
    Leave the two checks in the function in place:
    `if not (waiting_time >= 0):`
    and
    `if number_of_substitutions > 1_000_000:`.
    If there's a mistake in your waiting time (for example, if it is always zero or
    negative), these checks stop the function with an error, instead of letting it
    loop forever and freeze your notebook.
    ///
    """)
    return


@app.function
def simulate_site(start_base, t, rates, rng):
    """Simulate the evolution of one site for time `t` in continuous time.

    Args:
        start_base (str): The base at time 0.
        t (float): How long to evolve the site, in expected substitutions per
            site.
        rates (dict[str, dict[str, float]]): A table of rates, as returned by
            `make_rate_table`.
        rng (random.Random): The random number generator to use.

    Returns:
        tuple[str, int]: The base at time `t`, and the number of substitutions
            that happened.

    Examples:
        >>> simulate_site("A", 0.0, make_rate_table(), random.Random(1))
        ('A', 0)
    """
    base = start_base
    clock = 0.0
    number_of_substitutions = 0
    while True:
        # 1. Replace `None` with the total rate of leaving the current base
        total_rate = None
        # 2. Replace `None` with a random waiting time until the next substitution
        waiting_time = None
        if not (waiting_time >= 0):
            raise ValueError("The waiting time cannot be negative.")
        clock += waiting_time
        if clock > t:
            break
        # 3. Replace `None` with the new base, chosen in proportion to the rates
        new_base = None
        base = new_base
        number_of_substitutions += 1
        if number_of_substitutions > 1_000_000:
            raise RuntimeError(
                "Too many substitutions! Is your waiting time always 0?"
            )
    return base, number_of_substitutions


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(jc_rates, k80_rates):
    def _run_site(start_base, t, rates, rng):
        # Call the student's function, catching any error so we can report it
        try:
            return simulate_site(start_base, t, rates, rng), None
        except Exception as _error:
            return None, f"{type(_error).__name__}: {_error}"

    simulate_site_works = True
    _messages = []

    # Test 1: No time, no change
    _result, _error = _run_site("A", 0.0, jc_rates, random.Random(1))
    if _error is not None:
        simulate_site_works = False
        _messages.append(f"Calling your function gave an error: {_error}")
    elif _result != ("A", 0):
        simulate_site_works = False
        _messages.append(f"With t = 0, the result should be ('A', 0), not {_result}.")

    if simulate_site_works:
        try:
            # Test 2: Under JC at t = 1, about 44.8% of sites still match, and the
            # average number of substitutions per site is about 1
            _rng = random.Random(2)
            _matches = 0
            _substitutions = 0
            for _ in range(4000):
                _base, _count = simulate_site("A", 1.0, jc_rates, _rng)
                if _base == "A":
                    _matches += 1
                _substitutions += _count
            _match_fraction = _matches / 4000
            _mean_substitutions = _substitutions / 4000
            print(f"JC, t = 1: {_match_fraction:.3f} of sites are still A "
                  + f"(expected 0.448), {_mean_substitutions:.3f} substitutions per site "
                  + "(expected 1)")
            if not (0.41 < _match_fraction < 0.49):
                simulate_site_works = False
                _messages.append(
                    "Under JC at t = 1, about 44.8% of sites should still be A."
                )
            if not (0.92 < _mean_substitutions < 1.08):
                simulate_site_works = False
                _messages.append(
                    "At t = 1, there should be about 1 substitution per site."
                )

            # Test 3: Under K80 (kappa = 8) at t = 0.5, the end states should follow
            # the rates (G should be far more common than C or T)
            _rng = random.Random(3)
            _ends = {"A": 0, "C": 0, "G": 0, "T": 0}
            for _ in range(4000):
                _ends[simulate_site("A", 0.5, k80_rates, _rng)[0]] += 1
            _fractions = {_b: _ends[_b] / 4000 for _b in BASES}
            _expected = {"A": 0.656, "C": 0.045, "G": 0.252, "T": 0.045}
            print("K80, t = 0.5: end states "
                  + ", ".join(f"{_b} {_fractions[_b]:.3f}" for _b in BASES)
                  + " (expected "
                  + ", ".join(f"{_b} {_expected[_b]:.3f}" for _b in BASES) + ")")
            for _b in BASES:
                if abs(_fractions[_b] - _expected[_b]) > 0.035:
                    simulate_site_works = False
                    _messages.append(
                        "Under K80, the new base should be chosen in proportion to "
                        + "its rate. Are you using the rates as weights?"
                    )
                    break

            # Test 4: The same seed should give the same results
            _rng_1 = random.Random(4)
            _rng_2 = random.Random(4)
            _first = [simulate_site("A", 2.0, k80_rates, _rng_1) for _ in range(20)]
            _second = [simulate_site("A", 2.0, k80_rates, _rng_2) for _ in range(20)]
            if _first != _second:
                simulate_site_works = False
                _messages.append("Make sure every random draw uses rng.")

        except Exception as _error:
            simulate_site_works = False
            _messages.append(
                f"Calling your function gave an error: {type(_error).__name__}: {_error}"
            )
            if isinstance(_error, KeyError) and (_error.args == (None,)):
                _messages.append(
                    "The base became None. Did you replace the None in "
                    + "`new_base = None`?"
                )

    print()
    if simulate_site_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your simulate_site function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (simulate_site_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Below is our `jc_prob_different` function from our last exercise (**you don't
    need to edit it**).
    We will use it for plotting in the next Python cell.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below uses your `simulate_site` function to evolve 2,000 sites that
    start as `A` under the JC model, for a range of times, and compares the fraction
    that are still `A` to the JC prediction from the last exercise,
    $\frac{1}{4} + \frac{3}{4}e^{-\frac{4}{3}t}$.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(jc_rates, mo, simulate_site_works):
    mo.stop(
        not simulate_site_works,
        mo.md("***Waiting — Get your `simulate_site` function working first.***"),
    )

    _rng = random.Random(2026)
    _times = [_i / 4 for _i in range(0, 13)]
    _simulated = []
    _mean_substitutions = []
    for _t in _times:
        _matches = 0
        _total = 0
        for _ in range(2000):
            _base, _count = simulate_site("A", _t, jc_rates, _rng)
            if _base == "A":
                _matches += 1
            _total += _count
        _simulated.append(_matches / 2000)
        _mean_substitutions.append(_total / 2000)

    _curve_t = [_i / 100 for _i in range(0, 301)]
    _figure, _axes = plt.subplots(figsize = (7, 4))
    _axes.scatter(_times, _simulated, color = "black", zorder = 3,
                  label = "Continuous-time simulation")
    _axes.plot(_curve_t, [1.0 - jc_prob_different(_t) for _t in _curve_t],
               color = "steelblue", linewidth = 2, label = "JC prediction")
    _axes.axhline(0.25, color = "gray", linestyle = ":", linewidth = 1)
    _axes.set_xlabel("Time, $t$ (expected substitutions per site)")
    _axes.set_ylabel("Fraction of sites still A")
    _axes.set_ylim(0, 1.05)
    _axes.legend()

    _rows = [f"| {_t:.2f} | {_m:.3f} |"
             for _t, _m in zip(_times[::2], _mean_substitutions[::2])]
    _table = mo.md("| $t$ | Substitutions per site |\n|--:|--:|\n" + "\n".join(_rows))
    mo.hstack([_figure, _table], align = "center")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 5: Evolution without discrete steps </font>

    Double-click this cell and answer the questions below.

    1.  **How does your continuous-time simulation compare to the JC prediction?
        How does the average number of substitutions per site compare to $t$?**

        **Answer**:

    2.  **After each substitution, your function draws a brand new waiting time,
        without keeping track of how long the site had been waiting. Why is that
        OK?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 3: When bases are not equally common

    The JC and K80 models assume all four bases are equally common (25% each).
    Many genomes don't follow this assumption.
    Some are rich in `G` and `C`, and others are rich in `A` and `T`.
    The HKY model (Hasegawa, Kishino, and Yano, 1985) adds a frequency for each base,
    $\pi_A$, $\pi_C$, $\pi_G$, and $\pi_T$.
    The rate of change **to** a base is proportional to its frequency, so common bases
    are gained more often.

    Let's use our `make_rate_table` function to build a substitution model that
    assumes a GC-rich genome (40% each of `C` and `G`, 10% each of `A` and `T`).
    **You don't need to edit the next cell**, but you should understand what it is
    doing.
    """)
    return


@app.cell
def _():
    gc_rich_frequencies = {"A": 0.1, "C": 0.4, "G": 0.4, "T": 0.1}
    gc_rich_rates = make_rate_table(kappa = 1.0,
                                    base_frequencies = gc_rich_frequencies)
    return gc_rich_frequencies, gc_rich_rates


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below uses our new `gc_rich_rates` model and your `simulate_site`
    function for two experiments:

    1.  Evolve 2,000 sites that all start as `A`, and track the fraction of each
        base over time
    2.  Draw a 2,000-base ancestor with these base frequencies, evolve it, and track
        the p-distance between the ancestor and its descendant

    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(gc_rich_frequencies, gc_rich_rates, mo, simulate_site_works):
    mo.stop(
        not simulate_site_works,
        mo.md("***Waiting — Get your `simulate_site` function working first.***"),
    )

    _rng = random.Random(1985)
    _times = [_i / 2 for _i in range(0, 11)]

    # Experiment 1: sites that start as A
    _fractions = {_b: [] for _b in BASES}
    for _t in _times:
        _counts = {_b: 0 for _b in BASES}
        for _ in range(2000):
            _counts[simulate_site("A", _t, gc_rich_rates, _rng)[0]] += 1
        for _b in BASES:
            _fractions[_b].append(_counts[_b] / 2000)

    # Experiment 2: an ancestor with GC-rich base frequencies
    _ancestor = _rng.choices(
        BASES, weights = [gc_rich_frequencies[_b] for _b in BASES], k = 2000
    )
    _p_distances = []
    for _t in _times:
        _differences = 0
        for _base in _ancestor:
            if simulate_site(_base, _t, gc_rich_rates, _rng)[0] != _base:
                _differences += 1
        _p_distances.append(_differences / 2000)

    _figure, (_axes_1, _axes_2) = plt.subplots(1, 2, figsize = (11, 4))
    for _b in BASES:
        _axes_1.plot(_times, _fractions[_b], marker = "o", label = _b)
    _axes_1.set_xlabel("Time, $t$")
    _axes_1.set_ylabel("Fraction of sites")
    _axes_1.set_title("Sites that started as A")
    _axes_1.legend()

    _axes_2.plot(_times, _p_distances, marker = "o", color = "black",
                 label = "p-distance")
    _axes_2.axhline(0.75, color = "firebrick", linestyle = ":", label = "0.75")
    _axes_2.set_xlabel("Time, $t$")
    _axes_2.set_ylabel("p-distance")
    _axes_2.set_ylim(0, 1)
    _axes_2.set_title("Ancestor vs. descendant")
    _axes_2.legend(loc = "lower right")
    _figure.tight_layout()
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 6: Different equilibrium frequencies </font>

    Double-click this cell and answer the questions below.

    1.  **In the left plot, what fraction of sites end up as each base?
        How is this different from the JC model in the last exercise, and why?**

        **Answer**:

    2.  **In the right plot, the p-distance plateaus well below 0.75.
        At what value, roughly?
        Explain why.
        (Hint: After a long time, the descendant's base at a site is a random draw
        from $\pi$. What is the probability that two random draws match?)**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 4: Transition probabilities with NumPy and SciPy

    Simulation tells us what *can* happen.
    To calculate likelihoods, we need the **probability** of each outcome.
    If a site starts as base $i$, what is the probability that it is
    base $j$ after time $t$?
    We call this $P_{ij}(t)$.
    For JC, we had a formula.
    For richer models, the formulas quickly get complicated (and for the most general
    models, there isn't a simple formula at all), so we let the computer do the
    math.

    ## The rate matrix, $Q$

    First, we write the table of rates as a 4-by-4 grid of numbers called the
    ***rate matrix***, $Q$.
    Rows are the base now, columns are the base it changes to, in the order
    `A`, `C`, `G`, `T`.
    The off-diagonal entries are the rates from our rate table.
    Each **diagonal** entry is **minus** the total rate of leaving that base (the
    `total_rate` in your `simulate_site` function), so every row of $Q$ adds up to
    zero.
    For example, the JC rate matrix is:

    $$
    Q = \begin{bmatrix}
    -1 & \frac{1}{3} & \frac{1}{3} & \frac{1}{3} \\
    \frac{1}{3} & -1 & \frac{1}{3} & \frac{1}{3} \\
    \frac{1}{3} & \frac{1}{3} & -1 & \frac{1}{3} \\
    \frac{1}{3} & \frac{1}{3} & \frac{1}{3} & -1
    \end{bmatrix}
    $$

    ### NumPy arrays

    ***NumPy*** is the standard Python package for working with grids of numbers
    (called ***arrays***).
    It was imported for you as `np` at the top of this notebook.
    Here are some basics for how to create and work with NumPy arrays:

    ```python
    Q = np.zeros((4, 4)) # Create a 4-by-4 array of zeros
    Q[0, 2] = 0.5        # Set row 0, column 2 (A -> G) to 0.5
    Q[0, 2]              # Get the value of row 0, column 2
    Q * 2.0              # Create a new array equal to every entry in Q multiplied by 2
    ```

    ## <font color=red> Challenge 7: Building the rate matrix </font>

    Complete the `get_rate_matrix` function below, which converts a table of rates
    into a NumPy rate matrix.
    A recipe:

    1.  Write a **nested loop** over row index `i` and column index `j`, both in
        `range(4)`
    2.  Inside the loops, if `i` is not equal to `j`, set `rate_matrix[i, j]` to
        `rates[BASES[i]][BASES[j]]`, and add that rate to `total_rate`
    3.  After the inner loop (but still inside the outer loop), set the diagonal
        entry, `rate_matrix[i, i]`, to `-total_rate`

    /// warning
    `total_rate` is the total rate of leaving **one** base, so it has to start
    over at 0 for every row.
    Set `total_rate = 0.0` at the start of the outer loop, before the inner loop.
    ///
    """)
    return


@app.function
def get_rate_matrix(rates):
    """Convert a table of rates into a rate matrix (a NumPy array).

    Args:
        rates (dict[str, dict[str, float]]): A table of rates, as returned by
            `make_rate_table`.

    Returns:
        numpy.ndarray: A 4-by-4 array with rows and columns in the order of
            `BASES` ("ACGT"). Off-diagonal entries are the rates, and each
            diagonal entry is minus the sum of the other entries in its row.

    Examples:
        >>> float(get_rate_matrix(make_rate_table())[0, 0])
        -1.0
    """
    rate_matrix = np.zeros((4, 4))
    # Add your code here!
    return rate_matrix


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(gc_rich_rates, jc_rates, k80_rates):
    _expected_jc = np.array([
        [-1.0, 1 / 3, 1 / 3, 1 / 3],
        [1 / 3, -1.0, 1 / 3, 1 / 3],
        [1 / 3, 1 / 3, -1.0, 1 / 3],
        [1 / 3, 1 / 3, 1 / 3, -1.0],
    ])
    _expected_k80 = np.array([
        [-1.0, 0.1, 0.8, 0.1],
        [0.1, -1.0, 0.1, 0.8],
        [0.8, 0.1, -1.0, 0.1],
        [0.1, 0.8, 0.1, -1.0],
    ])
    get_rate_matrix_works = True
    for _label, _rates, _expected in [
        ("JC", jc_rates, _expected_jc),
        ("K80 (kappa = 8)", k80_rates, _expected_k80),
    ]:
        try:
            _found = get_rate_matrix(_rates)
            _ok = np.allclose(_found, _expected)
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
            _ok = False
        if not _ok:
            get_rate_matrix_works = False
            print(f"Sorry, for the {_label} model, get_rate_matrix should return")
            print(np.round(_expected, 3))
            print("but it returned")
            print(_found if isinstance(_found, str) else np.round(_found, 3))
            print()

    # Every row of any rate matrix should sum to zero
    if get_rate_matrix_works:
        _gc_matrix = get_rate_matrix(gc_rich_rates)
        if not np.allclose(_gc_matrix.sum(axis = 1), 0.0):
            get_rate_matrix_works = False
            print("Sorry, every row of a rate matrix should add up to 0.")

    if get_rate_matrix_works:
        print("Yay, your function passed the test!")
    else:
        print("Please try again!")
    return (get_rate_matrix_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## From rates to probabilities: $P(t) = e^{Qt}$

    Remember, we want the matrix of transition probabilities for looking up the
    probability of a site that starts as base $i$ ending up as base $j$ after time
    $t$.
    To get this matrix of transition probabilities for a given time $t$ we use:

    $$
    P(t) = e^{Qt}
    $$

    This is the ***matrix exponential***, a version of $e^x$ for matrices.
    You do not need to know how to calculate it by hand, because the
    ***SciPy*** package has a function for it, `expm` (already imported for you).
    `expm(Q * t)` returns a 4-by-4 NumPy array, $P(t)$, where row $i$, column $j$ is
    the probability that a site that starts as base $i$ is base $j$ after time $t$.

    For the JC model, $e^{Qt}$ gives exactly the formula we used in the last
    exercise.
    For richer models of sequence evolution, it gives us the transition
    probabilities that would be hard (or impossible) to write down "by hand."

    ## <font color=red> Challenge 8: Calculating $P(t)$ </font>

    Complete the `get_transition_probabilities` function below so that it returns
    $P(t) = e^{Qt}$, using `expm`.
    This takes only one line of code!
    """)
    return


@app.function
def get_transition_probabilities(rate_matrix, t):
    """Calculate the transition probability matrix P(t) = e^(Qt).

    Args:
        rate_matrix (numpy.ndarray): A 4-by-4 rate matrix, as returned by
            `get_rate_matrix`.
        t (float): Time, in expected substitutions per site.

    Returns:
        numpy.ndarray: A 4-by-4 array where row i, column j is the probability
            that a site that starts as base i is base j after time t.

    Examples:
        >>> P = get_transition_probabilities(get_rate_matrix(make_rate_table()), 0.0)
        >>> float(P[0, 0])
        1.0
    """
    # Replace the next line of code with your code for calculating P(t)!
    transition_probabilities = np.zeros((4, 4))

    return transition_probabilities


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function against the JC formula from the last
    exercise.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(get_rate_matrix_works, jc_rates):
    get_transition_probabilities_works = False
    if not get_rate_matrix_works:
        print("Get get_rate_matrix working first!")
    else:
        _jc_matrix = get_rate_matrix(jc_rates)
        _failures = []
        for _t in [0.0, 0.1, 0.5, 2.0]:
            _same = 1.0 - jc_prob_different(_t)
            _different = (1 - _same) / 3
            _expected = np.full((4, 4), _different)
            np.fill_diagonal(_expected, _same)
            try:
                _found = get_transition_probabilities(_jc_matrix, _t)
                _ok = np.allclose(_found, _expected)
            except Exception as _error:
                _ok = False
            if not _ok:
                _failures.append(f"  t = {_t}")
        get_transition_probabilities_works = len(_failures) == 0
        if get_transition_probabilities_works:
            print("Yay, your function passed the test!")
        else:
            print("Sorry, get_transition_probabilities did not match the JC "
                  + "formula at:\n" + "\n".join(_failures))
    return (get_transition_probabilities_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Exploring $P(t)$

    The next two cells create an interactive demonstration of the transition
    probability matrix.
    **You don't need to edit the next two cells**, but
    use the controls below to choose a model and watch how the matrix of transition
    probabilities changes as you adjust the amount of time during which evolution
    occurred.
    Your `get_rate_matrix` and `get_transition_probabilities` functions are used to
    calculate the probabilities of each possible substitution.
    """)
    return


@app.cell
def _(mo):
    # Create a dropdown for changing the model of sequence evolution
    model_dropdown = mo.ui.dropdown(
        options = ["JC", "K80 (kappa = 8)", "GC-rich HKY"],
        value = "K80 (kappa = 8)",
        label = "Model",
    )
    # Create a slider for adjusting time
    time_slider = mo.ui.slider(
        start = 0.0,
        stop = 10.0,
        step = 0.05,
        value = 0.5,
        label = "Time, $t$",
        show_value = True,
    )
    return model_dropdown, time_slider


@app.cell
def _(
    gc_rich_rates,
    get_transition_probabilities_works,
    jc_rates,
    k80_rates,
    mo,
    model_dropdown,
    time_slider,
):
    mo.stop(
        not get_transition_probabilities_works,
        mo.md(
            "***Waiting — Get `get_rate_matrix` and "
            + "`get_transition_probabilities` working first.***"
        ),
    )

    _models = {
        "JC": jc_rates,
        "K80 (kappa = 8)": k80_rates,
        "GC-rich HKY": gc_rich_rates,
    }
    _P = get_transition_probabilities(
        get_rate_matrix(_models[model_dropdown.value]), time_slider.value
    )
    _lines = [
        "| From \\ To | " + " | ".join(f"**{_b}**" for _b in BASES) + " | Row sum |",
        "|:-:|" + "--:|" * (len(BASES) + 1),
    ]
    for _i in range(4):
        _cells = " | ".join(f"{_P[_i, _j]:.3f}" for _j in range(4))
        _lines.append(f"| **{BASES[_i]}** | {_cells} | {_P[_i].sum():.3f} |")

    _instructions = "**Choose different models, adjust the time, and watch the probabilities change!**"
    _table_title = f"**{model_dropdown.value}**, $t$ = {time_slider.value:.2f}"
    _table = "\n".join(_lines)

    mo.vstack([
        mo.md(_instructions),
        model_dropdown,
        time_slider,
        mo.md(_table_title),
        mo.md(_table),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below compares your transition probabilities to your continuous-time
    simulation.
    It evolves 2,000 sites that start as `A` under K80 ($\kappa = 8$) with your
    `simulate_site` function, and plots the fraction of sites that are each base
    (points) along with the first row of $P(t)$ (lines).
    Under K80, an `A` is equally likely to become a `C` or a `T` (both are
    transversions), so those two lines lie on top of each other.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(get_transition_probabilities_works, k80_rates, mo, simulate_site_works):
    mo.stop(
        not (get_transition_probabilities_works and simulate_site_works),
        mo.md(
            "***Waiting — Get `simulate_site`, `get_rate_matrix`, and "
            + "`get_transition_probabilities` working first.***"
        ),
    )

    _k80_matrix = get_rate_matrix(k80_rates)
    _curve_t = [_i / 20 for _i in range(0, 201)]
    _curves = {_b: [] for _b in BASES}
    for _t in _curve_t:
        _P = get_transition_probabilities(_k80_matrix, _t)
        for _j in range(4):
            _curves[BASES[_j]].append(_P[0, _j])

    _rng = random.Random(1980)
    _sim_t = [_i / 1.5 for _i in range(0, 16)]
    _sim = {_b: [] for _b in BASES}
    for _t in _sim_t:
        _counts = {_b: 0 for _b in BASES}
        for _ in range(2000):
            _counts[simulate_site("A", _t, k80_rates, _rng)[0]] += 1
        for _b in BASES:
            _sim[_b].append(_counts[_b] / 2000)

    _figure, _axes = plt.subplots(figsize = (7, 4))
    _colors = {"A": "tab:blue", "C": "tab:orange", "G": "tab:green", "T": "tab:red"}
    for _b in BASES:
        _axes.plot(_curve_t, _curves[_b], color = _colors[_b],
                   label = f"$P_{{A{_b}}}(t)$")
        _axes.scatter(_sim_t, _sim[_b], color = _colors[_b], s = 18)
    _axes.set_xlabel("Time, $t$")
    _axes.set_ylabel("Probability")
    _axes.set_title("K80 ($\\kappa = 8$), starting from A: simulation vs. $P(t)$")
    _axes.legend()
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 9: Interpreting $P(t)$ </font>

    Use the controls and the plot above to answer the questions below.
    Double-click this cell to write your answers.

    1.  **When you set $t = 0$ using the slider, what does $P(t)$ look like?
        Why does that make sense?**

        **Answer**:

    2.  **Every row of the $P(t)$ table adds up to 1, for every model and every
        time. Why?**

        **Answer**:

    3.  **Set $t$ to 10. For the GC-rich model, what does every row look like?
        Why?**

        **Answer**:

    4.  **In the plot above, which bases does an `A` reach quickly, and which
        slowly? Why?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 5: Which model fits the yeast gene better?

    Now that we can calculate $P(t)$, we can use it to calculate the likelihood of two
    aligned sequences under **any** model.
    For each site where the first sequence has base $x$ and the second has base $y$,
    the probability is the frequency of $x$ times the probability of changing from
    $x$ to $y$ in time $t$:

    $$
    \ln L(t) = \sum_{\text{sites}} \Big[\ln(\pi_x) + \ln\big(P_{xy}(t)\big)\Big]
    $$

    /// note
    This is the full likelihood, including the probability of the bases themselves
    ($\pi_x$), which we left out in the last exercise.
    So, the log-likelihoods here will be lower than the ones you calculated last
    time.
    ///

    ## <font color=red> Challenge 10: The log-likelihood of two sequences </font>

    Complete the `log_likelihood_pair` function below.
    A recipe:

    1.  Loop over every index of `seq_1` (we assume the sequences are aligned, so
        the same index works for both)
    2.  If both bases (from `seq_1` and `seq_2`) at that index are in `BASES`, get
        their row and column numbers within the transition probability matrix
        using `i = BASES.index(base_1)` and `j = BASES.index(base_2)`
    3.  Add `math.log(base_frequencies[base_1])` and
        `math.log(transition_probabilities[i, j])` to `log_like`

    /// tip
    1.  `BASES.index("G")` returns 2, the position of `"G"` in `"ACGT"`.
    2.  If you use `i` and `j` for the row and column indices of the transition
        probability matrix (as suggested in Step 2 of the recipe above), make sure
        you use a different variable for looping over every index of `seq_1`.
    ///
    """)
    return


@app.function
def log_likelihood_pair(seq_1, seq_2, transition_probabilities, base_frequencies):
    """Log-likelihood of two aligned sequences, given P(t) and base frequencies.

    Only sites where both sequences have one of the four DNA bases are
    included.

    Args:
        seq_1 (str): The first aligned sequence.
        seq_2 (str): The second aligned sequence, the same length as `seq_1`.
        transition_probabilities (numpy.ndarray): The 4-by-4 matrix P(t), as
            returned by `get_transition_probabilities`.
        base_frequencies (dict[str, float]): The frequency of each base.

    Returns:
        float: The natural log of the likelihood.
    """
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
def _(get_transition_probabilities_works, jc_rates, k80_rates):
    log_likelihood_pair_works = False
    if not get_transition_probabilities_works:
        print("Get get_rate_matrix and get_transition_probabilities working first!")
    else:
        _equal_freqs = {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}
        _P_jc = get_transition_probabilities(get_rate_matrix(jc_rates), 0.2)
        _P_k80 = get_transition_probabilities(get_rate_matrix(k80_rates), 0.2)
        _ll_test_cases = [
            (("ACGT", "ACGT", _P_jc), -6.317351),
            (("ACGT", "GCAA", _P_jc), -14.253488),
            (("AC-TN", "GCATA", _P_k80), -6.557866),
        ]
        _failures = []
        for (_seq_1, _seq_2, _P), _expected in _ll_test_cases:
            try:
                _found = log_likelihood_pair(_seq_1, _seq_2, _P, _equal_freqs)
                _ok = abs(_found - _expected) < 1e-4
            except Exception as _error:
                _found = f"an error ({type(_error).__name__}: {_error})"
                _ok = False
            if not _ok:
                _failures.append(
                    f"  {_seq_1} vs {_seq_2}: expected {_expected:.4f}, got {_found}"
                )
        log_likelihood_pair_works = len(_failures) == 0
        if log_likelihood_pair_works:
            print("Yay, your function passed the test!")
        else:
            print("Sorry, log_likelihood_pair failed these cases:\n"
                  + "\n".join(_failures))
    return (log_likelihood_pair_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Comparing JC and K80

    The function below searches a grid of values of $t$ for the one with the highest
    log-likelihood.
    The second cell below uses this function, along with your other functions, to
    fit the JC model and the K80 model (with $\kappa$ set to its estimate from Part
    1) to the 3rd codon positions of the yeast gene.
    **You do not need to edit the next two cells.**
    """)
    return


@app.function
def find_best_time(seq_1, seq_2, rates, base_frequencies, max_t = 1.5, steps = 300):
    """Search a grid of times for the maximum likelihood estimate of t.

    Returns:
        tuple[list[float], list[float], float, float]: The grid of times, the
            log-likelihood at each, the best time, and its log-likelihood.
    """
    rate_matrix = get_rate_matrix(rates)
    times = [max_t * (i + 1) / steps for i in range(steps)]
    log_likes = []
    for t in times:
        P = get_transition_probabilities(rate_matrix, t)
        log_likes.append(log_likelihood_pair(seq_1, seq_2, P, base_frequencies))
    best_index = 0
    for i in range(len(log_likes)):
        if log_likes[i] > log_likes[best_index]:
            best_index = i
    return times, log_likes, times[best_index], log_likes[best_index]


@app.cell
def _(k80_distance_works, log_likelihood_pair_works, mo, site_sets):
    mo.stop(
        not (log_likelihood_pair_works and k80_distance_works),
        mo.md(
            "***Waiting — Get `log_likelihood_pair` and `k80_distance` working "
            + "first.***"
        ),
    )

    _seq_1, _seq_2 = site_sets["3rd codon positions"]
    _equal_freqs = {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}
    third_kappa = estimate_kappa(_seq_1, _seq_2)

    jc_times, _jc_log_likes, _jc_best_t, _jc_best_ll = find_best_time(
        _seq_1, _seq_2, make_rate_table(), _equal_freqs
    )
    k80_times, _k80_log_likes, _k80_best_t, _k80_best_ll = find_best_time(
        _seq_1, _seq_2, make_rate_table(kappa = third_kappa), _equal_freqs
    )
    _n, _ts, _tv = count_transitions_transversions(_seq_1, _seq_2)

    _figure, _axes = plt.subplots(figsize = (7, 4))
    _axes.plot(jc_times, _jc_log_likes, color = "steelblue", linewidth = 2, label = "JC")
    _axes.plot(k80_times, _k80_log_likes, color = "darkorange", linewidth = 2,
               label = f"K80 ($\\kappa$ = {third_kappa:.2f})")
    _axes.set_ylim(_k80_best_ll - 200, _k80_best_ll + 20)
    _axes.set_xlabel("Time, $t$ (expected substitutions per site)")
    _axes.set_ylabel("Log-likelihood")
    _axes.set_title("Yeast SSA3, 3rd codon positions")
    _axes.legend()

    _table = mo.md(
        "| Model | Best $t$ | Log-likelihood | Distance formula |\n"
        + "|:--|--:|--:|--:|\n"
        + f"| JC | {_jc_best_t:.3f} | {_jc_best_ll:.1f} "
        + f"| {jc_distance((_ts + _tv) / _n):.3f} |\n"
        + f"| K80 | {_k80_best_t:.3f} | {_k80_best_ll:.1f} "
        + f"| {k80_distance(_seq_1, _seq_2):.3f} |"
    )
    mo.vstack([_figure, _table])
    return (third_kappa,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 11: Comparing models </font>

    Double-click this cell and answer the questions below.

    1.  **Compare the best value of $t$ for each model to the distance formulas from
        Part 1. What do you notice?**

        **Answer**:

    2.  **Which model gives the higher log-likelihood, and by about how much? K80
        has one more parameter ($\kappa$) than JC. Does it fit better by only a
        little, or by a lot?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Stretch goal </font>

    In Part 1, we created the `estimate_kappa` function that used Kimura's formula
    to estimate $\kappa$.
    In the Python cell above Challenge 11, we used that function to calculate
    $\kappa$ from the 3rd codon positions of the *SSA3* gene from the two species of
    yeast, and stored that value in the `third_kappa` variable.

    Can you find the best $\kappa$ by maximum likelihood instead?

    In the cell below, beneath the "`Write your stretch goal code below ...`"
    comment, add your code that finds the maximum likelihood estimate of $\kappa$.

    Your code should loop over values of $\kappa$ from 1 to 20 (in steps of 1).
    For each value of $\kappa$, make a K80 rate table with `make_rate_table(kappa =
    kappa)`, and use `find_best_time` to get the best $t$ and its log-likelihood.
    After you finish looping over the 20 values,
    print the value of $\kappa$ with the highest log-likelihood.

    How does the value of $\kappa$ with the highest log-likelihood compare to the
    estimate using Kimura's formula?

    **Answer**:
    """)
    return


@app.cell
def _(log_likelihood_pair_works, mo, site_sets, third_kappa):
    mo.stop(not log_likelihood_pair_works)

    # Print the value of kappa estimated with Kimura's formula
    print(f"Kappa estimated with Kimura's formula: {third_kappa:.2f}\n")

    # Get the 3rd codon positions of the SSA3 gene from both yeast species
    _seq_1, _seq_2 = site_sets["3rd codon positions"]

    # Create a dict of equal frequencies (we'll need it for `find_best_time`)
    _equal_freqs = {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}

    # Set initial best kappa to None and best log likelihood to negative infinity
    _best_kappa = None
    _best_log_like = -math.inf

    # Write your stretch goal code below that uses a for loop to try values of kappa
    # 1, 2, 3, ..., 20 and stores the kappa value with the best log-likelihood in
    # `_best_kappa` and stores the best log-likelihood in `_best_log_like`
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    -   The **K80 model** has separate rates for transitions and transversions; its
        distance corrects the bias JC showed when transitions are more common
        than transversions
    -   A model is a **table of rates**; in **continuous time**, the waiting time
        until the next substitution is **exponentially distributed** (and
        memoryless)
    -   With unequal **base frequencies** (HKY), a site settles at those
        frequencies, and sequences saturate below 0.75
    -   The **rate matrix** $Q$ holds the rates, and $P(t) = e^{Qt}$ gives the
        **transition probabilities** for any model
    -   With $P(t)$, we can calculate the **likelihood** under any model, and compare
        models: K80 fits the yeast 3rd codon positions far better than JC
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
