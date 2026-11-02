# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.0",
#     "matplotlib",
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

    # Where to find the tree of bent-toed geckos we use in Part 4
    GECKO_TREE_URL = (
        "https://raw.githubusercontent.com/phyletica/intro-to-comp-bio/"
        + "refs/heads/main/notebooks/data/Cyrtodactylus-beast-tree.nex"
    )


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Birth-death models: How lineages multiply and vanish

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A process that grows trees

    In the phylogenetics exercise, we used trees to learn about how **sequences**
    evolve.
    In this exercise, we will flip the question around, and ask: What process grows
    the **tree** itself?

    Every branch of a tree of species is a ***lineage***.
    As time passes, lineages split into two (***speciation***), and some
    lineages die out (***extinction***).
    A ***birth-death model*** treats speciation ("birth") and extinction
    ("death") as random events that happen to each lineage at a constant rate.
    Birth-death models are used to model many other things that multiply and die,
    like cells in a tumor, individuals in a population, or infections in an epidemic
    (which is where we are headed in the next exercise).

    Here's our plan for this exercise:

    1.  Simulate lineages that only **split** (a ***pure-birth*** process)
    2.  Add **extinction**, and see how often a whole group of species dies out
    3.  Simulate **trees**, and compare the full history of a group to the tree
        we can actually see from the species that are alive today
    4.  Compare the tree of 345 species of **bent-toed geckos** to our model
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: Lineages that only split

    ## The pure-birth model

    Let's start with the simplest model: Every lineage splits into two at a rate of
    $\lambda$ splits per lineage per unit of time, and no lineage ever goes extinct.
    This is called the ***pure-birth*** model, or the ***Yule*** model, after the
    statistician who first used it to model the number of species in a genus
    (Yule, 1925).
    The rate $\lambda$ is called the ***birth rate*** (or the ***speciation
    rate***).
    The time could be in any unit, but for species, it is usually millions of
    years.

    Simulating the pure-birth model will feel familiar!
    In the substitution models exercise, a site changed at a ***total rate*** (the
    sum of the rate of change from the current base to the other three bases), so
    the waiting time until its next substitution was exponential, which we drew with
    `rng.expovariate(total_rate)`.
    Then, we randomly chose which base the current base changed to.
    The pure-birth model is very similar: The waiting time until the next split is
    exponential with a total rate that is the sum of the rates of all the lineages
    that can split.
    After we draw the waiting time, then we randomly pick which lineage splits.

    Let's make this more specific by using $n$ to represent the number of tips
    (lineages) currently on the growing tree.
    Each lineage has its own waiting time, and the next event happens when the
    **first** of them splits.
    With $n$ lineages, splits happen $n$ times as often as with one, so the
    waiting time until the next split is exponential with a total rate of
    $n \lambda$.
    That means the more lineages there are, the faster new ones appear!

    This way of simulating a random process, one event at a time, by drawing the
    waiting time from the total rate and then choosing which event happened, is
    called the ***Gillespie algorithm*** (Gillespie, 1977).
    You already used it to simulate a site in the substitution models exercise!

    /// details | Optional: Why do the rates add up?
    A rate is the expected number of events per unit of time.
    If one lineage splits, on average, $\lambda$ times per unit of time, then $n$
    lineages, each splitting independently, produce $n \lambda$ splits per unit
    of time, on average.
    And because the exponential distribution is memoryless, it doesn't matter
    how long each lineage has already been waiting: After every event, the
    waiting time until the next one is exponential with the new total rate.
    ///

    ## <font color=red> Challenge 1: Simulating a pure-birth process </font>

    Complete the `simulate_pure_birth` function below.
    It starts with one lineage at time 0, and repeats three steps:

    1.  Find the **total rate** of splitting, for all of the lineages together
    2.  Draw a **waiting time** until the next split, and add it to the `clock`
    3.  If the clock has gone past `max_time`, stop.
        Otherwise, add one lineage, and record the time and the number of lineages

    The function already has the loop, the clock, the records, and the check for
    when to stop.
    Replace each of the two `None`s (`total_rate` and `waiting_time`) with code
    that does what the comment above it says.

    /// tip
    1.  The total rate is the number of lineages (the `lineages` variable) times
        the birth rate (`birth_rate`)
    2.  `rng.expovariate(total_rate)` draws a random waiting time
    ///

    /// warning
    Leave the two checks in the function in place.
    If there's a mistake in your waiting time (for example, if it is always
    zero), they stop the function with an error, instead of letting it loop
    forever and freeze your notebook.
    ///

    /// note
    You might notice that, after we draw the waiting time, we don't randomly pick
    which lineage splits.
    That is because in this function, we don't keep track of the tree relating the
    tips, only the number of tips.
    So, we don't need to keep track of which tip splits, only when the next one
    splits.
    ///
    """)
    return


@app.function
def simulate_pure_birth(birth_rate, max_time, rng):
    """Simulate the number of lineages under a pure-birth (Yule) process.

    The simulation starts with one lineage at time 0. Each lineage splits into
    two at rate `birth_rate`, and no lineage ever goes extinct.

    Args:
        birth_rate (float): The rate at which each lineage splits (splits per
            lineage per unit of time).
        max_time (float): How long to run the simulation.
        rng (random.Random): The random number generator to use.

    Returns:
        tuple[list[float], list[int]]: The times of the events, and the number
            of lineages right after each event. The lists start with time 0 (and
            1 lineage), and end with `max_time` (and the final number of
            lineages).

    Examples:
        >>> simulate_pure_birth(1.0, 0.0, random.Random(1))
        ([0.0, 0.0], [1, 1])
    """
    lineages = 1
    clock = 0.0
    times = [0.0]
    counts = [1]
    while True:
        # 1. Replace `None` with the total rate of splitting, for all of the
        #    lineages together
        total_rate = None
        # 2. Replace `None` with a random waiting time until the next split
        waiting_time = None
        if not (waiting_time >= 0):
            raise ValueError("The waiting time cannot be negative.")
        clock += waiting_time
        if clock > max_time:
            break
        lineages += 1
        times.append(clock)
        counts.append(lineages)
        if lineages > 100_000:
            raise RuntimeError(
                "Too many lineages! Is your waiting time always 0?"
            )
    times.append(max_time)
    counts.append(lineages)
    return times, counts


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    simulate_pure_birth_works = True
    _messages = []

    try:
        # Test 1: With no time, nothing happens
        _result = simulate_pure_birth(1.0, 0.0, random.Random(1))
        if _result != ([0.0, 0.0], [1, 1]):
            simulate_pure_birth_works = False
            _messages.append(
                f"With max_time = 0, the result should be ([0.0, 0.0], [1, 1]), "
                + f"not {_result}."
            )

        # Test 2: The records should make sense
        _times, _counts = simulate_pure_birth(1.0, 3.0, random.Random(2))
        if _times[-1] != 3.0 or len(_times) != len(_counts):
            simulate_pure_birth_works = False
            _messages.append("The records don't end at max_time.")
        for _i in range(1, len(_times) - 1):
            if _counts[_i] != _counts[_i - 1] + 1 or _times[_i] < _times[_i - 1]:
                simulate_pure_birth_works = False
                _messages.append(
                    "Each event should add one lineage, at a later time."
                )
                break

        # Test 3: At birth rate 1 and time 2, the average number of lineages
        # should be about e^2 = 7.39, and about 13.5% of runs should still have
        # only 1 lineage
        if simulate_pure_birth_works:
            _rng = random.Random(3)
            _finals = []
            for _ in range(2000):
                _finals.append(simulate_pure_birth(1.0, 2.0, _rng)[1][-1])
            _mean = sum(_finals) / len(_finals)
            _fraction_one = _finals.count(1) / len(_finals)
            print(f"Birth rate 1, time 2: average of {_mean:.2f} lineages "
                  + f"(expected {math.exp(2):.2f}), {_fraction_one:.3f} of runs "
                  + f"still have 1 lineage (expected {math.exp(-2):.3f})")
            if not (6.8 < _mean < 8.0):
                simulate_pure_birth_works = False
                _messages.append(
                    "The average number of lineages is off. "
                    + "Is your total rate the number of lineages times the "
                    + "birth rate? Did you give rng.expovariate the rate (not "
                    + "the average waiting time)?"
                )
            if not (0.11 < _fraction_one < 0.16):
                simulate_pure_birth_works = False
                _messages.append(
                    "The fraction of runs with only 1 lineage is off."
                )

        # Test 4: The same seed should give the same results
        _first = simulate_pure_birth(1.0, 3.0, random.Random(4))
        _second = simulate_pure_birth(1.0, 3.0, random.Random(4))
        if _first != _second:
            simulate_pure_birth_works = False
            _messages.append("Make sure every random draw uses rng.")

    except Exception as _error:
        simulate_pure_birth_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )
        if "NoneType" in str(_error):
            _messages.append("Did you replace both of the Nones?")

    print()
    if simulate_pure_birth_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your simulate_pure_birth function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (simulate_pure_birth_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below uses your `simulate_pure_birth` function to run 20 simulations
    with a birth rate of 1, for 5 units of time.
    It plots the number of lineages over time in each simulation (gray), along
    with the expected number of lineages, $e^{\lambda t}$ (red).
    The left plot uses a regular y-axis, and the right plot uses a ***log
    scale***, where each step up the axis is 10 times the one below it.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(mo, simulate_pure_birth_works):
    mo.stop(
        not simulate_pure_birth_works,
        mo.md("***Waiting — Get your `simulate_pure_birth` function working "
              + "first.***"),
    )

    _rng = random.Random(1925)
    _birth_rate = 1.0
    _max_time = 5.0
    _figure, _axes = plt.subplots(1, 2, figsize = (11, 4))
    for _ in range(20):
        _times, _counts = simulate_pure_birth(_birth_rate, _max_time, _rng)
        for _ax in _axes:
            _ax.step(_times, _counts, where = "post", color = "gray",
                     alpha = 0.6, linewidth = 1)
    _curve_t = [_i / 20 for _i in range(0, 101)]
    _expected = [math.exp(_birth_rate * _t) for _t in _curve_t]
    for _ax in _axes:
        _ax.plot(_curve_t, _expected, color = "firebrick", linewidth = 2,
                 label = r"Expected, $e^{\lambda t}$")
        _ax.set_xlabel("Time")
        _ax.set_ylabel("Number of lineages")
        _ax.legend()
    _axes[0].set_title("Regular y-axis")
    _axes[1].set_yscale("log")
    _axes[1].set_title("Log-scale y-axis")
    _figure.tight_layout()
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 2: Exponential growth </font>

    Double-click this cell and answer the questions below.

    1.  **On the regular y-axis, the curves bend upward, but on the log-scale
        y-axis, they are close to straight lines. Why? (Hint: What is
        $\log_e\left(e^{\lambda t}\right)$?)**

        **Answer**:

    2.  **On the log-scale plot, the simulations differ the most from each other
        near the start, and later they run roughly parallel to each other. Why do
        you think that is?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 2: Adding extinction

    ## The birth-death model

    Now, let's allow lineages to go extinct.
    Each lineage splits at rate $\lambda$, and goes extinct at a ***death
    rate*** (or ***extinction rate***) of $\mu$.
    With $n$ lineages, each of them can either split or go extinct, so the total
    rate of events is:

    $$
    n \lambda + n \mu = n (\lambda + \mu)
    $$

    With this total rate, we can get our waiting time until the next event
    (*i.e.*, `rng.expovariate(total_rate)`),
    but when the event happens, ***which kind is it***?
    Splits happen at rate $n \lambda$ out of the total rate of $n (\lambda + \mu)$,
    so the event is a split with probability:

    $$
    \frac{n \lambda}{n (\lambda + \mu)} = \frac{\lambda}{\lambda + \mu}
    $$

    and an extinction otherwise.

    The difference between the birth and death rates, $r = \lambda - \mu$, is
    called the ***net diversification rate***.
    On average, the number of lineages grows like $e^{r t}$.
    But, as we will see, the average hides a lot!

    ## <font color=red> Challenge 3: Simulating a birth-death process </font>

    Complete the `simulate_birth_death` function below.
    It works just like your `simulate_pure_birth` function, but now each event
    can be a split **or** an extinction, and the loop stops early if every
    lineage goes extinct (`while lineages > 0`).

    1.  Replace the two `None`s (`total_rate` and `waiting_time`), like you did
        in Challenge 1, but now the total rate includes extinction
    2.  Under the "`3. Add your code here!`" comment, decide which kind of event
        happened: With probability $\lambda / (\lambda + \mu)$, add 1 to
        `lineages`; otherwise, subtract 1 from `lineages`

    /// tip
    Remember, `rng.random()` returns a random number between 0 and 1, so
    `rng.random() < p` is `True` with probability `p`.
    So, the event is a split if
    `rng.random() < birth_rate / (birth_rate + death_rate)`.
    Use an `if` and an `else` to either add or subtract a lineage.
    ///
    """)
    return


@app.function
def simulate_birth_death(birth_rate, death_rate, max_time, rng):
    """Simulate the number of lineages under a birth-death process.

    The simulation starts with one lineage at time 0. Each lineage splits into
    two at rate `birth_rate`, and goes extinct at rate `death_rate`. The
    simulation stops at `max_time`, or earlier if every lineage goes extinct.

    Args:
        birth_rate (float): The rate at which each lineage splits (per lineage
            per unit of time).
        death_rate (float): The rate at which each lineage goes extinct (per
            lineage per unit of time).
        max_time (float): How long to run the simulation.
        rng (random.Random): The random number generator to use.

    Returns:
        tuple[list[float], list[int]]: The times of the events, and the number
            of lineages right after each event. The lists start with time 0 (and
            1 lineage), and end with `max_time` (and the final number of
            lineages, which is 0 if every lineage went extinct).

    Examples:
        >>> simulate_birth_death(1.0, 0.5, 0.0, random.Random(1))
        ([0.0, 0.0], [1, 1])
    """
    lineages = 1
    clock = 0.0
    times = [0.0]
    counts = [1]
    while lineages > 0:
        # 1. Replace `None` with the total rate of events (splits and
        #    extinctions), for all of the lineages together
        total_rate = None
        # 2. Replace `None` with a random waiting time until the next event
        waiting_time = None
        if not (waiting_time >= 0):
            raise ValueError("The waiting time cannot be negative.")
        clock += waiting_time
        if clock > max_time:
            break
        # 3. Add your code here! Decide whether the event is a split or an
        #    extinction, and add 1 to, or subtract 1 from, `lineages`

        times.append(clock)
        counts.append(lineages)
        if lineages > 100_000:
            raise RuntimeError(
                "Too many lineages! Is your waiting time always 0?"
            )
    times.append(max_time)
    counts.append(lineages)
    return times, counts


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    simulate_birth_death_works = True
    _messages = []

    try:
        # Test 1: With no time, nothing happens
        _result = simulate_birth_death(1.0, 0.5, 0.0, random.Random(1))
        if _result != ([0.0, 0.0], [1, 1]):
            simulate_birth_death_works = False
            _messages.append(
                f"With max_time = 0, the result should be ([0.0, 0.0], [1, 1]), "
                + f"not {_result}."
            )

        # Test 2: Each event should add or remove exactly one lineage
        _times, _counts = simulate_birth_death(1.0, 0.5, 4.0, random.Random(2))
        if _times[-1] != 4.0 or len(_times) != len(_counts):
            simulate_birth_death_works = False
            _messages.append("The records don't end at max_time.")
        for _i in range(1, len(_times) - 1):
            if abs(_counts[_i] - _counts[_i - 1]) != 1:
                simulate_birth_death_works = False
                _messages.append(
                    "Each event should add 1 lineage or remove 1 lineage."
                )
                break

        # Test 3: With a birth rate of 0, every event is an extinction
        _rng = random.Random(3)
        _extinct = 0
        for _ in range(500):
            _times, _counts = simulate_birth_death(0.0, 1.0, 5.0, _rng)
            if max(_counts) > 1:
                simulate_birth_death_works = False
                _messages.append(
                    "With a birth rate of 0, every event should be an "
                    + "extinction. Is your split probability "
                    + "birth_rate / (birth_rate + death_rate)?"
                )
                break
            if _counts[-1] == 0:
                _extinct += 1
        if simulate_birth_death_works and _extinct < 480:
            simulate_birth_death_works = False
            _messages.append(
                "With a birth rate of 0 and a death rate of 1, almost every "
                + "lineage should go extinct by time 5."
            )

        # Test 4: With a death rate of 0, this is the pure-birth model
        if simulate_birth_death_works:
            _rng = random.Random(4)
            _finals = []
            for _ in range(2000):
                _finals.append(simulate_birth_death(1.0, 0.0, 2.0, _rng)[1][-1])
            _mean = sum(_finals) / len(_finals)
            print(f"Birth rate 1, death rate 0, time 2: average of {_mean:.2f} "
                  + f"lineages (expected {math.exp(2):.2f})")
            if not (6.8 < _mean < 8.0):
                simulate_birth_death_works = False
                _messages.append(
                    "With a death rate of 0, the average number of lineages "
                    + "should match the pure-birth model."
                )

        # Test 5: Birth rate 1, death rate 0.5, time 6
        if simulate_birth_death_works:
            _rng = random.Random(5)
            _finals = []
            for _ in range(2000):
                _finals.append(simulate_birth_death(1.0, 0.5, 6.0, _rng)[1][-1])
            _mean = sum(_finals) / len(_finals)
            _fraction_extinct = _finals.count(0) / len(_finals)
            print(f"Birth rate 1, death rate 0.5, time 6: average of {_mean:.2f} "
                  + f"lineages (expected {math.exp(3):.2f}), "
                  + f"{_fraction_extinct:.3f} of runs went extinct "
                  + "(expected 0.487)")
            if not (16.5 < _mean < 23.5):
                simulate_birth_death_works = False
                _messages.append(
                    "The average number of lineages is off. Does your total "
                    + "rate include both splits and extinctions?"
                )
            if not (0.44 < _fraction_extinct < 0.54):
                simulate_birth_death_works = False
                _messages.append("The fraction of runs that went extinct is off.")

        # Test 6: The same seed should give the same results
        _first = simulate_birth_death(1.0, 0.5, 4.0, random.Random(6))
        _second = simulate_birth_death(1.0, 0.5, 4.0, random.Random(6))
        if _first != _second:
            simulate_birth_death_works = False
            _messages.append("Make sure every random draw uses rng.")

    except Exception as _error:
        simulate_birth_death_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )
        if "NoneType" in str(_error):
            _messages.append("Did you replace both of the Nones?")
        if isinstance(_error, ZeroDivisionError):
            _messages.append(
                "The total rate was 0 when the birth rate was 0. Does your "
                + "total rate include both splits and extinctions?"
            )

    print()
    if simulate_birth_death_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your simulate_birth_death function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (simulate_birth_death_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How often does a clade go extinct?

    A ***clade*** is an ancestor and all of its descendants.
    In our simulations, the clade is the first lineage and every lineage that
    descends from it.
    If every lineage dies, the whole clade is extinct.

    The cell below uses your `simulate_birth_death` function to simulate 1,000
    clades for each of several death rates (with a birth rate of 1, for 5 units
    of time), and counts how many went extinct.
    It compares those counts to two predictions from the math of birth-death
    models (Kendall, 1948):

    -   The probability that a clade is extinct by time $t$, which is
        $\frac{\mu \left( e^{r t} - 1 \right)}{\lambda e^{r t} - \mu}$
        (or $\frac{\lambda t}{1 + \lambda t}$ when $\lambda = \mu$)
    -   The probability that a clade **eventually** goes extinct, if we wait
        forever, which is $\mu / \lambda$ when $\mu < \lambda$, and 1 when
        $\mu \ge \lambda$

    **You do not need to edit the next two cells.**
    """)
    return


@app.function
def prob_extinct_by_time(birth_rate, death_rate, t):
    """Probability that a clade that starts with one lineage is extinct by time t.

    Args:
        birth_rate (float): The birth rate (lambda).
        death_rate (float): The death rate (mu).
        t (float): The amount of time.

    Returns:
        float: The probability that every lineage is extinct by time `t`.
    """
    if birth_rate == death_rate:
        return birth_rate * t / (1 + birth_rate * t)
    net_rate = birth_rate - death_rate
    growth = math.exp(net_rate * t)
    return death_rate * (growth - 1) / (birth_rate * growth - death_rate)


@app.cell
def _(mo, simulate_birth_death_works):
    mo.stop(
        not simulate_birth_death_works,
        mo.md("***Waiting — Get your `simulate_birth_death` function working "
              + "first.***"),
    )

    _rng = random.Random(1948)
    _rows = []
    for _death_rate in [0.0, 0.25, 0.5, 0.75, 0.9, 1.0]:
        _extinct = 0
        for _ in range(1000):
            _times, _counts = simulate_birth_death(1.0, _death_rate, 5.0, _rng)
            if _counts[-1] == 0:
                _extinct += 1
        _by_time = prob_extinct_by_time(1.0, _death_rate, 5.0)
        _eventually = min(_death_rate / 1.0, 1.0)
        _rows.append(
            f"| {_death_rate} | {_extinct / 1000:.3f} | {_by_time:.3f} "
            + f"| {_eventually:.3f} |"
        )
    mo.md(
        "| Death rate ($\\mu$) | Fraction extinct by time 5 (simulated) "
        + "| Predicted by time 5 | Predicted eventually |\n"
        + "|--:|--:|--:|--:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 4: Plotting the size of clades </font>

    So far, I've written all of the plotting code for you.
    Now it's your turn!
    The cell after next simulates 1,000 clades with a birth rate of 1 and a death
    rate of 0.5, for 6 units of time, and stores the final number of lineages of
    each clade in a list called `final_counts`.
    Complete the `plot_final_counts` function below, which plots a
    ***histogram*** of these numbers.
    A histogram divides the range of the numbers into equal-sized bins, and draws
    a bar for each bin, whose height is how many of the numbers fall into it.

    A recipe:

    1.  Make a figure with one set of axes:
        `figure, axes = plt.subplots(figsize = (7, 4))`
    2.  Draw a histogram of `final_counts` with 50 bins:
        `axes.hist(final_counts, bins = 50)`
    3.  Label the x-axis with `axes.set_xlabel("...")`, the y-axis with
        `axes.set_ylabel("...")`, and give the plot a title with
        `axes.set_title("...")`, replacing each `...` with a helpful label
    4.  The function already returns `figure`

    /// tip
    Think about what each axis shows.
    Each number in `final_counts` is the number of lineages at the end of one
    simulation, and the height of each bar is a number of simulations.
    ///
    """)
    return


@app.function
def plot_final_counts(final_counts):
    """Plot a histogram of the final number of lineages in many simulations.

    Args:
        final_counts (list[int]): The number of lineages at the end of each
            simulation.

    Returns:
        matplotlib.figure.Figure: The figure with the histogram (or None, until
            the function is complete).
    """
    figure = None
    # Add your code here!
    return figure


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    plot_final_counts_works = True
    _messages = []
    try:
        _figure = plot_final_counts([0, 0, 0, 1, 2, 3, 5, 8, 13, 21])
        if not isinstance(_figure, plt.Figure):
            plot_final_counts_works = False
            _messages.append(
                f"Your function should return a figure, not {type(_figure).__name__}."
            )
        elif len(_figure.axes) != 1:
            plot_final_counts_works = False
            _messages.append("Your figure should have one set of axes.")
        else:
            _axes = _figure.axes[0]
            if len(_axes.patches) == 0:
                plot_final_counts_works = False
                _messages.append("Your axes don't have any histogram bars.")
            if _axes.get_xlabel() == "":
                plot_final_counts_works = False
                _messages.append("Your x-axis needs a label.")
            if _axes.get_ylabel() == "":
                plot_final_counts_works = False
                _messages.append("Your y-axis needs a label.")
            if _axes.get_title() == "":
                plot_final_counts_works = False
                _messages.append("Your plot needs a title.")
        if isinstance(_figure, plt.Figure):
            plt.close(_figure)
    except Exception as _error:
        plot_final_counts_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )

    if plot_final_counts_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your plot_final_counts function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (plot_final_counts_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below runs the 1,000 simulations, uses your function to plot their
    final sizes, and summarizes them.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(mo, plot_final_counts_works, simulate_birth_death_works):
    mo.stop(
        not (simulate_birth_death_works and plot_final_counts_works),
        mo.md("***Waiting — Get your `simulate_birth_death` and "
              + "`plot_final_counts` functions working first.***"),
    )

    _rng = random.Random(1)
    final_counts = []
    for _ in range(1000):
        final_counts.append(simulate_birth_death(1.0, 0.5, 6.0, _rng)[1][-1])

    _survivors = []
    for _count in final_counts:
        if _count > 0:
            _survivors.append(_count)

    _summary = mo.md(
        f"""
    | | |
    |:--|--:|
    | Fraction of clades that went extinct | {final_counts.count(0) / 1000:.3f} |
    | Average size of all clades | {sum(final_counts) / 1000:.1f} |
    | Average size of the clades that survived | {sum(_survivors) / len(_survivors):.1f} |
    | Expected size, $e^{{r t}}$ | {math.exp(0.5 * 6.0):.1f} |
    | Largest clade | {max(final_counts)} |
    """
    )
    mo.vstack([plot_final_counts(final_counts), _summary])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 5: Winning and losing clades in a game of chance </font>

    Double-click this cell and answer the questions below.

    1.  **In the table of extinctions with varying death rates (above Challenge 4),
        how does the fraction of clades that went extinct change as the death rate
        increases? Even when the birth rate is twice the death rate ($\mu = 0.5$),
        about how many clades go extinct?**

        **Answer**:

    2.  **In the histogram, about half of the clades went extinct, and the clades
        that survived are, on average, about twice as big as $e^{r t}$. Every
        clade that biologists study today is a survivor. How might that bias what
        we learn about diversification from living clades?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Conditioning on survival

    Question 2 of Challenge 5 is alluding to a bias created by not accounting for
    clades that go extinct.
    This is why birth-death models used with real phylogenies ***condition on
    survival***: They ask how probable the tree is, **given** that the clade survived to
    the present.

    # Part 3: From lineages to trees

    ## Simulating trees

    Our simulations so far only counted lineages.
    To compare our model to real trees, we also need to keep track of **which**
    lineage split or went extinct at each event, which gives us a tree.
    The `simulate_tree` function below does exactly what your
    `simulate_birth_death` function does, but at each event, it picks one of the
    living lineages at random to split or go extinct, and records it in a tree.

    Two differences from before:

    1.  `simulate_tree` starts at the ***root*** of the tree, the first split, so
        there are **2** lineages at time 0.
        This is where trees of living species start: at the most recent common
        ancestor of all of the species.
    2.  If either of the two lineages at the root has no living descendants at the
        end of the simulation, `simulate_tree` throws the tree out and tries again.
        In other words, it **conditions on survival**, like we discussed after
        Challenge 5!

    The tree is a **list of nodes in postorder**, just like in the phylogenetics
    exercise.
    Each node is a dictionary with the keys `"name"`, `"children"`, and
    `"length"` (the length of the branch from the node to its parent), and one new
    key, `"extinct"`, which is `True` for a tip whose lineage went extinct.
    **You do not need to edit any of the functions in Part 3**, but you should read
    their descriptions to understand what they do.
    """)
    return


@app.function
def simulate_tree(birth_rate, death_rate, max_time, rng):
    """Simulate a complete tree under a birth-death process, from the root.

    The simulation starts at the root (time 0) with 2 lineages, and runs until
    `max_time` (the present). Trees in which either of the 2 lineages at the
    root has no living descendants at the present are thrown out, and the
    simulation is repeated.

    Args:
        birth_rate (float): The birth rate (lambda).
        death_rate (float): The death rate (mu).
        max_time (float): The time from the root to the present.
        rng (random.Random): The random number generator to use.

    Returns:
        list[dict]: The nodes of the complete tree, in postorder. Each node has
            the keys "name", "children", "length", and "extinct".
    """
    for _attempt in range(100_000):
        # Each lineage is a branch, stored by its index in these lists.
        # Lineage 0 is the root; lineages 1 and 2 start at the root.
        start_time = [0.0, 0.0, 0.0]
        end_time = [0.0, None, None]
        children = [[1, 2], [], []]
        extinct = [False, False, False]
        living = [1, 2]
        clock = 0.0
        while len(living) > 0:
            total_rate = len(living) * (birth_rate + death_rate)
            clock += rng.expovariate(total_rate)
            if clock > max_time:
                break
            # Pick which living lineage the event happens to
            lineage = living.pop(rng.randrange(len(living)))
            end_time[lineage] = clock
            if rng.random() < birth_rate / (birth_rate + death_rate):
                # A split: The lineage ends in a node with two new lineages
                for _ in range(2):
                    start_time.append(clock)
                    end_time.append(None)
                    children.append([])
                    extinct.append(False)
                    children[lineage].append(len(start_time) - 1)
                    living.append(len(start_time) - 1)
            else:
                # An extinction: The lineage ends in an extinct tip
                extinct[lineage] = True
            if len(living) > 50_000:
                raise RuntimeError("The tree is too big! Try a shorter time.")
        for lineage in living:
            end_time[lineage] = max_time

        # Find which lineages have living descendants. Children always have
        # larger indices than their parents, so we go from the end to the start.
        has_living = [False] * len(start_time)
        for index in reversed(range(len(start_time))):
            if len(children[index]) == 0:
                has_living[index] = not extinct[index]
            else:
                has_living[index] = any(has_living[c] for c in children[index])
        if not (has_living[1] and has_living[2]):
            # Neither lineage descending from the root of this tree has any
            # living descendants, so this clade went extinct.
            # Use `continue` to begin the next attempt in the for loop
            continue
        return lineages_to_tree(children, start_time, end_time, extinct)
    raise RuntimeError("No tree survived. Is the death rate much higher than "
                       + "the birth rate?")


@app.function
def lineages_to_tree(children, start_time, end_time, extinct):
    """Convert lineages recorded during a simulation into a list of nodes.

    Used by `simulate_tree` and `simulate_tree_with_tips`. Lineage 0 must be
    the root.

    Args:
        children (list[list[int]]): The child lineages of each lineage.
        start_time (list[float]): The time each lineage started.
        end_time (list[float]): The time each lineage ended.
        extinct (list[bool]): Whether each lineage ended in extinction.

    Returns:
        list[dict]: The tree as a list of nodes in postorder. Tips are named
            "t1", "t2", and so on.
    """
    # Put the lineages in postorder (children before parents), without
    # recursion, using a stack
    order = []
    stack = [(0, False)]
    while stack:
        index, children_done = stack.pop()
        if children_done:
            order.append(index)
        else:
            stack.append((index, True))
            for child in reversed(children[index]):
                stack.append((child, False))
    new_index = {}
    tree = []
    number_of_tips = 0
    for index in order:
        name = ""
        if len(children[index]) == 0:
            number_of_tips += 1
            name = f"t{number_of_tips}"
        new_index[index] = len(tree)
        tree.append({
            "name": name,
            "children": [new_index[c] for c in children[index]],
            "length": end_time[index] - start_time[index],
            "extinct": extinct[index],
        })
    # The root node (the last node in the list) has no length, because it has no
    # parent
    tree[-1]["length"] = None
    return tree


@app.function
def is_extant(node):
    """Return True if a node is not an extinct tip.

    ("Extant" means "still alive today," the opposite of "extinct.")
    """
    return not node.get("extinct", False)


@app.function
def prune_tips(tree, keep_func):
    """Remove tips from a tree, along with any branches left without tips.

    Internal nodes left with only one child are removed, and the branch above
    them is joined to the branch below them.

    Args:
        tree (list[dict]): A list of nodes in postorder.
        keep_func (function): A function that takes a tip node and returns True
            if the tip should be kept.

    Returns:
        list[dict]: The pruned tree, as a list of nodes in postorder. The
            original tree is not changed.
    """
    pruned = []
    new_index = [None] * len(tree)
    for index, node in enumerate(tree):
        if len(node["children"]) == 0:
            if keep_func(node):
                pruned.append(dict(node))
                new_index[index] = len(pruned) - 1
            continue
        kept_children = []
        for child in node["children"]:
            if new_index[child] is not None:
                kept_children.append(new_index[child])
        if len(kept_children) == 0:
            continue
        if len(kept_children) == 1:
            # Join this node's branch to the branch of its only child
            only_child = pruned[kept_children[0]]
            if node["length"] is None:
                only_child["length"] = None
            else:
                only_child["length"] += node["length"]
            new_index[index] = kept_children[0]
            continue
        new_node = dict(node)
        new_node["children"] = kept_children
        pruned.append(new_node)
        new_index[index] = len(pruned) - 1
    if len(pruned) > 0:
        pruned[-1]["length"] = None
    return pruned


@app.function
def get_node_times(tree):
    """Get the time of every node in a tree, measured from the root.

    Args:
        tree (list[dict]): A list of nodes in postorder.

    Returns:
        list[float]: The time of each node (in the same order as `tree`); the
            sum of the branch lengths from the root to the node.

    Examples:
        >>> get_node_times(parse_newick("((A:1,B:1):2,C:3);"))
        [3.0, 3.0, 2.0, 3.0, 0.0]
    """
    parent = [None] * len(tree)
    for index, node in enumerate(tree):
        for child in node["children"]:
            parent[child] = index
    times = [0.0] * len(tree)
    for index in reversed(range(len(tree) - 1)):
        times[index] = times[parent[index]] + tree[index]["length"]
    return times


@app.function
def draw_tree(tree, axes, title = "", time_label = "Time since the root"):
    """Draw a tree (a list of nodes in postorder) on a matplotlib axes.

    Time runs from the root at the left to the present at the right. Branches
    with no living descendants are drawn in light gray.

    Args:
        tree (list[dict]): A list of nodes in postorder.
        axes (matplotlib.axes.Axes): The axes to draw on.
        title (str): A title for the plot.
        time_label (str): A label for the x-axis.
    """
    x = get_node_times(tree)
    has_living = [False] * len(tree)
    y = [0.0] * len(tree)
    next_tip_y = 0
    for index, node in enumerate(tree):
        if len(node["children"]) == 0:
            has_living[index] = is_extant(node)
            y[index] = next_tip_y
            next_tip_y += 1
        else:
            has_living[index] = any(has_living[c] for c in node["children"])
            child_ys = [y[c] for c in node["children"]]
            y[index] = (min(child_ys) + max(child_ys)) / 2
    parent = [None] * len(tree)
    for index, node in enumerate(tree):
        for child in node["children"]:
            parent[child] = index
    for index, node in enumerate(tree):
        color = "black" if has_living[index] else "lightgray"
        if parent[index] is not None:
            axes.plot([x[parent[index]], x[index]], [y[index], y[index]],
                      color = color, linewidth = 1)
        if node["children"]:
            child_ys = [y[c] for c in node["children"]]
            axes.plot([x[index], x[index]], [min(child_ys), max(child_ys)],
                      color = color, linewidth = 1)
    axes.set_ylim(-1, next_tip_y)
    axes.invert_yaxis()
    axes.set_yticks([])
    for side in ["left", "right", "top"]:
        axes.spines[side].set_visible(False)
    axes.set_xlabel(time_label)
    axes.set_title(title)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The complete tree versus the reconstructed tree

    The cell below simulates one tree with a birth rate of 1 and a death rate of
    0.5, for 4 units of time.
    On the left is the ***complete tree***, the full history of the clade, with
    the lineages that went extinct in light gray.
    But biologists almost never get to see the complete tree!
    We can usually only observe and collect data from the species that are alive
    today, so the tree we estimate from their DNA is the ***reconstructed tree*** on
    the right: The complete tree with every extinct lineage pruned away (using the
    `prune_tips` function).
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _():
    _rng = random.Random(12)
    example_complete_tree = simulate_tree(1.0, 0.5, 4.0, _rng)
    example_reconstructed_tree = prune_tips(example_complete_tree, is_extant)

    _number_extinct = 0
    for _node in example_complete_tree:
        if _node["extinct"]:
            _number_extinct += 1
    _number_living = len(example_reconstructed_tree) // 2 + 1

    _figure, _axes = plt.subplots(1, 2, figsize = (11, 6), sharex = True)
    draw_tree(example_complete_tree, _axes[0],
              title = f"Complete tree ({_number_living} living, "
              + f"{_number_extinct} extinct)")
    draw_tree(example_reconstructed_tree, _axes[1],
              title = f"Reconstructed tree ({_number_living} living)")
    _figure.tight_layout()
    _figure
    return (example_reconstructed_tree,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `parse_newick` function from the phylogenetics exercise is in the next cell,
    because we will need it below.
    **You do not need to edit it.**
    """)
    return


@app.function
def parse_newick(newick):
    """Convert a Newick tree string into a list of nodes in postorder.

    This is the same function we used in the phylogenetics exercise.

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
        name = newick[start:position].strip().strip("'\"")
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
    ## Counting lineages through time

    A common way to summarize a tree is to count how many lineages there are at
    each point in time, from the root to the present.
    This is called a ***lineages-through-time plot*** (or ***LTT plot***), and it
    is just like the plots of your simulations in Parts 1 and 2!
    For a reconstructed tree, there are 2 lineages at the root, and each
    split (internal node) adds one more lineage.
    So, all we need to make an LTT plot are the times of the splits, which are
    called the ***branching times***.

    ## <font color=red> Challenge 6: Branching times </font>

    Complete the `get_branching_times` function below, which returns the times (from
    the root) of all of the internal nodes of a tree, from earliest (the root) to
    latest (the last split before present).

    A recipe:

    1.  Get the time of every node with
        `node_times = get_node_times(tree)`
    2.  Loop over every node, along with its index, using
        `for index, node in enumerate(tree):`
    3.  If the node has children (it is an internal node), append its time
        (`node_times[index]`) to `branching_times`
    4.  Sort `branching_times` from earliest (the root) to latest (the last split
        before present)

    /// tip
    `enumerate` gives you the index of each item in a list along with the item
    itself, so you know where each node's time is in `node_times`.

    `a_list.sort()` sorts a list in place, from smallest to largest.
    For example, if `numbers = [3, 1, 2]`, after `numbers.sort()`, `numbers`
    is `[1, 2, 3]`.
    Because the tree is in postorder, the root comes **last**, so the times
    won't be in order until you sort them!
    ///
    """)
    return


@app.function
def get_branching_times(tree):
    """Get the times of the internal nodes of a tree, from earliest to latest.

    Args:
        tree (list[dict]): A list of nodes in postorder.

    Returns:
        list[float]: The time (measured from the root) of every node that has
            children, sorted from earliest to latest. The first time is the
            root's, which is 0.

    Examples:
        >>> get_branching_times(parse_newick("((A:1,B:1):2,C:3);"))
        [0.0, 2.0]
    """
    branching_times = []
    # Add your code here!
    return branching_times


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _branching_test_cases = [
        ("((A:1,B:1):2,C:3);", [0.0, 2.0]),
        ("(((A:1,B:1):1,C:2):1,(D:0.5,E:0.5):2.5);", [0.0, 1.0, 2.0, 2.5]),
        ("((A:1,B:1):0.5,(C:0.25,D:0.25):1.25);", [0.0, 0.5, 1.25]),
        ("A;", []),
    ]
    _branching_failures = []
    for _newick, _expected in _branching_test_cases:
        try:
            _found = get_branching_times(parse_newick(_newick))
            if [round(_t, 9) for _t in _found] == _expected:
                continue
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
        _branching_failures.append(
            f"  {_newick}\n    expected {_expected}, got {_found}"
        )

    get_branching_times_works = len(_branching_failures) == 0
    if get_branching_times_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, get_branching_times failed these cases:\n"
              + "\n".join(_branching_failures))
    return (get_branching_times_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `plot_ltt` function below uses the branching times of a tree to draw its
    LTT plot, and the cell after it draws the LTT plot of the reconstructed tree
    from above.
    **You do not need to edit the next two cells.**
    """)
    return


@app.function
def plot_ltt(axes, branching_times, end_time, **style):
    """Draw a lineages-through-time plot on a matplotlib axes.

    Args:
        axes (matplotlib.axes.Axes): The axes to draw on.
        branching_times (list[float]): The branching times of a tree, from
            earliest (the root, at time 0) to latest.
        end_time (float): The time of the present (where the plot ends).
        **style: Any other keyword arguments (like `color`, `alpha`,
            `linewidth`, or `label`) are passed along to `axes.step`.
    """
    times = list(branching_times) + [end_time]
    counts = list(range(2, len(branching_times) + 2))
    counts.append(counts[-1])
    axes.step(times, counts, where = "post", **style)


@app.cell
def _(example_reconstructed_tree, get_branching_times_works, mo):
    mo.stop(
        not get_branching_times_works,
        mo.md("***Waiting — Get your `get_branching_times` function working "
              + "first.***"),
    )

    _figure, _axes = plt.subplots(2, 1, figsize = (7, 7), sharex = True)
    draw_tree(example_reconstructed_tree, _axes[0], title = "Reconstructed tree",
              time_label = "")
    plot_ltt(_axes[1], get_branching_times(example_reconstructed_tree), 4.0,
             color = "black", linewidth = 2)
    _axes[1].set_xlabel("Time since the root")
    _axes[1].set_ylabel("Number of lineages")
    _axes[1].set_title("Lineages through time")
    _figure.tight_layout()
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Estimating extinction from extant lineages

    Given that a tree we estimate from extant lineages (the reconstructed tree)
    lacks all the extinct lineages that evolved in the clade, it is logical to ask:
    **Can we see the signature of extinction in a reconstructed tree?**

    The cell below simulates 30 reconstructed trees under each of two models, for
    8 units of time, and draws their LTT plots on a log-scale y-axis (gray), along
    with the average of each set on the log scale (red).
    The two models have the **same** net diversification rate,
    $r = \lambda - \mu = 0.5$:

    -   **Left**: Pure birth, $\lambda = 0.5$ and $\mu = 0$
    -   **Right**: Lots of extinction, $\lambda = 2$ and $\mu = 1.5$

    The dashed line has a slope of $r$ on the log scale, for comparison.
    This cell runs a lot of simulations, so it might take a few seconds.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(get_branching_times_works, mo):
    mo.stop(
        not get_branching_times_works,
        mo.md("***Waiting — Get your `get_branching_times` function working "
              + "first.***"),
    )

    _rng = random.Random(1994)
    _max_time = 8.0
    _grid = [_i * _max_time / 80 for _i in range(81)]
    _models = [
        ("Pure birth", 0.5, 0.0),
        ("Lots of extinction", 2.0, 1.5),
    ]
    _figure, _axes = plt.subplots(1, 2, figsize = (11, 4.5), sharey = True)
    for _ax, (_name, _birth_rate, _death_rate) in zip(_axes, _models):
        _log_count_sums = [0.0] * len(_grid)
        for _ in range(30):
            _complete = simulate_tree(_birth_rate, _death_rate, _max_time, _rng)
            _times = get_branching_times(prune_tips(_complete, is_extant))
            plot_ltt(_ax, _times, _max_time, color = "gray", alpha = 0.4,
                     linewidth = 1)
            for _g, _t in enumerate(_grid):
                # The number of lineages at time _t is 1 plus the number of
                # splits at or before _t (the root's split makes it 2)
                _count = 1
                for _b in _times:
                    if _b <= _t:
                        _count += 1
                _log_count_sums[_g] += math.log(_count)
        _average = [math.exp(_s / 30) for _s in _log_count_sums]
        _ax.plot(_grid, _average, color = "firebrick", linewidth = 2.5,
                 label = "Average")
        _ax.plot(_grid, [2 * math.exp(0.5 * _t) for _t in _grid],
                 color = "black", linestyle = "--", linewidth = 1,
                 label = "Slope of $r = 0.5$")
        _ax.set_yscale("log")
        _ax.set_title(f"{_name}: $\\lambda$ = {_birth_rate}, $\\mu$ = {_death_rate}")
        _ax.set_xlabel("Time since the root")
        _ax.legend(loc = "upper left")
    _axes[0].set_ylabel("Number of lineages")
    _figure.tight_layout()
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 7: The pull of the present </font>

    Double-click this cell and answer the questions below.

    1.  **Both models have the same net diversification rate. How do the shapes of
        their LTT plots differ, especially near the present (the right side)?**

        **Answer**:

    2.  **With lots of extinction, why do you think the number of lineages in the
        reconstructed tree rises so quickly near the present? (Hint: Look back at
        the complete and reconstructed trees we plotted above.
        Which lineages are missing from the reconstructed tree, and when did they
        arise?)**

        **Answer**:

    3.  **Biologists usually have only one reconstructed tree for a group of
        species.
        Based on these plots, why do you think it is hard to estimate the extinction
        rate from a tree of living species?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 4: The bent-toed geckos

    Let's compare our model to a real tree!
    Bent-toed geckos (genus *Cyrtodactylus*) are the most species-rich
    genera of geckos, with 406 described species, and new species are still being
    described at a high rate.
    Grismer *et al.* (2022) estimated a ***time-calibrated tree*** of 345 species of
    bent-toed geckos from their DNA, with branch lengths in millions of years.
    Their tree also includes 19 species from other genera (an ***outgroup***),
    which help estimate the location of the tree's root.

    The next cell downloads their tree, and uses our `prune_tips` function to
    remove the outgroup species, whose names start with a capital letter (the
    names of the *Cyrtodactylus* species start with a lowercase letter).
    That's the same function we used to prune extinct lineages, but now we give
    it a different `keep_func` function!
    **You do not need to edit the next three cells.**
    """)
    return


@app.function
def read_nexus_tree_url(url):
    """Download the first tree in a NEXUS file, and parse it.

    Comments in square brackets (like the annotations that BEAST adds to its
    trees) are removed, and numbers in the tree are replaced by taxon names, if
    the file has a "translate" table.

    Args:
        url (str): The URL of a NEXUS file.

    Returns:
        list[dict]: The tree as a list of nodes in postorder.
    """
    import re
    import urllib.request

    with urllib.request.urlopen(url) as response:
        text = response.read().decode("utf-8")
    # Remove comments in square brackets
    text = re.sub(r"\[.*?\]", "", text, flags = re.S)
    # Read the "translate" table, if there is one
    translate = {}
    translate_match = re.search(r"\btranslate\b(.*?);", text,
                                flags = re.S | re.I)
    if translate_match:
        for entry in translate_match.group(1).split(","):
            parts = entry.split()
            if len(parts) >= 2:
                translate[parts[0]] = parts[1].strip("'\"")
    tree_match = re.search(r"^\s*tree\s+[^=]+=\s*(.*?;)", text,
                           flags = re.S | re.I | re.M)
    if tree_match is None:
        raise ValueError("Couldn't find a tree in the NEXUS file.")
    tree = parse_newick(tree_match.group(1))
    for node in tree:
        if node["name"] in translate:
            node["name"] = translate[node["name"]]
    return tree


@app.function
def is_bent_toed_gecko(node):
    """Return True if a tip's name starts with a lowercase letter."""
    return node["name"][0].islower()


@app.cell
def _(mo):
    _full_tree = read_nexus_tree_url(GECKO_TREE_URL)
    gecko_tree = prune_tips(_full_tree, is_bent_toed_gecko)

    _gecko_times = get_node_times(gecko_tree)
    gecko_tip_count = len(gecko_tree) // 2 + 1
    gecko_crown_age = max(_gecko_times)

    _figure, _axes = plt.subplots(figsize = (7, 9))
    draw_tree(gecko_tree, _axes,
              title = f"Cyrtodactylus ({gecko_tip_count} species)",
              time_label = "Millions of years since the root")
    _figure.tight_layout()
    mo.vstack([
        mo.md(
            f"The full tree has {len(_full_tree) // 2 + 1} tips. "
            + f"After removing the outgroup, the *Cyrtodactylus* tree has "
            + f"**{gecko_tip_count}** tips, and its root is "
            + f"**{gecko_crown_age:.1f}** million years old."
        ),
        _figure,
    ])
    return gecko_crown_age, gecko_tip_count, gecko_tree


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Estimating the birth rate

    If we assume the geckos diversified under a pure-birth model, what birth rate
    best explains their tree?
    For a reconstructed tree with $n$ tips that starts at the root, the maximum
    likelihood estimate of the birth rate is surprisingly simple:

    $$
    \hat{\lambda} = \frac{n - 2}{L}
    $$

    where $L$ is the sum of the lengths of all of the branches in the tree.
    This makes sense: The tree has $n - 2$ splits after the root, and $L$ is the
    total amount of time that lineages had to split, so $\hat{\lambda}$ is the
    number of splits per lineage per unit of time.

    ## <font color=red> Challenge 8: Estimating the birth rate </font>

    Complete the `estimate_birth_rate` function below.
    A recipe:

    1.  Loop over every `node` in `tree`
    2.  If the node has no children, add 1 to `number_of_tips`
    3.  If the node's branch length is not `None` (the root's is `None`), add it
        to `total_length`
    4.  After the loop, set `birth_rate` to the maximum-likelihood estimate of the
        birth rate under a pure-birth model, using the equation above.

    /// tip
    To check whether a value is not `None`, use `if value is not None:`.
    ///
    """)
    return


@app.function
def estimate_birth_rate(tree):
    """Estimate the birth rate of a reconstructed tree under the pure-birth model.

    Args:
        tree (list[dict]): A reconstructed tree (starting at the root), as a
            list of nodes in postorder.

    Returns:
        float: The maximum likelihood estimate of the birth rate,
            (number of tips - 2) / (sum of the branch lengths).

    Examples:
        >>> estimate_birth_rate(parse_newick("((A:1,B:1):1,C:2);"))
        0.2
    """
    number_of_tips = 0
    total_length = 0.0
    birth_rate = 0.0
    # Add your code here!
    return birth_rate


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    estimate_birth_rate_works = True
    _messages = []
    _rate_test_cases = [
        ("((A:1,B:1):1,C:2);", 0.2),
        ("((A:1,B:1):1,(C:1,D:1):1);", 2 / 6),
        ("(((A:0.5,B:0.5):0.5,C:1):1,(D:1.5,E:1.5):0.5);", 3 / 7),
    ]
    for _newick, _expected in _rate_test_cases:
        try:
            _found = estimate_birth_rate(parse_newick(_newick))
            if abs(_found - _expected) < 1e-9:
                continue
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
        estimate_birth_rate_works = False
        _messages.append(f"{_newick}\n    expected {_expected:.4f}, got {_found}")

    # Simulated pure-birth trees should give estimates close to the true rate
    if estimate_birth_rate_works:
        _rng = random.Random(8)
        _estimates = []
        for _ in range(20):
            _estimates.append(estimate_birth_rate(simulate_tree(0.5, 0.0, 10.0, _rng)))
        _mean = sum(_estimates) / len(_estimates)
        print(f"20 trees simulated with a birth rate of 0.5: average estimate "
              + f"of {_mean:.3f}")
        if not (0.45 < _mean < 0.55):
            estimate_birth_rate_works = False
            _messages.append("Estimates from simulated trees are off.")

    if estimate_birth_rate_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, estimate_birth_rate failed these cases:")
        for _message in _messages:
            print("  " + _message)
    return (estimate_birth_rate_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Do the geckos look like a pure-birth process?

    To compare the **shape** of the gecko tree's LTT plot to the pure-birth model,
    we want simulated trees that start and end at the same place as the gecko
    tree: 2 lineages at a root that is the same age, and 345 tips at the present.
    The `simulate_tree_with_tips` function below does that.
    It simulates splits, one at a time, until the tree has the number of tips we
    ask for, and then uses the `stretch_tree` function to stretch (or shrink)
    every branch so that the root is the age we ask for.
    **You do not need to edit the next three cells.**

    The cell after the two functions estimates the birth rate of the gecko tree
    with your function, and draws the LTT plots of 100 simulated trees (gray) and
    the gecko tree (red), on a log-scale y-axis.
    """)
    return


@app.function
def simulate_tree_with_tips(number_of_tips, root_age, rng):
    """Simulate a pure-birth tree with a set number of tips and root age.

    Splits are simulated one at a time (with a birth rate of 1), starting from
    2 lineages at the root, until there are `number_of_tips` lineages. Then, a
    final waiting time until the present is drawn, and every branch is
    stretched (or shrunk) so the root is `root_age` units of time old.

    Args:
        number_of_tips (int): The number of tips in the tree (at least 2).
        root_age (float): The time from the root to the present.
        rng (random.Random): The random number generator to use.

    Returns:
        list[dict]: The tree as a list of nodes in postorder. Tips are named
            "t1", "t2", and so on.
    """
    start_time = [0.0, 0.0, 0.0]
    end_time = [0.0, None, None]
    children = [[1, 2], [], []]
    living = [1, 2]
    clock = 0.0
    while True:
        clock += rng.expovariate(len(living))
        if len(living) >= number_of_tips:
            break
        lineage = living.pop(rng.randrange(len(living)))
        end_time[lineage] = clock
        for _ in range(2):
            start_time.append(clock)
            end_time.append(None)
            children.append([])
            children[lineage].append(len(start_time) - 1)
            living.append(len(start_time) - 1)
    for lineage in living:
        end_time[lineage] = clock
    tree = lineages_to_tree(children, start_time, end_time,
                            [False] * len(start_time))
    return stretch_tree(tree, root_age)


@app.function
def stretch_tree(tree, root_age):
    """Multiply every branch length so the root is `root_age` from the present.

    Args:
        tree (list[dict]): A list of nodes in postorder, with every tip at the
            present.
        root_age (float): The new time from the root to the present.

    Returns:
        list[dict]: A stretched copy of the tree.
    """
    scale = root_age / max(get_node_times(tree))
    stretched = []
    for node in tree:
        new_node = dict(node)
        if new_node["length"] is not None:
            new_node["length"] *= scale
        stretched.append(new_node)
    return stretched


@app.cell
def _(
    estimate_birth_rate_works,
    gecko_crown_age,
    gecko_tip_count,
    gecko_tree,
    get_branching_times_works,
    mo,
):
    mo.stop(
        not (estimate_birth_rate_works and get_branching_times_works),
        mo.md("***Waiting — Get your `estimate_birth_rate` and "
              + "`get_branching_times` functions working first.***"),
    )

    gecko_birth_rate = estimate_birth_rate(gecko_tree)
    _rng = random.Random(2022)
    _figure, _axes = plt.subplots(figsize = (7, 4.5))
    for _ in range(100):
        _simulated = simulate_tree_with_tips(gecko_tip_count, gecko_crown_age, _rng)
        plot_ltt(_axes, get_branching_times(_simulated), gecko_crown_age,
                 color = "gray", alpha = 0.25, linewidth = 1)
    plot_ltt(_axes, get_branching_times(gecko_tree), gecko_crown_age,
             color = "firebrick", linewidth = 2.5, label = "Cyrtodactylus")
    _axes.set_yscale("log")
    _axes.set_title(f"Simulated pure-birth trees with {gecko_tip_count} species")
    _axes.set_xlabel("Millions of years since the root")
    _axes.set_ylabel("Number of lineages")
    _axes.legend(loc = "upper left")
    _figure.tight_layout()

    mo.vstack([
        mo.md(
            f"Estimated birth rate: **{gecko_birth_rate:.4f}** splits per lineage "
            + "per million years."
        ),
        _figure,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 9: Bent-toed gecko diversification </font>

    Double-click this cell and answer the questions below.

    1.  **What is your estimate of the birth rate of bent-toed geckos? On average,
        about how many millions of years does a gecko lineage wait before it
        splits (Hint: The average waiting time is $1 / \lambda$)?**

        **Answer**:

    2.  **Is the gecko tree consistent with a constant-rate pure-birth process? If
        not, where (early, in the middle, or near the present) does it differ from
        the simulated trees?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How many bent-toed geckos are there?

    Our simulated trees include **every** species in the clade, but the gecko tree
    doesn't.
    It is missing at least 61 of the 406 described species, and new species of
    bent-toed geckos are still being described at a high rate, so there are
    probably many more species yet to be described.

    How do missing species change the shape of an LTT plot?
    Every species we leave out of a tree removes one split: the split between that
    species and its closest relative.
    To see what this does, we can simulate trees with more species than the gecko
    tree has, and then keep only 345 of the tips, chosen at random, as if we only
    had DNA from 345 of the species.
    Then we can ask: **How many species would bent-toed geckos need to have for a
    pure-birth model to explain their tree?**

    ## <font color=red> Challenge 10: Simulating an incomplete tree </font>

    Complete the `simulate_sampled_tree` function below, which simulates a tree
    with `total_species` tips, and returns the tree of `number_sampled` of them,
    chosen at random.
    A recipe:

    1.  Simulate a tree with every species, using
        `complete_tree = simulate_tree_with_tips(total_species, root_age, rng)`
    2.  Make a list of the names of the tips of `complete_tree` (the nodes with no
        children) called `tip_names`.
        To do this, create an empty list, `tip_names = []` and then loop over the
        nodes in `complete_tree`; if a node is a tip, add its name to `tip_names`.
    3.  Choose the names of the tips to keep, at random, using
        `kept_names = set(rng.sample(tip_names, number_sampled))`
    4.  Define a function called `is_sampled` inside the `simulate_sampled_tree
        function can be given to the `prune_tips` function as the `keep_func`
        argument.
        The `is_sampled` function should return `True` if a node's name is in
        `kept_names` (see the tip below)
    5.  Prune the other tips from the tree using the `prune_tips` function, and then
        stretch the pruned tree so its root is `root_age` using the `stretch_tree`
        function.
        Assign the tree returned by `stetch_tree` to `sampled_tree`.

    /// tip
    `rng.sample(a_list, k)` returns a new list of `k` items chosen at random from
    `a_list`, without repeating any of them (*i.e.*, `rng.sample` samples items
    **without** replacement).

    We turn that list into a ***set*** with `set()`, because, as we saw in the
    complexity exercise, checking whether an item is `in` a set is much faster
    than checking whether it is `in` a list.

    You can define a function **inside** another function, and the inner function
    can use the variables of the outer function.
    For example, inside `simulate_sampled_tree`, the following defines a function
    that uses `kept_names`:

    ```python
    def is_sampled(node):
        return node["name"] in kept_names
    ```

    Then, you can give `is_sampled` to `prune_tips` (as the `keep_func` argument),
    just like we gave it `is_extant` and `is_bent_toed_gecko` (without parentheses,
    because we are giving `prune_tips` the function itself, not calling it).
    ///

    /// details | Why do we need to stretch the pruned tree?
    When we prune tips, every split that leads to a tip we removed disappears.
    If, by chance, we remove **every** tip on one side of the root, the root
    itself disappears, and the pruned tree's root is younger than `root_age`.
    That is rare when we keep many of the tips, but `stretch_tree` makes sure every
    simulated tree has the same root age as the gecko tree.
    ///
    """)
    return


@app.function
def simulate_sampled_tree(total_species, number_sampled, root_age, rng):
    """Simulate a pure-birth tree, and keep a random sample of its tips.

    Args:
        total_species (int): The number of tips in the complete tree.
        number_sampled (int): The number of tips to keep (no more than
            `total_species`).
        root_age (float): The age of the root of the returned tree.
        rng (random.Random): The random number generator to use.

    Returns:
        list[dict]: The tree of the sampled tips, as a list of nodes in
            postorder, with its root `root_age` units of time from the present
            (or None, until the function is complete).

    Examples:
        >>> tree = simulate_sampled_tree(100, 10, 5.0, random.Random(1))
        >>> len(get_branching_times(tree)) + 1
        10
    """
    sampled_tree = None
    # Add your code here!
    return sampled_tree


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    simulate_sampled_tree_works = True
    _messages = []

    def _tip_names(tree):
        _names = []
        for _node in tree:
            if len(_node["children"]) == 0:
                _names.append(_node["name"])
        return _names

    try:
        # Test 1: The tree has the right number of tips and root age
        _tree = simulate_sampled_tree(100, 10, 5.0, random.Random(1))
        if not isinstance(_tree, list):
            simulate_sampled_tree_works = False
            _messages.append(
                f"Your function should return a list of nodes, not "
                + f"{type(_tree).__name__}."
            )
        else:
            _names = _tip_names(_tree)
            if len(_names) != 10:
                simulate_sampled_tree_works = False
                _messages.append(
                    f"With number_sampled = 10, the tree should have 10 tips, "
                    + f"not {len(_names)}. Did you prune the tree?"
                )
            elif len(set(_names)) != 10:
                simulate_sampled_tree_works = False
                _messages.append("Some tips are in the tree more than once.")
            _age = max(get_node_times(_tree))
            if abs(_age - 5.0) > 1e-9:
                simulate_sampled_tree_works = False
                _messages.append(
                    f"The root should be 5.0 units of time old, not {_age:.4f}."
                )
            for _node in _tree:
                if len(_node["children"]) not in (0, 2):
                    simulate_sampled_tree_works = False
                    _messages.append(
                        "Every internal node should have 2 children. Are you "
                        + "using prune_tips?"
                    )
                    break

        # Test 2: The tips should be chosen at random, not always the same ones
        if simulate_sampled_tree_works:
            _rng = random.Random(2)
            _seen = set()
            for _ in range(20):
                _seen.update(_tip_names(simulate_sampled_tree(100, 10, 5.0, _rng)))
            if len(_seen) < 50:
                simulate_sampled_tree_works = False
                _messages.append(
                    "The same tips are kept every time. Are you choosing them at "
                    + "random with rng.sample?"
                )

        # Test 3: Even when only 2 tips are kept, the root age should be right,
        # so the tree must be stretched after it is pruned
        if simulate_sampled_tree_works:
            _rng = random.Random(3)
            for _ in range(50):
                _age = max(get_node_times(simulate_sampled_tree(30, 2, 5.0, _rng)))
                if abs(_age - 5.0) > 1e-9:
                    simulate_sampled_tree_works = False
                    _messages.append(
                        "Sometimes the root is not root_age units of time old. Did "
                        + "you stretch the tree after pruning it?"
                    )
                    break

        # Test 4: The same seed should give the same tree
        if simulate_sampled_tree_works:
            _first = simulate_sampled_tree(50, 10, 5.0, random.Random(4))
            _second = simulate_sampled_tree(50, 10, 5.0, random.Random(4))
            if _first != _second:
                simulate_sampled_tree_works = False
                _messages.append("Make sure every random draw uses rng.")

    except Exception as _error:
        simulate_sampled_tree_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )
        if "not callable" in str(_error):
            _messages.append(
                "Did you give prune_tips your function itself, without "
                + "parentheses (e.g., is_sampled, not is_sampled(node))?"
            )

    if simulate_sampled_tree_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your simulate_sampled_tree function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (simulate_sampled_tree_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exploring how many species there are

    Use the slider below to determine the total number of species of bent-toed
    geckos (assuming a pure-birth model).
    The second cell below uses your `simulate_sampled_tree` function to simulate 100
    pure-birth trees with the number of species indicated by the slider, keeps 345
    of the species in each one, and draws their LTT plots (gray), along with the LTT
    plot of the gecko tree (red).
    Start at 406 (the number of described species), and slowly move the slider to
    the right.
    Each time you move the slider, the plot updates, which might take a few
    seconds.
    **You do not need to edit the next two cells.**
    """)
    return


@app.cell
def _(mo):
    # Create a slider for controlling the number of species
    total_species_slider = mo.ui.slider(
        start = 406,
        stop = 2006,
        step = 100,
        value = 406,
        show_value = True,
        label = "Total number of species of bent-toed geckos",
    )
    return (total_species_slider,)


@app.cell
def _(
    gecko_crown_age,
    gecko_tip_count,
    gecko_tree,
    get_branching_times_works,
    mo,
    simulate_sampled_tree_works,
    total_species_slider,
):
    mo.stop(
        not (simulate_sampled_tree_works and get_branching_times_works),
        mo.md("***Waiting — Get your `simulate_sampled_tree` and "
              + "`get_branching_times` functions working first.***"),
    )

    _total = total_species_slider.value
    _rng = random.Random(2022)
    _figure, _axes = plt.subplots(figsize = (7, 4.5))
    for _ in range(100):
        _sampled = simulate_sampled_tree(_total, gecko_tip_count, gecko_crown_age,
                                         _rng)
        plot_ltt(_axes, get_branching_times(_sampled), gecko_crown_age,
                 color = "gray", alpha = 0.25, linewidth = 1)
    plot_ltt(_axes, get_branching_times(gecko_tree), gecko_crown_age,
             color = "firebrick", linewidth = 2.5, label = "Cyrtodactylus")
    _axes.set_yscale("log")
    _axes.set_title(f"Simulated trees with {gecko_tip_count} of {_total} species")
    _axes.set_xlabel("Millions of years since the root")
    _axes.set_ylabel("Number of lineages")
    _axes.legend(loc = "upper left")
    _figure.tight_layout()

    mo.vstack([
        mo.md(
            "**Adjust the slider to determine the number of bent-toed gecko "
            + "species (assuming a pure-birth model)**."
        ),
        total_species_slider,
        _figure,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 11: Undescribed geckos </font>

    Double-click this cell and answer the questions below.

    1.  **As you increase the total number of species, how does the shape of the
        simulated LTT plots change? At about what total number of species do the
        simulated trees match the gecko tree well? So, under a pure-birth model,
        about how many species of bent-toed geckos remain undescribed (or are
        otherwise missing from the tree)?**

        **Answer**:

    2.  **Other than undescribed species, what else could cause the LTT plot of the
        gecko tree to flatten out near the present?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    -   In a **birth-death model**, each lineage splits at rate $\lambda$ and goes
        extinct at rate $\mu$; with $n$ lineages, the waiting time to the next event
        is exponential with a total rate of $n(\lambda + \mu)$
    -   The **Gillespie algorithm** simulates such a process one event at a time:
        Draw a waiting time from the total rate, then choose which event happened
    -   Without extinction, lineages grow **exponentially**, which looks like a
        straight line on a log scale
    -   Even when the birth rate is higher than the death rate, **many clades go
        extinct**, and the ones that survive are bigger than average, so living
        clades are a biased sample
    -   We usually see only the **reconstructed tree** of living species; extinction
        leaves a subtle signature in it, which is called the **pull of the present**
    -   Under a pure-birth model, the birth rate of a tree can be estimated as
        $(n - 2) / L$
    -   **Missing species** remove recent splits, which flattens an LTT plot near
        the present; by simulating trees with missing species, we can ask how many
        species a clade would need to have for a model to explain its tree

    Birth-death models are used across many fields of biology. For example, the
    same models, with "birth" as infection and "death" as recovery, describe
    the spread of an epidemic!
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

    The tree of bent-toed geckos is from Grismer, L. L., N. A. Poyarkov,
    E. S. H. Quah, J. L. Grismer, and P. L. Wood Jr. (2022), The biogeography of
    bent-toed geckos, *Cyrtodactylus* (Squamata: Gekkonidae), *PeerJ* 10:e13153
    ([doi:10.7717/peerj.13153](https://doi.org/10.7717/peerj.13153)).
    The pure-birth model is from Yule (1925), *Philosophical Transactions of the
    Royal Society B* 213:21–87; the extinction probabilities are from Kendall
    (1948), *Annals of Mathematical Statistics* 19:1–15; the Gillespie algorithm
    is from Gillespie (1977), *Journal of Physical Chemistry* 81:2340–2361; and
    the pull of the present is from Nee, May, and Harvey (1994), *Philosophical
    Transactions of the Royal Society B* 344:305–311.
    I used Anthropic's Claude (Opus 5.5 model) to help draft this notebook.
    """)
    return


if __name__ == "__main__":
    app.run()
