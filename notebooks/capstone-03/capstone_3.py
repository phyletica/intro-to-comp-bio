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

    # The 1978 influenza outbreak at a boarding school (see the
    # Acknowledgements at the end of the notebook for the source)
    SCHOOL_SIZE = 763
    OUTBREAK_DAYS = list(range(1, 15))
    OUTBREAK_DATES = [
        "Jan 22", "Jan 23", "Jan 24", "Jan 25", "Jan 26", "Jan 27", "Jan 28",
        "Jan 29", "Jan 30", "Jan 31", "Feb 1", "Feb 2", "Feb 3", "Feb 4",
    ]
    # The number of boys confined to bed on each day
    IN_BED = [3, 8, 26, 76, 225, 298, 258, 233, 189, 128, 68, 29, 14, 4]


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Capstone Project 3: Influenza at a boarding school

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

    In January 1978, influenza swept through a boarding school for boys in the
    north of England.
    The virus was a strain of H1N1 influenza that had not circulated in people
    since the 1950s, so none of the boys had immunity to it.
    In just two weeks, 512 of the 763 boys at the school were sick enough to be
    confined to bed.
    The school's doctors counted how many boys were in bed each day (plotted in the
    next cell), and these counts have become one of the most famous datasets in
    epidemiology.

    In the birth-death exercise, we simulated lineages that split and die.
    In this project, the "lineages" will be **infections**: An infected person
    passes the virus on to someone else ("birth"), or recovers ("death").
    You will use this idea to answer three questions:

    1.  **When one infected person arrives, how often does a big outbreak
        follow?**
    2.  **What makes an outbreak grow, peak, and end?**
    3.  **How contagious was the virus at the boarding school?**

    To answer them, you will:

    1.  Simulate outbreaks one event at a time, with the Gillespie algorithm
    2.  Find out how often an outbreak dies out on its own, and connect it to the
        extinction of clades from the birth-death exercise
    3.  Use ***Euler's method*** to calculate the average course of an outbreak
    4.  Fit the model to the counts from the boarding school

    /// attention | This project is graded for correctness
    Unlike the lab exercises, which are graded for effort, this project is graded
    for correctness.
    The number of points each challenge is worth is listed in its heading.
    Each code challenge has a test cell to help you check your work.
    ///

    **You do not need to edit the next cell.**
    It plots the number of boys confined to bed each day during the 1978 influenza
    outbreak at the English boarding school.
    """)
    return


@app.cell
def _():
    _figure, _axes = plt.subplots(figsize = (8, 4))
    _axes.bar(OUTBREAK_DAYS, IN_BED, color = "steelblue")
    _axes.set_xticks(OUTBREAK_DAYS, OUTBREAK_DATES, rotation = 45)
    _axes.set_xlabel("Date (1978)")
    _axes.set_ylabel("Number of boys in bed")
    _axes.set_title(f"Influenza at a boarding school with {SCHOOL_SIZE} boys")
    _figure.tight_layout()
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tools from previous exercises

    The function below is from the birth-death exercise.
    **You do not need to edit it**, but you will use it as a model for your first
    function.
    As a reminder, `simulate_birth_death(birth_rate, death_rate, max_time, rng)`
    starts with one lineage and uses the ***Gillespie algorithm*** to simulate
    splits and extinctions, one event at a time, using the following steps:

    1.  Calculate the **total rate** of all the events that can happen
    2.  Draw an exponential **waiting time** with that total rate, and move the
        clock forward
    3.  Choose **which event** happened, with probability proportional to its rate
    4.  Record the time and the number of lineages, and repeat
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
        total_rate = lineages * (birth_rate + death_rate)
        waiting_time = rng.expovariate(total_rate)
        clock += waiting_time
        if clock > max_time:
            break
        if rng.random() < birth_rate / (birth_rate + death_rate):
            lineages += 1
        else:
            lineages -= 1
        times.append(clock)
        counts.append(lineages)
    times.append(max_time)
    counts.append(lineages)
    return times, counts


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: Simulating an outbreak

    ## The SIR model

    The ***SIR model*** (Kermack and McKendrick, 1927) divides a population of
    $N$ people into three groups:

    -   $S$: ***Susceptible*** people, who can catch the virus
    -   $I$: ***Infected*** people, who have the virus and can pass it on
    -   $R$: ***Recovered*** people, who are immune, and can't catch it again

    Everyone starts out susceptible, except for a few infected people.
    Then, two kinds of events happen:

    1.  ***Infection***: An infected person passes the virus to a susceptible
        person, so $S$ goes down by 1, and $I$ goes up by 1
    2.  ***Recovery***: An infected person recovers, so $I$ goes down by 1, and
        $R$ goes up by 1

    Each infected person recovers at a ***recovery rate*** of $\gamma$ (the Greek
    letter "gamma") per day, so the average time a person is infectious is
    $1 / \gamma$ days.
    With $I$ infected people, recoveries happen at a total rate of $\gamma I$,
    just like extinctions in a birth-death model happen at a total rate of
    $\mu n$.

    Infections are a little different.
    Each infected person has contact with others, and passes on the virus at a
    ***transmission rate*** of $\beta$ (the Greek letter "beta") per day.
    But a contact only causes an infection if the other person is susceptible,
    and only a fraction, $S / N$, of the population is susceptible.
    So, with $I$ infected people, infections happen at a total rate of:

    $$
    \beta I \frac{S}{N} = \frac{\beta S I}{N}
    $$

    At the start of an outbreak, almost everyone is susceptible, so $S / N$ is
    close to 1, and each infected person causes new infections at a rate of
    about $\beta$, just like each lineage splits at a rate of $\lambda$ in a
    birth-death model.
    But as more people get infected and recover, $S / N$ shrinks, and the virus
    runs out of people to infect.

    ## The basic reproduction number

    The ***basic reproduction number***, $R_0$ ("R naught"), is the average number
    of people an infected person infects, when everyone else is susceptible.
    An infected person infects others at a rate of $\beta$ per day, for an average
    of $1 / \gamma$ days, so:

    $$
    R_0 = \beta \frac{1}{\gamma} = \frac{\beta}{\gamma}
    $$

    /// note
    The "R" in $R_0$ has nothing to do with the "R" (recovered) in "SIR".
    The two names just happen to share a letter.
    ///

    ## <font color=red> Challenge 1: Simulating an outbreak (4 points) </font>

    Complete the `simulate_sir` function below, which uses the Gillespie algorithm
    to simulate an outbreak one event at a time, until no one is infected.
    The function already sets up the starting numbers, the clock, and the records,
    and has the loop.
    Inside the loop, under the "`Add your code here!`" comment, write code to:

    1.  Calculate the total rate of **infections**,
        $\beta S I / N$, and the total rate of **recoveries**, $\gamma I$
    2.  Add them to get the **total rate** of events
    3.  Draw a **waiting time** with the `rng.expovariate` function, and add it to
        `clock`
    4.  Choose **which event** happened: With probability
        $\text{(infection rate)} / \text{(total rate)}$, it's an infection
        (subtract 1 from `susceptible`, and add 1 to `infected`); otherwise, it's a
        recovery (subtract 1 from `infected`)
    5.  **Record** the event, by appending `clock` to `times`, `susceptible` to
        `susceptible_counts`, and `infected` to `infected_counts`

    /// tip
    Look at the `simulate_birth_death` function above.
    Your loop will look a lot like the one in that function!
    The main differences are the rates, and that an infection changes **two**
    numbers (`susceptible` and `infected`).
    Unlike `simulate_birth_death`, there's no `max_time`, because every outbreak
    ends on its own.
    ///

    /// note
    We don't need to keep track of the number of recovered people, because it is
    always equal to `population_size - susceptible - infected`.
    ///

    /// attention
    Leave the `if number_of_events > 2 * population_size + 10:` check at the top of
    the loop in place.
    If something is wrong with your code (for example, if no event ever changes
    the number of infected people), it stops the function with an error, instead
    of letting it loop forever and freeze your notebook.
    ///
    """)
    return


@app.function
def simulate_sir(population_size, initial_infected, transmission_rate,
                 recovery_rate, rng):
    """Simulate an outbreak under the SIR model with the Gillespie algorithm.

    The simulation runs until no one is infected.

    Args:
        population_size (int): The number of people in the population (N).
        initial_infected (int): The number of people infected at time 0.
        transmission_rate (float): The rate at which an infected person passes
            on the virus, when everyone else is susceptible (beta, per day).
        recovery_rate (float): The rate at which an infected person recovers
            (gamma, per day).
        rng (random.Random): The random number generator to use.

    Returns:
        tuple[list[float], list[int], list[int]]: The times of the events, and
            the numbers of susceptible and infected people right after each
            event. The lists start with time 0 (and the starting numbers).

    Examples:
        >>> simulate_sir(10, 0, 1.0, 0.5, random.Random(1))
        ([0.0], [10], [0])
    """
    susceptible = population_size - initial_infected
    infected = initial_infected
    clock = 0.0
    times = [0.0]
    susceptible_counts = [susceptible]
    infected_counts = [infected]
    number_of_events = 0
    while infected > 0:
        number_of_events += 1
        if number_of_events > 2 * population_size + 10:
            raise RuntimeError(
                "Too many events! Each person can only be infected once and "
                + "recover once. Did you add your code inside the loop? Is your "
                + "infection rate beta * S * I / N, and does each event change "
                + "the right numbers?"
            )
        # Add your code here!
    return times, susceptible_counts, infected_counts


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    simulate_sir_works = True
    _messages = []

    try:
        # Test 1: With no one infected, nothing happens
        _result = simulate_sir(10, 0, 1.0, 0.5, random.Random(1))
        if _result != ([0.0], [10], [0]):
            simulate_sir_works = False
            _messages.append(
                "With 0 infected people, the result should be "
                + f"([0.0], [10], [0]), not {_result}."
            )

        # Test 2: Each event should be one infection or one recovery
        _times, _susceptible, _infected = simulate_sir(50, 2, 1.5, 0.5,
                                                       random.Random(2))
        if not (len(_times) == len(_susceptible) == len(_infected)):
            simulate_sir_works = False
            _messages.append("The three lists should all have the same length.")
        elif len(_times) < 3:
            simulate_sir_works = False
            _messages.append("Your function should record every event.")
        else:
            if (_times[0], _susceptible[0], _infected[0]) != (0.0, 48, 2):
                simulate_sir_works = False
                _messages.append("The records should start with the starting numbers.")
            if _infected[-1] != 0:
                simulate_sir_works = False
                _messages.append("The outbreak should end with 0 infected people.")
            for _k in range(1, len(_times)):
                _change = (_susceptible[_k] - _susceptible[_k - 1],
                           _infected[_k] - _infected[_k - 1])
                if _change not in [(-1, 1), (0, -1)]:
                    simulate_sir_works = False
                    _messages.append(
                        "Each event should be an infection (susceptible - 1, "
                        + "infected + 1) or a recovery (infected - 1)."
                    )
                    break
                if not (_times[_k] > _times[_k - 1]):
                    simulate_sir_works = False
                    _messages.append(
                        "The time of each event should be later than the last. "
                        + "Are you adding the waiting time to the clock?"
                    )
                    break

        # Test 3: With a transmission rate of 0, the one infected person just
        # recovers, after an average of 1 / recovery_rate = 2 days
        if simulate_sir_works:
            _rng = random.Random(3)
            _recovery_times = []
            for _ in range(2000):
                _times, _susceptible, _infected = simulate_sir(50, 1, 0.0, 0.5, _rng)
                if _susceptible[-1] != 49 or len(_times) != 2:
                    simulate_sir_works = False
                    _messages.append(
                        "With a transmission rate of 0, no one should be infected."
                    )
                    break
                _recovery_times.append(_times[-1])
            if simulate_sir_works:
                _mean = sum(_recovery_times) / len(_recovery_times)
                print(f"Transmission rate 0, recovery rate 0.5: average time to "
                      + f"recover was {_mean:.2f} days (expected 2.00)")
                if not (1.85 < _mean < 2.15):
                    simulate_sir_works = False
                    _messages.append(
                        "The average time to recover is off. Did you give "
                        + "rng.expovariate the total rate (not the average "
                        + "waiting time)?"
                    )

        # Test 4: With beta = 1 and gamma = 0.5, the first infected person
        # recovers before infecting anyone with probability
        # 0.5 / (1 + 0.5) = 1/3
        if simulate_sir_works:
            _rng = random.Random(4)
            _no_spread = 0
            _sizes = []
            for _ in range(2000):
                _times, _susceptible, _infected = simulate_sir(200, 1, 1.0, 0.5, _rng)
                if _susceptible[-1] == 199:
                    _no_spread += 1
                _sizes.append(200 - _susceptible[-1])
            _fraction = _no_spread / 2000
            print(f"Beta 1, gamma 0.5: {_fraction:.3f} of outbreaks stopped with "
                  + "the first person (expected 0.333)")
            if not (0.30 < _fraction < 0.37):
                simulate_sir_works = False
                _messages.append(
                    "The fraction of outbreaks that stop with the first person "
                    + "is off. Is the probability of an infection the infection "
                    + "rate divided by the total rate?"
                )
            # Test 5: Big outbreaks should infect about 80% of the population
            _big = []
            for _size in _sizes:
                if _size >= 20:
                    _big.append(_size / 200)
            if len(_big) > 0:
                _mean_big = sum(_big) / len(_big)
                print(f"Beta 1, gamma 0.5: big outbreaks infected {_mean_big:.3f} "
                      + "of the population, on average (expected about 0.80)")
            else:
                _mean_big = 0.0
            if not (0.75 < _mean_big < 0.84):
                simulate_sir_works = False
                _messages.append(
                    "Big outbreaks infect the wrong fraction of the population. "
                    + "Is your infection rate beta * S * I / N?"
                )

        # Test 6: The same seed should give the same results
        _first = simulate_sir(50, 1, 1.5, 0.5, random.Random(6))
        _second = simulate_sir(50, 1, 1.5, 0.5, random.Random(6))
        if _first != _second:
            simulate_sir_works = False
            _messages.append("Make sure every random draw uses rng.")

    except Exception as _error:
        simulate_sir_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )

    print()
    if simulate_sir_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your simulate_sir function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (simulate_sir_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below uses your `simulate_sir` function to simulate outbreaks that
    each start with one infected person, in a school the size of our boarding
    school (763 people), with $\beta = 1$ and $\gamma = 0.5$ per day (so
    $R_0 = 2$).
    The left plot shows the number of infected people over time in 20 simulated
    outbreaks.
    The right plot is a histogram of the total number of people infected (at any
    time) in each of 1,000 simulated outbreaks.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(mo, simulate_sir_works):
    mo.stop(
        not simulate_sir_works,
        mo.md("***Waiting — Get your `simulate_sir` function working first.***"),
    )

    _rng = random.Random(1927)
    _figure, (_left, _right) = plt.subplots(1, 2, figsize = (11, 4))
    _maj_spread_label = "Major spread"
    _min_spread_label = "Minor spread"
    _n_sims = 20
    _n_maj_spread = 0
    for _ in range(_n_sims):
        _times, _susceptible, _infected = simulate_sir(SCHOOL_SIZE, 1, 1.0, 0.5, _rng)
        if max(_infected) < (0.1 * SCHOOL_SIZE):
            _left.step(_times, _infected, where = "post", color = "blue",
                       label = _min_spread_label, alpha = 0.6, linewidth = 2)
        else:
            _left.step(_times, _infected, where = "post", color = "firebrick",
                       label = _maj_spread_label, alpha = 0.6, linewidth = 1)
            _n_maj_spread += 1
    _left.set_xlabel("Days")
    _left.set_ylabel("Number of infected people")
    _left.set_title("20 outbreaks")
    _legend_handles, _legend_labels = _left.get_legend_handles_labels()
    _uniq_legend_entries = dict(zip(_legend_labels, _legend_handles))
    _annot_legend_entries = {}
    for _label, _handle in _uniq_legend_entries.items():
        if _label == _min_spread_label:
            _annot_legend_entries[f"{_label} ({_n_sims - _n_maj_spread})"] = _handle
        else:
            _annot_legend_entries[f"{_label} ({_n_maj_spread})"] = _handle
    _left.legend(_annot_legend_entries.values(), _annot_legend_entries.keys())

    _total_infected = []
    for _ in range(1000):
        _times, _susceptible, _infected = simulate_sir(SCHOOL_SIZE, 1, 1.0, 0.5, _rng)
        _total_infected.append(SCHOOL_SIZE - _susceptible[-1])
    _right.hist(_total_infected, bins = 50, color = "gray")
    _right.set_xlabel("Total number of people infected")
    _right.set_ylabel("Number of outbreaks")
    _right.set_title("1,000 outbreaks")
    _figure.tight_layout()
    _figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 2: Outbreaks that fizzle out

    Look at the histogram on the right above.
    The outbreaks fall into two groups: Many ***minor outbreaks***, where only a
    few people are infected before the virus disappears, and ***major
    outbreaks***, where most of the school gets infected.
    There are almost no outbreaks in between!
    This should remind you of the clades in the birth-death exercise, which
    either went extinct early, or grew big.

    Let's call an outbreak minor if fewer than 10% of the population is ever
    infected.
    The total number of people infected at any time during an outbreak is the
    number of people who are no longer susceptible at the end:

    $$
    N - S_\text{end}
    $$

    ## <font color=red> Challenge 2: How often does an outbreak fizzle out? (2 points) </font>

    Complete the `fraction_minor_outbreaks` function below, which simulates
    `number_of_simulations` outbreaks, each starting with one infected person,
    and returns the fraction of them that were minor.

    A recipe:

    1.  Start a count of minor outbreaks at 0
    2.  Use a `for` loop to repeat `number_of_simulations` times:
        1.  Simulate an outbreak with your `simulate_sir` function, starting
            with 1 infected person (and passing along `rng`)
        2.  Calculate the total number of people infected, from the last number
            of susceptible people
        3.  If that number is less than 10% of `population_size`, add 1 to your
            count
    3.  Return your count divided by `number_of_simulations`

    /// tip
    `simulate_sir` returns three lists, and the last item in a list is `[-1]`.
    So, `times, susceptible_counts, infected_counts = simulate_sir(...)` followed
    by `susceptible_counts[-1]` gets the final number of susceptible people.
    ///
    """)
    return


@app.function
def fraction_minor_outbreaks(population_size, transmission_rate, recovery_rate,
                             number_of_simulations, rng):
    """Estimate the probability that an outbreak is minor.

    Each simulated outbreak starts with one infected person. An outbreak is
    minor if fewer than 10% of the population is ever infected.

    Args:
        population_size (int): The number of people in the population (N).
        transmission_rate (float): The transmission rate (beta, per day).
        recovery_rate (float): The recovery rate (gamma, per day).
        number_of_simulations (int): The number of outbreaks to simulate.
        rng (random.Random): The random number generator to use.

    Returns:
        float: The fraction of the simulated outbreaks that were minor.

    Examples:
        >>> fraction_minor_outbreaks(100, 0.0, 0.5, 10, random.Random(1))
        1.0
    """
    fraction = 0.0
    # Add your code here!
    return fraction


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(simulate_sir_works):
    fraction_minor_outbreaks_works = True
    _messages = []
    try:
        if not simulate_sir_works:
            raise RuntimeError("Get your simulate_sir function working first.")

        # Test 1: With no transmission, every outbreak is minor
        _result = fraction_minor_outbreaks(100, 0.0, 0.5, 10, random.Random(1))
        if _result != 1.0:
            fraction_minor_outbreaks_works = False
            _messages.append(
                f"With a transmission rate of 0, the result should be 1.0, not {_result}."
            )

        # Test 2: The result should be a fraction of number_of_simulations
        _result = fraction_minor_outbreaks(100, 1.0, 0.5, 7, random.Random(2))
        if not (0 <= _result <= 1) or abs(_result * 7 - round(_result * 7)) > 1e-9:
            fraction_minor_outbreaks_works = False
            _messages.append(
                "With 7 simulations, the result should be 0/7, 1/7, ..., or 7/7, "
                + f"not {_result}. Are you using number_of_simulations?"
            )

        # Test 3: With R0 = 100, almost no outbreaks are minor
        _result = fraction_minor_outbreaks(100, 50.0, 0.5, 200, random.Random(3))
        if not (_result < 0.05):
            fraction_minor_outbreaks_works = False
            _messages.append(
                f"With R0 = 100, almost no outbreaks should be minor, but you got "
                + f"{_result}. Are you counting the people who were ever infected "
                + "(population_size minus the final number of susceptible people)?"
            )

        # Test 4: With R0 = 2, about half of outbreaks are minor
        _result = fraction_minor_outbreaks(300, 1.0, 0.5, 1000, random.Random(4))
        print(f"R0 = 2: {_result:.3f} of outbreaks were minor")
        if not (0.44 < _result < 0.56):
            fraction_minor_outbreaks_works = False
            _messages.append(
                "With R0 = 2, about half of outbreaks should be minor."
            )

        # Test 5: The same seed should give the same results
        if (fraction_minor_outbreaks(100, 1.0, 0.5, 50, random.Random(5))
                != fraction_minor_outbreaks(100, 1.0, 0.5, 50, random.Random(5))):
            fraction_minor_outbreaks_works = False
            _messages.append("Make sure you pass rng to simulate_sir.")

    except Exception as _error:
        fraction_minor_outbreaks_works = False
        if str(_error).startswith("Get your"):
            _messages.append(str(_error))
        else:
            _messages.append(
                f"Calling your function gave an error: {type(_error).__name__}: "
                + f"{_error}"
            )

    print()
    if fraction_minor_outbreaks_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your fraction_minor_outbreaks function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (fraction_minor_outbreaks_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below uses your `fraction_minor_outbreaks` function to simulate
    1,000 outbreaks in our school for each of several values of $R_0$ (with
    $\gamma = 0.5$ per day), and compares the fraction of minor outbreaks to
    $1 / R_0$.
    It takes a few seconds to run.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(fraction_minor_outbreaks_works, mo):
    mo.stop(
        not fraction_minor_outbreaks_works,
        mo.md("***Waiting — Get your `fraction_minor_outbreaks` function working "
              + "first.***"),
    )

    _rng = random.Random(1978)
    _rows = []
    for _r0 in [0.8, 1.25, 1.5, 2.0, 3.0, 4.0]:
        _fraction = fraction_minor_outbreaks(SCHOOL_SIZE, _r0 * 0.5, 0.5, 1000, _rng)
        _rows.append(f"| {_r0} | {_fraction:.3f} | {min(1.0, 1 / _r0):.3f} |")
    mo.md(
        "| $R_0$ | Fraction of minor outbreaks (simulated) | $1 / R_0$ |\n"
        + "|--:|--:|--:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 3: Fizzling out, like a clade going extinct (3 points) </font>

    Double-click this cell and answer the questions below.

    1.  **How does the fraction of minor outbreaks compare to $1 / R_0$?**

        **Answer**:

    2.  **In the birth-death exercise, a clade that starts with one lineage eventually
        goes extinct with probability $\mu / \lambda$.
        Explain why an outbreak behaves like a birth-death process near its start,
        and what birth rate ($\lambda$) and death rate ($\mu$) are for an
        outbreak.**

        **Hint 1**: What is $S / N$ near the start of an outbreak and how does that
        simplify the transmission rate per infected person?

        **Hint 2**: Put $\mu / \lambda$ in terms of $\beta$ and $\gamma$ and compare
        that to the equation for $R_0$ above.

        **Hint 3**: Dividing 1 by a fraction flips the fraction upside down.
        *E.g.*, $1 / \frac{a}{b} = \frac{b}{a}$.

        **Answer**:

    3.  **Even with $R_0 = 3$, about one in three outbreaks fizzles out on its
        own. What does that mean for a town (or a school) when a single infected
        person arrives? Why might a new virus need to be introduced several times
        before it takes off?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 3: The average outbreak

    ## From random events to smooth curves

    In a major outbreak, there are hundreds of infections and recoveries, and the
    randomness of each one averages out, so major outbreaks all have about the
    same shape (look back at the left plot in Part 1).
    So, instead of simulating every event, we can calculate the **average**
    course of an outbreak.

    In a short amount of time, $\Delta t$ (say, a tenth of a day), the expected
    number of new infections is the infection rate times $\Delta t$, and the
    expected number of recoveries is the recovery rate times $\Delta t$:

    $$
    \text{new infections} = \frac{\beta S I}{N} \Delta t
    \qquad
    \text{recoveries} = \gamma I \Delta t
    $$

    New infections move people from $S$ to $I$, and recoveries move people from
    $I$ to $R$, so after the short time, we update all three groups:

    $$
    \begin{aligned}
    S &\leftarrow S - \text{new infections} \\
    I &\leftarrow I + \text{new infections} - \text{recoveries} \\
    R &\leftarrow R + \text{recoveries}
    \end{aligned}
    $$

    Then, we repeat, one ***time step*** ($\Delta t$) at a time.
    This is called ***Euler's method***, after the mathematician Leonhard Euler.
    Kermack and McKendrick (1927) wrote the SIR model as ***differential
    equations***, which describe how fast $S$, $I$, and $R$ change:

    $$
    \begin{aligned}
    \frac{dS}{dt} &= -\text{total infection rate} \\
    \frac{dI}{dt} &= +\text{total infection rate} - \text{total recovery rate} \\
    \frac{dR}{dt} &= +\text{total recovery rate}
    \end{aligned}
    $$

    Plugging in the total rates of infections and recoveries, we get:

    $$
    \begin{aligned}
    \frac{dS}{dt} &= -\frac{\beta S I}{N} \\
    \frac{dI}{dt} &= \frac{\beta S I}{N} - \gamma I \\
    \frac{dR}{dt} &= \gamma I
    \end{aligned}
    $$

    Euler's method is the simplest way to solve differential equations like these
    with a computer.
    The smaller the time step, the closer it gets to the exact solution (but the
    more steps it takes).

    /// note
    In this model, $S$, $I$, and $R$ are **averages**, so they don't have to be
    whole numbers.
    For example, after one time step, there might be 1.2 infected people.
    ///

    ## <font color=red> Challenge 4: Euler's method (4 points) </font>

    Complete the `simulate_sir_euler` function below.
    The function already sets up the starting numbers, the records, and the
    number of time steps.
    Under the "`Add your code here!`" comment, write a `for` loop that repeats
    `number_of_steps` times.
    In each step:

    1.  Calculate the number of new infections, $\beta S I \Delta t / N$, and the
        number of recoveries, $\gamma I \Delta t$, during the time step
        (`time_step` is $\Delta t$)
    2.  Update `susceptible`, `infected`, and `recovered`
    3.  Record the step, by appending the time at the end of the step to `times`
        (for step number `step`, counting from 0, that's
        `(step + 1) * time_step`), and appending `susceptible`, `infected`, and
        `recovered` to their lists

    /// attention
    Calculate **both** the new infections and the recoveries **before** you
    update any of the three groups.
    Otherwise, the recoveries will be calculated from the wrong number of
    infected people!
    ///
    """)
    return


@app.function
def simulate_sir_euler(population_size, initial_infected, transmission_rate,
                       recovery_rate, max_time, time_step, initial_recovered = 0):
    """Calculate the average course of an outbreak with Euler's method.

    Args:
        population_size (int): The number of people in the population (N).
        initial_infected (float): The number of people infected at time 0.
        transmission_rate (float): The transmission rate (beta, per day).
        recovery_rate (float): The recovery rate (gamma, per day).
        max_time (float): How many days to calculate.
        time_step (float): The length of each time step, in days.
        initial_recovered (float): The number of people who are immune at
            time 0 (default 0).

    Returns:
        tuple[list[float], list[float], list[float], list[float]]: The times,
            and the numbers of susceptible, infected, and recovered people at
            each time. The lists start with time 0 (and the starting numbers).

    Examples:
        >>> simulate_sir_euler(100, 10, 1.0, 0.5, 0.0, 0.1)
        ([0.0], [90], [10], [0])
    """
    susceptible = population_size - initial_infected - initial_recovered
    infected = initial_infected
    recovered = initial_recovered
    times = [0.0]
    susceptible_counts = [susceptible]
    infected_counts = [infected]
    recovered_counts = [recovered]
    number_of_steps = round(max_time / time_step)
    # Add your code here!
    return times, susceptible_counts, infected_counts, recovered_counts


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    simulate_sir_euler_works = True
    _messages = []

    def _close(found, expected):
        if len(found) != len(expected):
            return False
        return all(abs(_a - _b) < 1e-6 for _a, _b in zip(found, expected))

    try:
        # Test 1: Two steps that we can check by hand. Step 1: new infections
        # = 1 * 90 * 10 * 0.1 / 100 = 0.9 and recoveries = 0.5 * 10 * 0.1 = 0.5.
        # Step 2: new infections = 89.1 * 10.4 * 0.1 / 100 = 0.92664 and
        # recoveries = 0.5 * 10.4 * 0.1 = 0.52.
        _result = simulate_sir_euler(100, 10, 1.0, 0.5, 0.2, 0.1)
        _expected = (
            [0.0, 0.1, 0.2],
            [90, 89.1, 88.17336],
            [10, 10.4, 10.80664],
            [0, 0.5, 1.02],
        )
        _names = ["times", "susceptible", "infected", "recovered"]
        for _name, _found, _want in zip(_names, _result, _expected):
            if not _close(_found, _want):
                simulate_sir_euler_works = False
                _messages.append(
                    f"With N = 100, 10 infected, beta = 1, gamma = 0.5, max_time "
                    + f"= 0.2, and time_step = 0.1, the {_name} list should be "
                    + f"{_want}, not {_found}."
                )
                break

        # Test 2: Nobody is created or lost
        _times, _s, _i, _r = simulate_sir_euler(500, 1, 2.0, 0.5, 30.0, 0.05)
        if len(_times) != 601 or abs(_times[-1] - 30.0) > 1e-6:
            simulate_sir_euler_works = False
            _messages.append(
                "With max_time = 30 and time_step = 0.05, there should be 601 "
                + "times, ending at 30."
            )
        for _a, _b, _c in zip(_s, _i, _r):
            if abs(_a + _b + _c - 500) > 1e-6:
                simulate_sir_euler_works = False
                _messages.append(
                    "S + I + R should always equal the population size."
                )
                break

        # Test 3: Immune people at the start
        _times, _s, _i, _r = simulate_sir_euler(100, 1, 1.0, 0.5, 1.0, 0.1,
                                                initial_recovered = 50)
        if _s[0] != 49 or _r[0] != 50 or not (_r[-1] > 50):
            simulate_sir_euler_works = False
            _messages.append(
                "With initial_recovered = 50, recovered should start at 50 "
                + "(and susceptible at 49), and grow from there."
            )

        # Test 4: With R0 = 2, about 79.7% of people are eventually infected
        if simulate_sir_euler_works:
            _times, _s, _i, _r = simulate_sir_euler(1000, 1, 1.0, 0.5, 200.0, 0.01)
            _final = (1000 - _s[-1]) / 1000
            print(f"R0 = 2: {_final:.3f} of the population was eventually "
                  + "infected (expected 0.797)")
            if not (0.787 < _final < 0.807):
                simulate_sir_euler_works = False
                _messages.append(
                    "The fraction eventually infected is off. Are your new "
                    + "infections beta * S * I * time_step / N?"
                )

    except Exception as _error:
        simulate_sir_euler_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )

    print()
    if simulate_sir_euler_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your simulate_sir_euler function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (simulate_sir_euler_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 5: Plotting an outbreak (2 points) </font>

    Complete the `plot_sir` function below, which plots the numbers of
    susceptible, infected, and recovered people over time, as three lines on the
    same axes.

    A recipe:

    1.  Make a figure with one set of axes:
        `figure, axes = plt.subplots(figsize = (8, 4.5))`
    2.  Draw three lines, one for each group, with `axes.plot(x, y, label =
        "...")`, where `x` is `times`, `y` is `susceptible`, `infected`, or
        `recovered`, and `label` is the name of the group (*e.g.*,
        `"Susceptible"`)
    3.  Label the x-axis and the y-axis, and give the plot a title, like you did in
        the birth-death exercise
    4.  Add a legend with `axes.legend()`
    5.  The function already returns `figure`

    /// tip | Optional
    You can choose the color of each line with the `color` argument
    (*e.g.*, `color = "firebrick"`).
    ///
    """)
    return


@app.function
def plot_sir(times, susceptible, infected, recovered):
    """Plot the numbers of susceptible, infected, and recovered people over time.

    Args:
        times (list[float]): The times.
        susceptible (list[float]): The number of susceptible people at each time.
        infected (list[float]): The number of infected people at each time.
        recovered (list[float]): The number of recovered people at each time.

    Returns:
        matplotlib.figure.Figure: The figure with the three lines (or None, until
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
    plot_sir_works = True
    _messages = []
    try:
        _figure = plot_sir([0, 1, 2, 3], [9, 7, 4, 3], [1, 2, 3, 1], [0, 1, 3, 6])
        if not isinstance(_figure, plt.Figure):
            plot_sir_works = False
            _messages.append(
                f"Your function should return a figure, not {type(_figure).__name__}."
            )
        elif len(_figure.axes) != 1:
            plot_sir_works = False
            _messages.append("Your figure should have one set of axes.")
        else:
            _axes = _figure.axes[0]
            if len(_axes.lines) != 3:
                plot_sir_works = False
                _messages.append(
                    f"Your axes should have 3 lines, not {len(_axes.lines)}."
                )
            else:
                _ys = sorted(list(_line.get_ydata()) for _line in _axes.lines)
                if _ys != sorted([[9, 7, 4, 3], [1, 2, 3, 1], [0, 1, 3, 6]]):
                    plot_sir_works = False
                    _messages.append(
                        "Your lines should show susceptible, infected, and "
                        + "recovered (in that order of arguments) versus times."
                    )
                for _line in _axes.lines:
                    if _line.get_label().startswith("_"):
                        plot_sir_works = False
                        _messages.append("Give each line a label.")
                        break
            if _axes.get_legend() is None:
                plot_sir_works = False
                _messages.append("Your plot needs a legend.")
            if _axes.get_xlabel() == "":
                plot_sir_works = False
                _messages.append("Your x-axis needs a label.")
            if _axes.get_ylabel() == "":
                plot_sir_works = False
                _messages.append("Your y-axis needs a label.")
            if _axes.get_title() == "":
                plot_sir_works = False
                _messages.append("Your plot needs a title.")
        if isinstance(_figure, plt.Figure):
            plt.close(_figure)
    except Exception as _error:
        plot_sir_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )

    if plot_sir_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your plot_sir function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (plot_sir_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exploring the SIR model

    The second cell below uses your `simulate_sir_euler` and `plot_sir` functions
    to calculate and plot the average course of an outbreak in our school,
    starting with one infected person, over 100 days.
    Use the sliders to change the transmission rate ($\beta$) and the recovery
    rate ($\gamma$), and the drop-down menu to change the time step
    ($\Delta t$).
    The table below the plot shows $R_0$, the peak of the outbreak, and how many
    people were infected in total.
    **You do not need to edit the next two cells.**
    """)
    return


@app.cell
def _(mo):
    # Create the sliders and the drop-down menu
    transmission_rate_slider = mo.ui.slider(
        start = 0.1, stop = 3.0, step = 0.05, value = 1.0, show_value = True,
        label = r"Transmission rate, $\beta$ (per day)",
    )
    recovery_rate_slider = mo.ui.slider(
        start = 0.1, stop = 1.0, step = 0.05, value = 0.5, show_value = True,
        label = r"Recovery rate, $\gamma$ (per day)",
    )
    time_step_dropdown = mo.ui.dropdown(
        options = {"0.01 days": 0.01, "0.1 days": 0.1, "0.5 days": 0.5,
                   "1 day": 1.0, "2 days": 2.0},
        value = "0.1 days",
        label = r"Time step, $\Delta t$",
    )
    return recovery_rate_slider, time_step_dropdown, transmission_rate_slider


@app.cell
def _(
    mo,
    plot_sir_works,
    recovery_rate_slider,
    simulate_sir_euler_works,
    time_step_dropdown,
    transmission_rate_slider,
):
    mo.stop(
        not (simulate_sir_euler_works and plot_sir_works),
        mo.md("***Waiting — Get your `simulate_sir_euler` and `plot_sir` "
              + "functions working first.***"),
    )

    _beta = transmission_rate_slider.value
    _gamma = recovery_rate_slider.value
    _times, _s, _i, _r = simulate_sir_euler(SCHOOL_SIZE, 1, _beta, _gamma, 100.0,
                                            time_step_dropdown.value)
    _figure = plot_sir(_times, _s, _i, _r)
    _figure.axes[0].set_ylim(-20, SCHOOL_SIZE + 20)

    # Find the peak of the outbreak (the time with the most infected people)
    _peak = _i.index(max(_i))
    _table = mo.md(
        "| $R_0 = \\beta / \\gamma$ | Most people infected at once | Day of the "
        + "peak | $S / N$ at the peak | $1 / R_0$ | Fraction ever infected |\n"
        + "|--:|--:|--:|--:|--:|--:|\n"
        + f"| {_beta / _gamma:.2f} | {_i[_peak]:.1f} | {_times[_peak]:.1f} "
        + f"| {_s[_peak] / SCHOOL_SIZE:.3f} | {_gamma / _beta:.3f} "
        + f"| {(SCHOOL_SIZE - _s[-1]) / SCHOOL_SIZE:.3f} |"
    )
    mo.vstack([
        transmission_rate_slider,
        recovery_rate_slider,
        time_step_dropdown,
        _figure,
        _table,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 6: Growing, peaking, and ending (3 points) </font>

    Use the sliders above to answer the questions below.
    Double-click this cell to add your answers.

    1.  **Keep $\gamma$ at 0.5, and slowly lower $\beta$ from 1.0. At about what
        value of $R_0$ does the number of infected people stop growing at all?
        Why does that value make sense? (Hint: Think about what $R_0$ means.)**

        **Answer**:

    2.  **Try a few combinations of $\beta$ and $\gamma$ with $R_0 > 1$. How does
        $S / N$ at the peak compare to $1 / R_0$? Why does the number of infected
        people start to fall at that point? (Hint: Each infected person infects
        others at rate $\beta S / N$, and recovers at rate $\gamma$.)**

        **Answer**:

    3.  **Set $\beta$ back to 1.0 and $\gamma$ to 0.5, and change the time step
        from 0.01 days to 2 days. What happens to the peak and to the curves? Why
        do we need a small time step for Euler's method?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 4: The boarding school

    Now, let's fit the SIR model to the outbreak at the boarding school, to
    estimate how contagious the virus was ($\beta$) and how long boys stayed
    infectious ($1 / \gamma$).
    We will make a few simplifying assumptions:

    -   The number of boys **in bed** each day is the number of **infected**
        boys, $I$
    -   The outbreak started on **January 21** (day 0, the day before the first
        count) with **one** infected boy
    -   All 763 boys mixed with each other equally

    The `predict_in_bed` function below uses your `simulate_sir_euler` function
    (with a time step of 0.1 days) to predict the number of infected boys on each
    day, for a transmission rate and a recovery rate.
    **You do not need to edit this function.**
    """)
    return


@app.function
def predict_in_bed(population_size, transmission_rate, recovery_rate, days):
    """Predict the number of infected people on each day with the SIR model.

    The outbreak starts at day 0 with one infected person, and is calculated
    with Euler's method, with a time step of 0.1 days.

    Args:
        population_size (int): The number of people in the population (N).
        transmission_rate (float): The transmission rate (beta, per day).
        recovery_rate (float): The recovery rate (gamma, per day).
        days (list[int]): The days on which to predict the number of infected
            people.

    Returns:
        list[float]: The predicted number of infected people on each day in
            `days`.
    """
    time_step = 0.1
    times, susceptible, infected, recovered = simulate_sir_euler(
        population_size, 1, transmission_rate, recovery_rate, max(days),
        time_step)
    # With 10 steps per day, day d is at index 10 * d of the lists
    predictions = []
    for day in days:
        predictions.append(infected[round(day / time_step)])
    return predictions


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fitting a model to data

    How do we find the values of $\beta$ and $\gamma$ that best fit the data?
    For each pair of values, we can measure how far the model's predictions are
    from the counts, with the ***sum of squares***:

    $$
    \text{sum of squares} = \sum_{d} \left(\text{observed}_d -
    \text{predicted}_d\right)^2
    $$

    where the sum is over the days, $d$.
    Squaring each difference makes it positive (so too-high and too-low
    predictions both count against the model), and penalizes big misses more
    than small ones.
    The best-fitting values are the ones with the **smallest** sum of squares.
    This is called ***least squares***, and it's the same idea that `linregress`
    used to fit the molecular clock in Capstone 2.

    The simplest way to find the best values is a ***grid search***: Try every
    combination of $\beta$ and $\gamma$ from a list of values for each, and keep
    the combination with the smallest sum of squares.

    ## <font color=red> Challenge 7: Fitting the SIR model (4 points) </font>

    Complete the two functions below.

    **`sum_of_squares(observed, predicted)`** returns the sum of the squared
    differences between two lists of numbers.
    A recipe:

    1.  Start a total at 0
    2.  Loop over the pairs of numbers, with
        `for observed_value, predicted_value in zip(observed, predicted):`
        (remember, `zip` pairs up the first items of the lists, then the second
        items, and so on)
    3.  Add the squared difference of each pair to the total (`x ** 2` is $x$
        squared), and return the total

    **`fit_sir(days, observed, population_size, transmission_rates,
    recovery_rates)`** does a grid search.
    It returns the best transmission rate, the best recovery rate, and their sum
    of squares.
    A recipe:

    1.  Start with `best_score = math.inf` (`math.inf` is infinity, so the
        first sum-of-squares score we calculate will always be better)
    2.  Use a `for` loop over `transmission_rates`, with **another** `for` loop
        inside it over `recovery_rates`, so that you try every combination
    3.  For each combination:
        1.  Get the predictions with
            `predict_in_bed(population_size, transmission_rate, recovery_rate, days)`
        2.  Calculate the sum of squares with your `sum_of_squares` function
        3.  If it's smaller than `best_score`, update `best_score`,
            `best_transmission_rate`, and `best_recovery_rate`
    4.  The function already returns the three best values
    """)
    return


@app.function
def sum_of_squares(observed, predicted):
    """Calculate the sum of the squared differences between two lists.

    Args:
        observed (list[float]): The observed values.
        predicted (list[float]): The predicted values, in the same order.

    Returns:
        float: The sum of (observed - predicted) squared, over all the pairs.

    Examples:
        >>> sum_of_squares([1, 2, 3], [1, 4, 6])
        13
    """
    total = 0
    # Add your code here!
    return total


@app.function
def fit_sir(days, observed, population_size, transmission_rates, recovery_rates):
    """Find the transmission and recovery rates that best fit the data.

    Tries every combination of the transmission rates and recovery rates, and
    keeps the one whose predictions (from `predict_in_bed`) have the smallest
    sum of squares.

    Args:
        days (list[int]): The days on which the counts were made.
        observed (list[float]): The number of infected people on each day.
        population_size (int): The number of people in the population (N).
        transmission_rates (list[float]): The transmission rates to try.
        recovery_rates (list[float]): The recovery rates to try.

    Returns:
        tuple[float, float, float]: The best transmission rate, the best
            recovery rate, and their sum of squares.
    """
    best_transmission_rate = None
    best_recovery_rate = None
    best_score = math.inf
    # Add your code here!
    return best_transmission_rate, best_recovery_rate, best_score


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next two cells test your `sum_of_squares` and `fit_sir` functions,
    respectively.
    **Note**: You do not need to edit the next two cells.
    """)
    return


@app.cell
def _():
    _cases = [
        (([1, 2, 3], [1, 2, 3]), 0),
        (([1, 2, 3], [1, 4, 6]), 13),
        (([10, 20], [12.5, 15.0]), 31.25),
        (([], []), 0),
    ]
    _failures = []
    for (_observed, _predicted), _expected in _cases:
        try:
            _found = sum_of_squares(_observed, _predicted)
            _ok = abs(_found - _expected) < 1e-9
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
            _ok = False
        if not _ok:
            _failures.append(
                f"  sum_of_squares({_observed}, {_predicted}): expected "
                + f"{_expected}, got {_found}"
            )
    sum_of_squares_works = len(_failures) == 0
    if sum_of_squares_works:
        print("Yay, your sum_of_squares function passed the test!")
    else:
        print("Sorry, sum_of_squares failed these cases:\n" + "\n".join(_failures))
    return (sum_of_squares_works,)


@app.cell
def _(simulate_sir_euler_works, sum_of_squares_works):
    fit_sir_works = True
    _messages = []
    try:
        if not (simulate_sir_euler_works and sum_of_squares_works):
            raise RuntimeError(
                "Get your simulate_sir_euler and sum_of_squares functions "
                + "working first."
            )

        # Test 1: Data made by the model itself, with beta = 1.2 and gamma = 0.4,
        # should be fit perfectly
        _days = list(range(1, 11))
        _data = predict_in_bed(500, 1.2, 0.4, _days)
        _result = fit_sir(_days, _data, 500, [1.0, 1.1, 1.2, 1.3], [0.3, 0.4, 0.5])
        if (_result[0] != 1.2 or _result[1] != 0.4
                or not abs(_result[2]) < 1e-9):
            fit_sir_works = False
            _messages.append(
                "With data made with beta = 1.2 and gamma = 0.4, the result should "
                + f"be (1.2, 0.4, 0.0), not {_result}."
            )

        # Test 2: The best combination in a small grid for the school data
        _betas = [1.5, 1.6, 1.7, 1.8]
        _gammas = [0.35, 0.45, 0.55]
        _best = None
        for _b in _betas:
            for _g in _gammas:
                _score = sum_of_squares(
                    IN_BED, predict_in_bed(SCHOOL_SIZE, _b, _g, OUTBREAK_DAYS))
                if _best is None or _score < _best[2]:
                    _best = (_b, _g, _score)
        _result = fit_sir(OUTBREAK_DAYS, IN_BED, SCHOOL_SIZE, _betas, _gammas)
        if (_result[0] != _best[0] or _result[1] != _best[1]
                or not abs(_result[2] - _best[2]) < 1e-6):
            fit_sir_works = False
            _messages.append(
                f"For the school data and a small grid, the result should be "
                + f"({_best[0]}, {_best[1]}, {_best[2]:.4f}), not {_result}. Are "
                + "you trying every combination, and keeping the smallest score?"
            )
    except Exception as _error:
        fit_sir_works = False
        if str(_error).startswith("Get your"):
            _messages.append(str(_error))
        else:
            _messages.append(
                f"Calling your function gave an error: {type(_error).__name__}: "
                + f"{_error}"
            )

    if fit_sir_works:
        print("Yay, your fit_sir function passed the test!")
    else:
        print("Sorry, your fit_sir function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (fit_sir_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below uses your `fit_sir` function to try every combination of 76
    transmission rates (from 1.0 to 2.5 per day) and 61 recovery rates (from 0.2
    to 0.8 per day), which is 4,636 combinations, so it might take a few seconds.
    Then, it plots the counts from the school (bars) along with the
    best-fitting model (line), and calculates how many boys the model predicts
    were infected by the end of the outbreak.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(fit_sir_works, mo):
    mo.stop(
        not fit_sir_works,
        mo.md("***Waiting — Get your `fit_sir` function working first.***"),
    )

    _betas = []
    for _k in range(76):
        _betas.append(round(1.0 + 0.02 * _k, 2))
    _gammas = []
    for _k in range(61):
        _gammas.append(round(0.2 + 0.01 * _k, 2))
    fitted_transmission_rate, fitted_recovery_rate, _score = fit_sir(
        OUTBREAK_DAYS, IN_BED, SCHOOL_SIZE, _betas, _gammas)
    fitted_r0 = fitted_transmission_rate / fitted_recovery_rate

    # The best-fitting model, over the 14 days of the outbreak
    _times, _s, _i, _r = simulate_sir_euler(
        SCHOOL_SIZE, 1, fitted_transmission_rate, fitted_recovery_rate, 14.0, 0.1)
    # And over a longer time, to see how many boys are eventually infected
    _long = simulate_sir_euler(
        SCHOOL_SIZE, 1, fitted_transmission_rate, fitted_recovery_rate, 60.0, 0.1)
    _ever_infected = SCHOOL_SIZE - _long[1][-1]

    _figure, _axes = plt.subplots(figsize = (8, 4.5))
    _axes.bar(OUTBREAK_DAYS, IN_BED, color = "steelblue", label = "Boys in bed")
    _axes.plot(_times, _i, color = "firebrick", linewidth = 2.5,
               label = "SIR model (infected)")
    _axes.set_xticks(OUTBREAK_DAYS, OUTBREAK_DATES, rotation = 45)
    _axes.set_xlabel("Date (1978)")
    _axes.set_ylabel("Number of boys")
    _axes.set_title("The best-fitting SIR model")
    _axes.legend()
    _figure.tight_layout()

    mo.vstack([
        _figure,
        mo.md(
            "| $\\beta$ (per day) | $\\gamma$ (per day) | $R_0$ "
            + "| Infectious period, $1 / \\gamma$ (days) | Sum of squares "
            + "| Boys ever infected (model) | Boys ever in bed (data) |\n"
            + "|--:|--:|--:|--:|--:|--:|--:|\n"
            + f"| {fitted_transmission_rate:.2f} | {fitted_recovery_rate:.2f} "
            + f"| {fitted_r0:.2f} | {1 / fitted_recovery_rate:.2f} "
            + f"| {_score:.0f} | {_ever_infected:.0f} | 512 |"
        ),
    ])
    return (fitted_r0,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 8: How contagious was the virus? (3 points) </font>

    Double-click this cell and answer the questions below.

    1.  **What are the best-fitting values of $R_0$ and the infectious period
        ($1 / \gamma$)? Based on your table in Part 2, if one infected boy
        brought this virus into the school, about how likely was it that a major
        outbreak would follow?**

        **Answer**:

    2.  **The model predicts that almost every boy was eventually infected, but
        only 512 of the 763 boys were ever confined to bed. Give two reasons the
        model and the data could disagree.**

        **Answer**:

    3.  **We assumed that the number of boys in bed is the number of infected (and
        infectious) boys. Why might that not be quite right? (Hint: Think about when
        a sick boy is infectious, and whether boys in bed can infect others.)**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Extra credit challenge (3 points) </font>

    If some boys had been vaccinated before the outbreak, they would have been
    immune from the start.
    How many boys would the school have needed to vaccinate to prevent a major
    outbreak?

    Your `simulate_sir_euler` function has an argument we haven't used yet,
    `initial_recovered`, which is the number of people who are immune at the start.
    In the cell below, beneath the "`Write your extra credit code here`" comment,
    write code to:

    1.  Loop over the fractions of boys vaccinated in the list
        `vaccinated_fractions` (defined for you: 0, 0.05, 0.10, ..., 0.95)
    2.  For each fraction, calculate the number of boys vaccinated (the fraction
        times `SCHOOL_SIZE`), and use `simulate_sir_euler` to calculate an
        outbreak in the school that starts with 1 infected boy, using the
        best-fitting rates (`fitted_transmission_rate` and
        `fitted_recovery_rate`), with `initial_recovered` set to the number
        vaccinated, for 200 days, with a time step of 0.1
    3.  Calculate the number of boys who were **infected** during the outbreak
        (careful: Vaccinated boys are not susceptible at the start, but they
        were never infected either!), and print it along with the fraction
        vaccinated

    After your code prints the results, answer the questions below.
    One of the three extra credit points is for your code, and one is for each of
    your answers.

    1.  **What is the smallest fraction vaccinated (in the list) at which fewer
        than 20 boys are infected? How does it compare to $1 - 1 / R_0$ (calculated
        for you in the cell below, using the best-fitting $R_0$)?**

        **Answer**:

    2.  **Why don't we need to vaccinate every boy to prevent a major outbreak?
        (Hint: In Challenge 6, you found that the number of infected people
        falls when $S / N$ is less than $1 / R_0$.)**

        **Answer**:
    """)
    return


@app.cell
def _(fitted_r0):
    vaccinated_fractions = []
    # Create a list of [0.00, 0.05, 0.10, 0.15, ... 0.95]
    for _k in range(20):
        vaccinated_fractions.append(round(0.05 * _k, 2))
    print(f"1 - 1 / R0 = {1 - 1 / fitted_r0:.3f}")
    print()

    # Write your extra credit code here
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    Starting from the daily counts of boys in bed at a boarding school in 1978,
    you:

    -   Simulated outbreaks under the **SIR model** with the **Gillespie
        algorithm**, and found that outbreaks are either **minor** or **major**
    -   Found that an outbreak that starts with one infected person fizzles out
        with a probability of about $1 / R_0$ (when $R_0 > 1$), because near its
        start, an outbreak is a
        **birth-death process** with $\lambda = \beta$ and $\mu = \gamma$
    -   Used **Euler's method** to calculate the average course of an outbreak, and
        found that an outbreak only grows when $R_0 > 1$, and peaks when
        $S / N = 1 / R_0$
    -   **Fit** the model to the boarding-school data by **least squares**, and
        estimated that each infected boy infected almost four others, which made
        a major outbreak very likely once the virus arrived

    Models like these were used throughout the COVID-19 pandemic to estimate
    $R_0$, predict when outbreaks would peak, and decide how many people needed to
    be vaccinated.
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

    The counts of boys in bed are from a report, "Influenza in a boarding school,"
    *British Medical Journal* 1:587 (4 March 1978).
    The report showed the counts only in a figure, so the exact numbers differ a
    little between sources; we use the version in the
    [`outbreaks`](https://github.com/reconverse/outbreaks) R package, which is
    from De Vries et al. (2006), *A Course in Mathematical Biology* (SIAM).
    The SIR model is from Kermack and McKendrick (1927), *Proceedings of the
    Royal Society A* 115:700–721, and the Gillespie algorithm is from Gillespie
    (1977), *Journal of Physical Chemistry* 81:2340–2361.
    I used Anthropic's Claude (Opus 5.5 model) to help draft this capstone project.
    """)
    return


if __name__ == "__main__":
    app.run()
