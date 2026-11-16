# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.0",
#     "matplotlib",
#     "numpy",
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
    from matplotlib.patches import Circle, FancyArrowPatch
    from matplotlib.ticker import StrMethodFormatter

    # The four DNA bases
    BASES = "ACGT"

    # Where to find the human DNA sequence and its features we use in Part 3
    CPG_FASTA_URL = (
        "https://raw.githubusercontent.com/phyletica/intro-to-comp-bio/"
        + "refs/heads/main/notebooks/data/chr19-cpg-region.fasta"
    )
    CPG_FEATURES_URL = (
        "https://raw.githubusercontent.com/phyletica/intro-to-comp-bio/"
        + "refs/heads/main/notebooks/data/chr19-cpg-region-features.tsv"
    )
    # We train our CpG island HMMs on the bases before this position, and test
    # them on the bases after it
    TRAINING_END = 1_000_000
    # The stretch of the sequence we plot in Part 3
    WINDOW = (1_000_000, 1_050_000)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Hidden Markov models: Inferring what we can't see

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Hidden states

    In many problems in biology, what we want to know is ***hidden***, and all we
    get to see are clues that it leaves behind.
    A genome is a long string of A, C, G, and T, but nothing in the string says
    "a gene starts here," or "this stretch is regulatory DNA."
    A ***hidden Markov model*** (***HMM***) is a model for exactly this kind of
    problem: A hidden ***state*** changes along a sequence, following a Markov
    chain (like the substitution models we've used), and at each position, the
    hidden state ***emits*** a symbol that we can see.
    The trick is to work backward, from what we see to the hidden states that most
    likely produced it.

    HMMs are used to find genes, protein domains, and regulatory regions in
    genomes, to infer the ancestry of different parts of a person's genome, to
    reconstruct the history of population sizes from one genome, and far beyond
    biology, to recognize speech and to decode the signals sent to your phone.
    **All of these use the same model, and the same algorithm, which you will write
    in this exercise.**

    Here's our plan:

    1.  **Simulate** an HMM: a casino that secretly switches between a fair die
        and a loaded die
    2.  Calculate the probability of the rolls **and** a path of hidden states
    3.  Write the ***Viterbi algorithm***, which finds the most probable path of
        hidden states, and use it to catch the casino cheating
    4.  **Train** an HMM by counting, and use it, along with your Viterbi
        function, to find ***CpG islands*** along a human chromosome
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 1: The occasionally dishonest casino

    A casino offers a game of dice.
    Most of the time, it uses a fair die, but every now and then, it secretly
    switches to a loaded die that rolls a 6 half of the time.
    After a while, it switches back to the fair die, so that nobody gets
    suspicious.
    All we see are the rolls.
    This classic example is from the book *Biological Sequence Analysis* (Durbin
    *et al.*, 1998).

    An HMM has three parts:

    1.  ***Hidden states***: Here, which die the casino is using (**Fair** or
        **Loaded**)
    2.  ***Transition probabilities***: The probability of each hidden state at
        the next position, given the hidden state at this position.
        Here, if the casino is using the fair die, it switches to the loaded die
        before the next roll with probability 0.05 (and keeps the fair die with
        probability 0.95).
        If it is using the loaded die, it switches back with probability 0.1.
    3.  ***Emission probabilities***: The probability of each symbol we can see,
        given the hidden state.
        The fair die rolls each number with probability 1/6.
        The loaded die rolls a 6 with probability 0.5, and each other number with
        probability 0.1.

    We also need the ***start probabilities*** of the hidden states for the
    first roll; we'll say the casino is equally likely to start with either die.

    The hidden states follow a Markov chain, just like the bases at a site in
    our substitution models: The next state depends only on the current one.
    But now we can't see the chain; we only see what each state emits.
    That's what makes it a ***hidden*** Markov model.

    In the next cell (**which you do not need to edit**),
    we create a dictionary to represent the casino HMM described above.
    Every hidden Markov model in this notebook will be a dictionary like this.
    """)
    return


@app.cell
def _():
    # The casino's HMM. Every model in this notebook is a dictionary like this:
    #   "states": The names of the hidden states
    #   "symbols": The symbols we can see
    #   "start": The start probability of each state
    #   "transitions": Row j, column k is the probability of going from state j to
    #       state k
    #   "emissions": Row k, column s is the probability that state k emits symbol s
    casino_model = {
        "states": ["Fair", "Loaded"],
        "symbols": ["1", "2", "3", "4", "5", "6"],
        "start": np.array([0.5, 0.5]),
        "transitions": np.array([
            [0.95, 0.05],
            [0.10, 0.90],
        ]),
        "emissions": np.array([
            [1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6],
            [0.1, 0.1, 0.1, 0.1, 0.1, 0.5],
        ]),
    }
    return (casino_model,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In the `casino_model` dictionary above, we represent the transition
    probabilities using a NumPy array with one row and one column per hidden state.
    Row `j`, column `k` is the probability of going from state `j` to state `k`, so
    each row adds up to 1.
    For example, `casino_model["transitions"][0, 1]` is 0.05, the probability of
    switching from the fair die (state 0) to the loaded die (state 1).
    Similarly, `casino_model["emissions"][1, 5]` is 0.5, the probability that
    the loaded die (state 1) rolls a 6 (symbol 5, because Python counts from 0).
    Use the cell below to explore the `casino_model` dictionary and get comfortable
    accessing different parts of the model.
    """)
    return


@app.cell
def _(casino_model):
    print('casino_model["transitions"]:')
    print(casino_model["transitions"])

    print()
    print('casino_model["transitions"][0, 0]:')
    print(casino_model["transitions"][0, 0])

    print()
    print('casino_model["transitions"][1, 0]:')
    print(casino_model["transitions"][1, 0])

    print()
    print('casino_model["emissions"]:')
    print(casino_model["emissions"])

    print()
    print('casino_model["emissions"][0, 0]:')
    print(casino_model["emissions"][0, 0])

    print()
    print('casino_model["emissions"][1, 5]:')
    print(casino_model["emissions"][1, 5])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The figure below shows the casino's model.
    The arrows show the transition probabilities, and the bar plots show the
    emission probabilities of each die.
    **You do not need to edit the next two cells.**
    """)
    return


@app.function(hide_code=True)
def draw_two_state_diagram(model, colors = ("steelblue", "firebrick"),
                           symbol_label = "Symbol"):
    """Draw a two-state HMM: states, transition arrows, and emission bars.

    Returns:
        matplotlib.figure.Figure: The figure.
    """
    names = model["states"]
    transitions = model["transitions"]
    figure = plt.figure(figsize = (9, 5.6))
    axes = figure.add_axes([0.0, 0.42, 1.0, 0.58])
    axes.set_xlim(0, 10)
    axes.set_ylim(0.2, 4.0)
    axes.set_aspect("equal")
    axes.axis("off")
    centers = [(3.0, 1.6), (7.0, 1.6)]
    radius = 0.8
    for k, (x, y) in enumerate(centers):
        axes.add_patch(Circle((x, y), radius, facecolor = colors[k], alpha = 0.15,
                              edgecolor = "none"))
        axes.add_patch(Circle((x, y), radius, facecolor = "none",
                              edgecolor = colors[k], linewidth = 2.5))
        axes.text(x, y, names[k], ha = "center", va = "center", fontsize = 15,
                  fontweight = "bold", color = colors[k])
        # Arrow back to the same state (a loop above the circle)
        axes.add_patch(FancyArrowPatch(
            (x - 0.45, y + 0.66), (x + 0.45, y + 0.66),
            connectionstyle = "arc3,rad=-1.9", arrowstyle = "-|>",
            mutation_scale = 18, linewidth = 2, color = "dimgray"))
        axes.text(x, y + 2.05, f"{transitions[k, k]:.4g}", ha = "center",
                  va = "bottom", fontsize = 13)
    # Arrows between the two states
    (x0, y0), (x1, y1) = centers
    axes.add_patch(FancyArrowPatch(
        (x0 + 0.7, y0 + 0.38), (x1 - 0.7, y1 + 0.38),
        connectionstyle = "arc3,rad=-0.25", arrowstyle = "-|>",
        mutation_scale = 18, linewidth = 2, color = "dimgray"))
    axes.text(5.0, y0 + 1.0, f"{transitions[0, 1]:.4g}", ha = "center",
              va = "bottom", fontsize = 13)
    axes.add_patch(FancyArrowPatch(
        (x1 - 0.7, y1 - 0.38), (x0 + 0.7, y0 - 0.38),
        connectionstyle = "arc3,rad=-0.25", arrowstyle = "-|>",
        mutation_scale = 18, linewidth = 2, color = "dimgray"))
    axes.text(5.0, y0 - 1.0, f"{transitions[1, 0]:.4g}", ha = "center",
              va = "top", fontsize = 13)
    # The emission probabilities of each state
    for k in range(2):
        bars = figure.add_axes([0.12 + 0.46 * k, 0.11, 0.34, 0.25])
        bars.bar(range(len(model["symbols"])), model["emissions"][k],
                 color = colors[k], alpha = 0.8)
        bars.set_xticks(range(len(model["symbols"])), model["symbols"])
        bars.set_ylim(0, max(0.55, 1.15 * model["emissions"].max()))
        bars.set_title(f"Emission probabilities: {names[k]}", fontsize = 11)
        bars.set_xlabel(symbol_label, fontsize = 10)
        bars.spines[["top", "right"]].set_visible(False)
    return figure


@app.cell
def _(casino_model):
    draw_two_state_diagram(casino_model, symbol_label = "Roll")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 1: Simulating the casino </font>

    Let's start by simulating the casino, so we know the true hidden states, and
    can later check how well we recover them.
    Simulating an HMM is a lot like simulating the Markov chains of earlier
    exercises, with one extra step at each position.

    Complete the `simulate_hmm` function below.
    It works with **any** HMM stored in a dictionary like `casino_model`, not just
    the casino.
    It will simulate a sequence of hidden states and the symbols (observed states)
    they emit.
    For the casino model, this is a sequence of die rolls, where the hidden states
    are whether the die is fair or loaded, and the observed states are the numbers
    rolled (1&ndash;6).

    Replace each of the three `None`s with code that does what the comment above
    it says.
    A recipe:

    1.  Choose the **first** hidden state, using the start probabilities
    2.  At each position (roll of the die) in the sequence:
        1.  Choose the symbol (observed state) that the current state **emits**,
            using the emission probabilities of the current state
        2.  Choose the **next** hidden state (for the next roll), using the
            transition probabilities of the current state

    The loop already records each state and symbol for you.

    /// tip
    Remember from the substitution models exercise:
    `rng.choices(options, weights = probabilities)[0]` picks one of the `options`,
    with the given probabilities.
    For example:

    -   `rng.choices(range(number_of_states), weights = model["start"])[0]` picks a
        state **number** (0 or 1 for the casino) using the start probabilities
    -   `model["emissions"][state]` is the row of emission probabilities of
        `state`, and `model["transitions"][state]` is its row of transition
        probabilities
    ///
    """)
    return


@app.function
def simulate_hmm(model, length, rng):
    """Simulate hidden states and the symbols they emit from an HMM.

    Args:
        model (dict): An HMM, with the keys "states", "symbols", "start",
            "transitions", and "emissions" (see `casino_model`).
        length (int): The number of symbols to simulate.
        rng (random.Random): The random number generator to use.

    Returns:
        tuple[list[str], list[int]]: The simulated symbols, and the hidden
            state (as a number: 0 for the first state, 1 for the second, and so
            on) at each position.

    Examples:
        >>> simulate_hmm(casino_model, 0, random.Random(1))
        ([], [])
    """
    number_of_states = len(model["states"])
    symbols = []
    states = []
    # 1. Replace `None` with a random first state, using the start
    #    probabilities
    state = None
    for position in range(length):
        # 2. Replace `None` with a random symbol emitted by the current state,
        #    using its emission probabilities
        symbol = None
        states.append(state)
        symbols.append(symbol)
        # 3. Replace `None` with a random next state, using the transition
        #    probabilities of the current state
        next_state = None
        state = next_state
    return symbols, states


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    simulate_hmm_works = True
    _messages = []

    test_model = {
        "states": ["Fair", "Loaded"],
        "symbols": ["1", "2", "3", "4", "5", "6"],
        "start": np.array([0.5, 0.5]),
        "transitions": np.array([
            [0.95, 0.05],
            [0.1, 0.9],
        ]),
        "emissions": np.array([
            [1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6],
            [0.1, 0.1, 0.1, 0.1, 0.1, 0.5],
        ]),
    }

    try:
        # Test 1: With a length of 0, there's nothing to simulate
        _result = simulate_hmm(test_model, 0, random.Random(1))
        if _result != ([], []):
            simulate_hmm_works = False
            _messages.append(
                f"With a length of 0, the result should be ([], []), not {_result}."
            )

        # Test 2: A model that always starts in state 1, always stays there, and
        # always emits "b"
        _certain_model = {
            "states": ["X", "Y"],
            "symbols": ["a", "b"],
            "start": np.array([0.0, 1.0]),
            "transitions": np.array([[0.0, 1.0], [0.0, 1.0]]),
            "emissions": np.array([[1.0, 0.0], [0.0, 1.0]]),
        }
        _result = simulate_hmm(_certain_model, 5, random.Random(2))
        if None in _result[0] or None in _result[1]:
            raise ValueError("Your function returned None for some states or "
                             + "symbols. Did you replace all three of the Nones?")
        if _result != (["b"] * 5, [1] * 5):
            simulate_hmm_works = False
            _messages.append(
                "A model that always starts in state 1, stays there, and emits "
                + "'b' should give (['b', 'b', 'b', 'b', 'b'], [1, 1, 1, 1, 1]), "
                + f"not {_result}."
            )

        # Test 3: A model that always switches states
        _switch_model = dict(_certain_model)
        _switch_model["start"] = np.array([1.0, 0.0])
        _switch_model["transitions"] = np.array([[0.0, 1.0], [1.0, 0.0]])
        _result = simulate_hmm(_switch_model, 4, random.Random(3))
        if _result != (["a", "b", "a", "b"], [0, 1, 0, 1]):
            simulate_hmm_works = False
            _messages.append(
                "A model that starts in state 0 and always switches should give "
                + f"(['a', 'b', 'a', 'b'], [0, 1, 0, 1]), not {_result}. "
                + "Are you using the transition probabilities of the current state?"
            )

        # Test 4: Long-run behavior of the casino
        if simulate_hmm_works:
            _rolls, _states = simulate_hmm(test_model, 30000, random.Random(4))
            _loaded = sum(_states) / len(_states)
            _sixes_when_loaded = sum(
                1 for _roll, _state in zip(_rolls, _states)
                if _state == 1 and _roll == "6"
            ) / max(1, sum(_states))
            print(f"Fraction of rolls with the loaded die: {_loaded:.3f} "
                  + "(expected 0.333)")
            print(f"Fraction of sixes when loaded: {_sixes_when_loaded:.3f} "
                  + "(expected 0.5)")
            if not (0.29 < _loaded < 0.38):
                simulate_hmm_works = False
                _messages.append(
                    "The fraction of rolls with the loaded die is off. Check your "
                    + "transitions."
                )
            if not (0.47 < _sixes_when_loaded < 0.53):
                simulate_hmm_works = False
                _messages.append(
                    "The fraction of sixes rolled with the loaded die is off. "
                    + "Check your emissions."
                )

        # Test 5: The same seed should give the same results
        if (simulate_hmm(test_model, 50, random.Random(5))
                != simulate_hmm(test_model, 50, random.Random(5))):
            simulate_hmm_works = False
            _messages.append("Make sure every random draw uses rng.")

    except Exception as _error:
        simulate_hmm_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )
        if "NoneType" in str(_error):
            _messages.append("Did you replace all three of the Nones?")

    print()
    if simulate_hmm_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your simulate_hmm function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return simulate_hmm_works, test_model


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A night at the casino

    The next cell uses your `simulate_hmm` function to simulate 300 rolls at the
    casino.
    Before you open the box below the rolls, look through the numbers rolled and try
    to guess where the casino used the loaded die.
    **You do not need to edit the next two cells.**
    """)
    return


@app.function(hide_code=True)
def rolls_html(rolls, states = None, per_line = 60):
    """Show rolls in rows, with the rolls of hidden state 1 highlighted.

    Returns:
        str: HTML to display with `mo.Html`.
    """
    lines = []
    for start in range(0, len(rolls), per_line):
        pieces = []
        for i in range(start, min(start + per_line, len(rolls))):
            if states is not None and states[i] == 1:
                pieces.append('<span style="background-color: #f4b6b6; '
                              + f'font-weight: bold;">{rolls[i]}</span>')
            else:
                pieces.append(rolls[i])
        lines.append("".join(pieces))
    return ('<pre style="font-size: 15px; line-height: 1.6;">'
            + "\n".join(lines) + "</pre>")


@app.cell
def _(casino_model, mo, simulate_hmm_works):
    if simulate_hmm_works:
        night_rolls, night_states = simulate_hmm(casino_model, 300,
                                                 random.Random(2093))
        _output = mo.vstack([
            mo.md("**The 300 rolls:**"),
            mo.Html(rolls_html(night_rolls)),
            mo.accordion({
                "Click here to reveal the rolls with the loaded die (in red)":
                    mo.Html(rolls_html(night_rolls, night_states)),
            }),
        ])
    else:
        night_rolls, night_states = None, None
        _output = mo.md("***Waiting — Get your `simulate_hmm` function working "
                        + "first.***")
    _output
    return night_rolls, night_states


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 2: Can you spot the loaded die? </font>

    Double-click this cell and answer the questions below.

    1.  **Before you revealed the hidden states, where did you think the casino
        was using the loaded die? How well did your guesses match the hidden
        states? What made it hard?**

        **Answer**:

    2.  **Once the casino switches to the loaded die, it switches back with
        probability 0.1 before each roll. On average, how many rolls in a row does
        the casino use the loaded die? How about the fair die?**
        (Hint: If something happens with probability $p$ at each step, then on
        average, it takes $1/p$ steps for it to happen.)

        **Answer**:

    You can check your answer to the second question with the next cell, which
    simulates 100,000 rolls and calculates the average length of each run of the
    fair and loaded dice.
    **You do not need to edit the next two cells.**
    We'll use the `get_runs` function again in Part 2.
    """)
    return


@app.function
def get_runs(states, state):
    """Find each run of consecutive positions in the given hidden state.

    Args:
        states (list[int] or numpy.ndarray): The hidden state at each position.
        state (int): Which hidden state to find runs of.

    Returns:
        list[tuple[int, int]]: The start and end of each run, as Python-style
            positions (the end is one past the last position of the run).

    Examples:
        >>> get_runs([0, 1, 1, 0, 0, 1], 1)
        [(1, 3), (5, 6)]
    """
    states = np.asarray(states)
    in_state = np.concatenate(([False], states == state, [False]))
    changes = np.flatnonzero(in_state[1:] != in_state[:-1])
    return [(int(start), int(end)) for start, end in zip(changes[::2], changes[1::2])]


@app.cell
def _(casino_model, mo, simulate_hmm_works):
    mo.stop(
        not simulate_hmm_works,
        mo.md("***Waiting — Get your `simulate_hmm` function working first.***"),
    )

    _rolls, _states = simulate_hmm(casino_model, 100_000, random.Random(10))
    _fair_runs = get_runs(_states, 0)
    _loaded_runs = get_runs(_states, 1)
    mo.md(
        f"""
    | Die | Number of runs | Average length of a run |
    |:--|--:|--:|
    | Fair | {len(_fair_runs)} | {np.mean([_end - _start for _start, _end in _fair_runs]):.1f} rolls |
    | Loaded | {len(_loaded_runs)} | {np.mean([_end - _start for _start, _end in _loaded_runs]):.1f} rolls |
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The probability of the rolls and a path

    Let's call a sequence of hidden states, one for each roll, a ***path***.
    If we knew the path, we could calculate the probability of the rolls **and**
    the path together, by multiplying the probability of each step of the
    process that generated them:

    $$
    P(\text{rolls}, \text{path}) =
    \underbrace{s_{\pi_1}}_{\text{start}} \,
    \underbrace{e_{\pi_1}(x_1)}_{\text{emission}} \,
    \underbrace{a_{\pi_1 \pi_2}}_{\text{transition}} \, e_{\pi_2}(x_2) \,
    a_{\pi_2 \pi_3} \, e_{\pi_3}(x_3) \cdots
    $$

    where $x_i$ is the $i$th roll, $\pi_i$ is the hidden state of the $i$th roll,
    $s_k$ is the start probability of state $k$, $a_{jk}$ is the probability
    of a transition from state $j$ to state $k$, and $e_k(x)$ is the probability
    that state $k$ emits $x$.

    For example, the probability of the rolls `2`, `6`, `6` and the path
    `Fair`, `Loaded`, `Loaded` is:

    $$
    \underbrace{0.5}_{\text{start Fair}} \times
    \underbrace{\tfrac{1}{6}}_{\text{Fair rolls 2}} \times
    \underbrace{0.05}_{\text{Fair} \rightarrow \text{Loaded}} \times
    \underbrace{0.5}_{\text{Loaded rolls 6}} \times
    \underbrace{0.9}_{\text{Loaded} \rightarrow \text{Loaded}} \times
    \underbrace{0.5}_{\text{Loaded rolls 6}} \approx 0.00094
    $$

    In plain English, that is the
    **probability of starting with the Fair die**
    times the
    **probability the Fair die rolls 2**
    times the
    **probability of switching to the loaded die**
    times the
    **probability the Loaded die rolls 6**
    times the
    **probability of keeping the Loaded die for the next roll**
    times the
    **probability the Loaded die rolls 6**.

    With hundreds of rolls, this product gets so small that a computer rounds it
    to zero (this is called ***underflow***).
    So, just like with our tree likelihoods, we'll work with the natural **log**
    of the probability, which turns the product into a sum:

    $$
    \log P(\text{rolls}, \text{path}) = \log s_{\pi_1} + \log e_{\pi_1}(x_1) +
    \sum_{i = 2}^{n} \Big[ \log a_{\pi_{i - 1} \pi_i} + \log e_{\pi_i}(x_i) \Big]
    $$

    ## <font color=red> Challenge 3: The log probability of the rolls and a path </font>

    Complete the `log_joint_probability` function below.
    A recipe:

    1.  Start with the log of the start probability of the first state
        (`path[0]`), and the log of the probability that the first state emits
        the first symbol (`observations[0]`)
        1.  Get the log of the probability of starting with the first hidden state
            (`math.log(model["start"][path[0]])`) and add it to `log_probability`
        2.  Get the index of the first observed symbol (`observations[0]`);
            see Tip 2 below
        3.  Get the log of the probability that the first state emits the first
            symbol (see Tip 3 below)
            and add it to `log_probability`
    2.  Loop over the rest of the positions (`i` in `range(1, len(path))`), and
        at each position `i`, add:
        1.  The log of the probability of a transition from `path[i - 1]` to
            `path[i]` (see Tip 4 below)
        2.  The log of the probability that `path[i]` emits `observations[i]`.
            Remember, you need to get the index of symbol `observations[i]`
            (see Tips 2 & 3 below)

    /// tip
    1.  `math.log(x)` is the natural log of `x`
    2.  To find the emission probabilities of a symbol, you need its index.
        To get the index of `symbol`, you use
        `model["symbols"].index(symbol)`;
        for example,
        `first_symbol_index = model["symbols"].index(observations[0])`
        is the index of the first observed symbol.
    3.  With the symbol's index in hand, you use the
        `model["emissions"]` NumPy array to get the probability that the
        current hidden state emits that symbol.
        For example, `model["emissions"][path[0], first_symbol_index]`
        is the probability that the first state emits the first symbol
    4.  Use the `model["transitions"]` NumPy array to get the probability of a
        transition from the previous hidden state to the current hidden state.
        For example, `math.log(model["transitions"][path[i - 1], path[i]])`
    ///
    """)
    return


@app.function
def log_joint_probability(observations, path, model):
    """Calculate the log probability of a sequence of symbols and a path of states.

    Args:
        observations (list[str] or str): The observed symbols.
        path (list[int]): The hidden state (as a number) at each position; the
            same length as `observations`.
        model (dict): An HMM (see `casino_model`).

    Returns:
        float: The natural log of the probability of the observations and the
            path.

    Examples:
        >>> log_joint_probability("26", [0, 1], casino_model)
        -6.1739...
    """
    log_probability = 0.0
    # Add your code here!
    return log_probability


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(test_model):
    _test_cases = [
        ("2", [0], math.log(0.5) + math.log(1 / 6)),
        ("6", [1], math.log(0.5) + math.log(0.5)),
        ("266", [0, 1, 1], math.log(0.5 * (1 / 6) * 0.05 * 0.5 * 0.9 * 0.5)),
        ("614", [1, 1, 0], math.log(0.5 * 0.5 * 0.9 * 0.1 * 0.1 * (1 / 6))),
        ("3333", [0, 0, 0, 0], math.log(0.5 * (1 / 6) ** 4 * 0.95 ** 3)),
    ]
    _failures = []
    for _rolls, _path, _expected in _test_cases:
        try:
            _found = log_joint_probability(_rolls, _path, test_model)
            _ok = isinstance(_found, (float, np.floating)) and math.isclose(
                _found, _expected, rel_tol = 1e-9)
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
            _ok = False
        if not _ok:
            _failures.append(
                f"  rolls {_rolls!r}, path {_path}: expected {_expected:.4f}, "
                + f"got {_found}"
            )

    log_joint_probability_works = len(_failures) == 0
    if log_joint_probability_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, log_joint_probability failed these cases:\n"
              + "\n".join(_failures))
    return (log_joint_probability_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Which path?

    The next cell uses your function to calculate the log probability of our 300
    rolls with three different paths: the true path from the simulation, a path
    where the casino always uses the fair die, and a path where it always uses the
    loaded die.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(
    casino_model,
    log_joint_probability_works,
    mo,
    night_rolls,
    night_states,
    simulate_hmm_works,
):
    mo.stop(
        not (simulate_hmm_works and log_joint_probability_works),
        mo.md("***Waiting — Get your `simulate_hmm` and `log_joint_probability` "
              + "functions working first.***"),
    )

    _paths = {
        "The true path": night_states,
        "Always fair": [0] * len(night_rolls),
        "Always loaded": [1] * len(night_rolls),
    }
    _rows = []
    for _name, _path in _paths.items():
        _rows.append(
            f"| {_name} | "
            + f"{log_joint_probability(night_rolls, _path, casino_model):.2f} |"
        )
    mo.md(
        "| Path | Log probability of the rolls and the path |\n"
        + "|:--|--:|\n"
        + "\n".join(_rows)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Remember, the most probable path has the log probability closest to zero
    (the least negative number).
    Are you surprised by the results?!
    The true path is probably **less** probable than "always fair."
    (It usually is, but not always; it depends on the rolls.)
    That's because the true path switches dice many times, and each switch is
    improbable (0.05 or 0.1).
    A path can be the true one without being the most probable one, because
    the casino doesn't always do the most probable thing!

    In the real world, we don't know the true path, so our best guess is the
    path with the highest probability.
    How do we find it?

    How many paths are there?
    Each roll could be fair or loaded, so with 300 rolls, there are
    $2^{300} \approx 2 \times 10^{90}$ possible paths.
    That's more paths than there are atoms in the universe (about $10^{80}$), just
    like the number of possible trees in the phylogenetics exercise!
    We can't try them all!

    # Part 2: The Viterbi algorithm

    Luckily, there's a clever way to find the most probable path without trying
    them all, called the ***Viterbi algorithm*** (Viterbi, 1967).
    The key idea: The best path that ends in a given state at position $i$ must
    pass through **one** of the states at position $i - 1$, and if it does, the
    part of it that ends at position $i - 1$ must be the best path that ends in
    **that** state.
    So, we only need to keep track of the best path that ends in each state, at
    each position.

    We fill in a table with one row per hidden state, and one column per
    position.
    Each cell, $V_k(i)$, holds the log probability of the **best** path for the
    first $i$ symbols that ends in state $k$:

    1.  **The first column** comes from the start probabilities:

        $$
        V_k(1) = \log s_k + \log e_k(x_1)
        $$

    2.  **Each later column** comes from the column before it.
        For each state $k$, we try each previous state $j$, and keep the best:

        $$
        V_k(i) = \max_j \Big[ V_j(i - 1) + \log a_{jk} \Big] + \log e_k(x_i)
        $$

        We also record which previous state $j$ was best, as a ***pointer***.

    3.  **Traceback**: When the table is full, the best score in the last column
        is the log probability of the most probable path.
        To find the path itself, we start at the best state in the last column,
        and follow the pointers backward.

    Does this sound familiar?
    It's ***dynamic programming***, just like sequence alignment: Fill in a
    table, one cell at a time, by choosing the best of a few options, and then
    trace back to find how you got there.
    It's also a lot like the pruning algorithm, but where the pruning algorithm
    **adds up** the probabilities over the bases of a hidden ancestor, the
    Viterbi algorithm takes the **best** (maximum) over the hidden states.

    /// details | Optional: What if we add instead of taking the best?
    If we replace the maximum with a sum (of probabilities, not log
    probabilities), we get the ***forward algorithm***, which calculates the
    probability of the observations, summed over **all** possible paths.
    That's exactly what the pruning algorithm does for the bases at the nodes of
    a tree!
    The forward algorithm (and its partner, the backward algorithm) can tell us
    how confident we should be about the hidden state at each position, and is
    used to train HMMs when we don't know any of the hidden states.
    ///

    ## Visualizing the Viterbi algorithm at work

    The animation below runs the Viterbi algorithm on a few rolls at the
    casino.
    Click "Play" to watch it, or step through it with "Previous" and "Next."
    At each step, the algorithm fills in the next column of the table (the orange
    cells), using the column before it.
    The blue arrows are the pointers: They point to the previous state that gave
    the best score.
    After the table is full, the traceback follows the arrows backward (in gold)
    to find the most probable path.

    Change the rolls in the box, and watch how the path changes.
    For example, how many sixes in a row does it take for the path to switch to
    the loaded die?
    **You do not need to edit the next four cells.**
    """)
    return


@app.function(hide_code=True)
def draw_viterbi_step(observations, model, step,
                      colors = ("steelblue", "firebrick")):
    """Draw the Viterbi algorithm after `step` steps.

    Step 0 is before anything is calculated; steps 1 to n fill in the columns
    of the table, one per observation; steps n + 1 to 2n trace back the most
    probable path, from the last observation to the first. This function does
    its own calculations, so it works before you have completed the challenges.

    Returns:
        matplotlib.figure.Figure: The figure.
    """
    observations = list(observations)
    n = len(observations)
    names = model["states"]
    number_of_states = len(names)
    log_start = np.log(model["start"])
    log_transitions = np.log(model["transitions"])
    log_emissions = np.log(model["emissions"])

    # Run the Viterbi algorithm, keeping everything we need to show
    indices = [model["symbols"].index(symbol) for symbol in observations]
    scores = np.zeros((n, number_of_states))
    pointers = np.zeros((n, number_of_states), dtype = int)
    scores[0] = log_start + log_emissions[:, indices[0]]
    for i in range(1, n):
        candidates = scores[i - 1][:, None] + log_transitions
        pointers[i] = candidates.argmax(axis = 0)
        scores[i] = candidates.max(axis = 0) + log_emissions[:, indices[i]]
    path = [0] * n
    path[-1] = int(scores[-1].argmax())
    for i in range(n - 1, 0, -1):
        path[i - 1] = int(pointers[i, path[i]])

    last_step = 2 * n
    step = max(0, min(step, last_step))
    filled = min(step, n)
    current = step - 1 if 1 <= step <= n else None
    traced = []
    if step > n:
        traced = list(range(n - (step - n), n))

    figure = plt.figure(figsize = (11, 5.6))
    table = figure.add_axes([0.02, 0.33, 0.96, 0.60])
    text = figure.add_axes([0.02, 0.0, 0.96, 0.31])
    table.set_xlim(-1.7, n - 0.4)
    table.set_ylim(1.25 * number_of_states + 2.0, -0.7)
    table.axis("off")
    text.axis("off")

    width, height = 0.62, 0.62

    def row_of(k):
        return 1.3 + 1.25 * k

    # The observations along the top
    table.text(-0.6, 0, "Roll", ha = "right", va = "center", fontsize = 12,
               fontweight = "bold")
    for i, symbol in enumerate(observations):
        table.add_patch(plt.Rectangle((i - width / 2, -height / 2), width,
                                      height, facecolor = "whitesmoke",
                                      edgecolor = "gray"))
        table.text(i, 0, symbol, ha = "center", va = "center", fontsize = 15,
                   fontweight = "bold")
    # The table of scores
    for k in range(number_of_states):
        table.text(-0.6, row_of(k), names[k], ha = "right", va = "center",
                   fontsize = 12, fontweight = "bold", color = colors[k])
        for i in range(n):
            face, edge, line = "white", "lightgray", 1
            if i < filled:
                face = "#dbe8f5"
                if scores[i, k] == scores[i].max():
                    face = "#a9c8e8"
            if i in traced and path[i] == k:
                face, edge, line = "gold", "darkgoldenrod", 2.5
            if i == current:
                edge, line = "darkorange", 2.5
            table.add_patch(plt.Rectangle(
                (i - width / 2, row_of(k) - height / 2), width, height,
                facecolor = face, edgecolor = edge, linewidth = line, zorder = 2))
            if i < filled:
                table.text(i, row_of(k), f"{scores[i, k]:.1f}", ha = "center",
                           va = "center", fontsize = 10, zorder = 3)

    def arrow(i, k_from, k_to, color, line = 2.0, style = "-"):
        table.add_patch(FancyArrowPatch(
            (i - 1 + width / 2, row_of(k_from)), (i - width / 2, row_of(k_to)),
            arrowstyle = "-|>", mutation_scale = 12, linewidth = line,
            color = color, linestyle = style, zorder = 4, shrinkA = 1,
            shrinkB = 1))

    # Pointer arrows into every column filled so far (which previous state was
    # best?); they stay visible for the rest of the animation
    for i in range(1, filled):
        for k in range(number_of_states):
            arrow(i, pointers[i, k], k, "steelblue", 2.5)
    # In the current column, also show the options that lost (gray, dashed)
    if current is not None and current >= 1:
        for k in range(number_of_states):
            for j in range(number_of_states):
                if j != pointers[current, k]:
                    arrow(current, j, k, "lightgray", 1.2, "--")
    # Arrows along the path we have traced back so far, drawn over the blue
    # pointer arrows
    for i in traced:
        if i >= 1 and (i - 1) in traced:
            arrow(i, path[i - 1], path[i], "darkgoldenrod", 3.5)
    # The path along the bottom
    path_row = 1.3 + 1.25 * number_of_states
    if traced:
        table.text(-0.6, path_row, "Path", ha = "right", va = "center",
                   fontsize = 12, fontweight = "bold")
    for i in traced:
        table.text(i, path_row, names[path[i]][0], ha = "center", va = "center",
                   fontsize = 15, fontweight = "bold", color = colors[path[i]])

    # What happens at this step
    def fmt(value):
        return f"{value:.2f}".replace("-", "−")

    def plus(a, b):
        sign = "−" if b < 0 else "+"
        return f"{fmt(a)} {sign} {fmt(abs(b))}"

    if step == 0:
        lines = [
            "Start: The table has one row per hidden state and one column per roll.",
            "Each cell will hold the log probability of the best path that ends "
            + "in that state at that roll.",
            "We fill in the table one column at a time, from left to right.",
        ]
    elif current == 0:
        symbol = observations[0]
        s = indices[0]
        lines = [f"Column 1 (rolled {symbol}): The first state comes from the "
                 + "start probabilities, so each cell is",
                 "log(start probability) + log(emission probability):"]
        for k in range(number_of_states):
            lines.append(f"    {names[k]}:  {plus(log_start[k], log_emissions[k, s])}"
                         + f" = {fmt(scores[0, k])}")
    elif current is not None:
        i = current
        symbol = observations[i]
        s = indices[i]
        lines = [f"Column {i + 1} (rolled {symbol}): For each state, take the "
                 + "best (max) of [previous score + log(transition probability)],",
                 "then add log(emission probability). The new blue arrows remember "
                 + "which previous state was best:"]
        for k in range(number_of_states):
            options = ",  ".join(plus(scores[i - 1, j], log_transitions[j, k])
                                 for j in range(number_of_states))
            emission = log_emissions[k, s]
            sign = "−" if emission < 0 else "+"
            lines.append(f"    {names[k]}:  max({options}) {sign} "
                         + f"{fmt(abs(emission))} = {fmt(scores[i, k])}"
                         + f"   (from {names[pointers[i, k]]})")
    else:
        i = traced[0]
        if i == n - 1:
            lines = ["Traceback: The table is full! The best score in the last "
                     + f"column is {names[path[i]]} ({fmt(scores[i, path[i]])}),",
                     "which is the log probability of the most probable path.",
                     "Now we follow the arrows backward to find that path."]
        elif i > 0:
            lines = [f"Traceback: Roll {i + 1} is {names[path[i]]}; its arrow "
                     + f"points back to {names[path[i - 1]]} at roll {i}."]
        else:
            decoded = "".join(names[k][0] for k in path)
            lines = [f"Done! The most probable path is {decoded}",
                     "(read from left to right), with a log probability of "
                     + f"{fmt(scores[-1].max())}."]
    text.text(0.0, 0.98, "\n".join(lines), va = "top", ha = "left",
              fontsize = 12, linespacing = 1.6, transform = text.transAxes)
    figure.suptitle(f"Step {step} of {last_step}", fontsize = 14, x = 0.02,
                    ha = "left")
    return figure


@app.function(hide_code=True)
def viterbi_animation_html(observations, model, seconds_per_step = 1.5):
    """Make an HTML player that steps through `draw_viterbi_step`.

    Returns:
        str: HTML (with a little JavaScript) to display with `mo.iframe`.
    """
    import base64
    import io
    import json

    frames = []
    for step in range(2 * len(observations) + 1):
        figure = draw_viterbi_step(observations, model, step)
        buffer = io.BytesIO()
        figure.savefig(buffer, format = "png", dpi = 80)
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
def _(mo):
    animation_rolls_box = mo.ui.text(
        value = "3152416666663142",
        label = "Rolls (up to 16 numbers from 1 to 6):",
    )
    return (animation_rolls_box,)


@app.cell
def _(animation_rolls_box, casino_model, mo):
    _rolls = [_roll for _roll in animation_rolls_box.value if _roll in "123456"][:16]
    if len(_rolls) == 0:
        _rolls = list("3152416666663142")
    mo.vstack([
        animation_rolls_box,
        mo.iframe(viterbi_animation_html(_rolls, casino_model), height = "600px"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 4: One column of the Viterbi table </font>

    Let's write the Viterbi algorithm in two pieces.
    First, complete the `viterbi_step` function below, which calculates one
    column of the table from the column before it (Rule 2 above).
    It takes three NumPy arrays:

    -   `previous_scores`: The previous column of the table, $V_j(i - 1)$, with
        one number per state
    -   `log_transitions`: The log of the transition probabilities; row `j`,
        column `k` is $\log a_{jk}$
    -   `log_emissions_here`: The log of the probability that each state emits
        the symbol at this position, $\log e_k(x_i)$, with one number per state

    It returns the new column of scores, $V_k(i)$, and the pointer to the best
    previous state for each state $k$.

    A recipe:

    For each state number `k` (`range(number_of_states)`):

    1.  Make an empty list, `candidates = []`.
        Then, for each previous state `j`
        (`range(number_of_states)`), append the sum of the previous score for state
        `j` and the log probability of transitioning from previous state `j` to
        current state `k`:
        `previous_scores[j] + log_transitions[j, k]`
    2.  Find the index of the largest candidate with `int(np.argmax(candidates))`,
        and store it in `pointers[k]`
    3.  Set `scores[k]` to the largest candidate score plus `log_emissions_here[k]`

    /// tip
    Be careful with the order of the indices in `log_transitions[j, k]`: We're
    going **from** the previous state `j` **to** the current state `k`.
    ///
    """)
    return


@app.function
def viterbi_step(previous_scores, log_transitions, log_emissions_here):
    """Calculate one column of the Viterbi table from the column before it.

    Args:
        previous_scores (numpy.ndarray): The previous column, with the best log
            probability of a path ending in each state at the previous position.
        log_transitions (numpy.ndarray): Row j, column k is the log of the
            probability of a transition from state j to state k.
        log_emissions_here (numpy.ndarray): The log of the probability that each
            state emits the symbol at this position.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]: The new column of scores (one per
            state), and the pointers (the number of the best previous state,
            for each state).

    Examples:
        >>> viterbi_step(np.array([-1.0, -5.0]),
        ...              np.log(np.array([[0.9, 0.1], [0.2, 0.8]])),
        ...              np.log(np.array([0.5, 0.25])))
        (array([-1.79..., -4.68...]), array([0, 0]))
    """
    number_of_states = len(previous_scores)
    # Create an initial numpy array of zeros (floats) for each state
    scores = np.zeros(number_of_states)
    # Create an initial numpy array of zeros (integers) for each state
    pointers = np.zeros(number_of_states, dtype = int)
    # Add your code here!
    return scores, pointers


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    _log_t = np.log(np.array([[0.9, 0.1], [0.2, 0.8]]))
    _log_t3 = np.log(np.array([
        [0.6, 0.3, 0.1],
        [0.1, 0.1, 0.8],
        [0.3, 0.3, 0.4],
    ]))
    _test_cases = [
        # (previous_scores, log_transitions, log_emissions_here,
        #  expected scores, expected pointers)
        ([-1.0, -2.0], _log_t, np.log([0.5, 0.25]),
         [-1.0 + math.log(0.9) + math.log(0.5), -2.0 + math.log(0.8) + math.log(0.25)],
         [0, 1]),
        ([-1.0, -5.0], _log_t, np.log([0.5, 0.25]),
         [-1.0 + math.log(0.9) + math.log(0.5), -1.0 + math.log(0.1) + math.log(0.25)],
         [0, 0]),
        ([-6.0, -1.0], _log_t, np.log([0.1, 0.4]),
         [-1.0 + math.log(0.2) + math.log(0.1), -1.0 + math.log(0.8) + math.log(0.4)],
         [1, 1]),
        ([-2.0, -1.0, -3.0], _log_t3, np.log([0.2, 0.5, 0.3]),
         [-2.0 + math.log(0.6) + math.log(0.2), -2.0 + math.log(0.3) + math.log(0.5),
          -1.0 + math.log(0.8) + math.log(0.3)],
         [0, 0, 1]),
    ]
    _failures = []
    for _previous, _log_trans, _log_em, _expected_scores, _expected_pointers in _test_cases:
        try:
            _scores, _pointers = viterbi_step(np.array(_previous), _log_trans,
                                              np.array(_log_em))
            _ok = (np.shape(_scores) == (len(_previous),)
                   and np.allclose(_scores, _expected_scores)
                   and list(np.asarray(_pointers)) == _expected_pointers)
            _found = (f"scores {np.round(_scores, 3)}, pointers "
                      + f"{[int(_p) for _p in _pointers]}")
        except Exception as _error:
            _found = f"an error ({type(_error).__name__}: {_error})"
            _ok = False
        if not _ok:
            _failures.append(
                f"  previous_scores {_previous}: expected scores "
                + f"{np.round(_expected_scores, 3)}, pointers {_expected_pointers}; "
                + f"got {_found}"
            )

    viterbi_step_works = len(_failures) == 0
    if viterbi_step_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, viterbi_step failed these cases:\n" + "\n".join(_failures))
    return (viterbi_step_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell defines a function we will need for Challenge 5.
    It converts observed symbols into their indices in `model["symbols"]`.
    **You do not need to edit the next cell.**
    """)
    return


@app.function
def symbol_indices(observations, model):
    """Convert observed symbols into their indices in model["symbols"].

    Returns:
        numpy.ndarray: The index of each symbol.

    Examples:
        >>> symbol_indices("1626", casino_model)
        array([0, 5, 1, 5])
    """
    lookup = {symbol: index for index, symbol in enumerate(model["symbols"])}
    return np.array([lookup[symbol] for symbol in observations], dtype = int)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 5: Tracing back </font>

    Now, let's put the whole algorithm together.
    The `viterbi` function below already fills in the table, using your
    `viterbi_step` function for every column after the first.
    It stores the Viterbi table in a NumPy array called `scores`, where row `i` is
    the column of the table for position `i` (so `scores[i, k]` is $V_k(i)$).
    It also stores the pointers in an array called `pointers`, where `pointers[i,
    k]` is the best previous state for state `k` at position `i`.

    Your job is to write the ***traceback***, which fills in the list `path`, from
    the **last** position to the first:

    1.  Set the state of the last position, `path[n - 1]`, to the state with the
        best score in the last row of `scores`
    2.  Loop **backward** over the positions, from `i = n - 1` down to `i = 1`; at
        each position, the state of the position before it, `path[i - 1]`, is
        the pointer of the state at position `i`: `pointers[i, path[i]]`

    /// tip
    1.  `int(np.argmax(scores[n - 1]))` is the number of the state with the best
        score in the last row
    2.  `range(n - 1, 0, -1)` counts backward from `n - 1` down to 1 (the third
        number, `-1`, is the step, and, as always, `range` stops **before** the
        second number)
    3.  Use `int(...)` around each value you store in `path`, so `path` is a list
        of regular Python integers
    ///
    """)
    return


@app.function
def viterbi(observations, model):
    """Find the most probable path of hidden states with the Viterbi algorithm.

    Args:
        observations (list[str] or str): The observed symbols.
        model (dict): An HMM (see `casino_model`).

    Returns:
        tuple[list[int], float]: The most probable path (the number of the
            hidden state at each position), and the log probability of the
            observations and that path.

    Examples:
        >>> viterbi("666", casino_model)
        ([1, 1, 1], -2.983...)
    """
    log_start = np.log(model["start"])
    log_transitions = np.log(model["transitions"])
    log_emissions = np.log(model["emissions"])
    indices = symbol_indices(observations, model)
    n = len(indices)
    number_of_states = len(model["states"])
    if n == 0:
        return [], 0.0

    # Fill in the table (you do not need to edit this part)
    scores = np.zeros((n, number_of_states))
    pointers = np.zeros((n, number_of_states), dtype = int)
    scores[0] = log_start + log_emissions[:, indices[0]]
    for i in range(1, n):
        scores[i], pointers[i] = viterbi_step(
            scores[i - 1], log_transitions, log_emissions[:, indices[i]]
        )
    best_log_probability = float(np.max(scores[n - 1]))

    # The traceback
    # Start with a path of zeros
    path = [0] * n
    # Add your code here!
    return path, best_log_probability


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    It runs your `viterbi` function on some short sequences of rolls, and checks
    its path against the best path found by trying **every** possible path (which
    we can do for short sequences).
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _(test_model, viterbi_step_works):
    import itertools as _itertools

    def _brute_force(observations, model):
        # Try every possible path, and keep the best one
        _best_path, _best = None, -math.inf
        _number_of_states = len(model["states"])
        for _path in _itertools.product(range(_number_of_states),
                                        repeat = len(observations)):
            _s = [model["symbols"].index(_x) for _x in observations]
            _value = math.log(model["start"][_path[0]]) + math.log(
                model["emissions"][_path[0], _s[0]])
            for _i in range(1, len(_path)):
                _value += math.log(model["transitions"][_path[_i - 1], _path[_i]])
                _value += math.log(model["emissions"][_path[_i], _s[_i]])
            if _value > _best:
                _best_path, _best = list(_path), _value
        return _best_path, _best

    _three_state_model = {
        "states": ["X", "Y", "Z"],
        "symbols": ["a", "b"],
        "start": np.array([0.2, 0.5, 0.3]),
        "transitions": np.array([[0.7, 0.2, 0.1], [0.3, 0.3, 0.4],
                                 [0.05, 0.15, 0.8]]),
        "emissions": np.array([[0.9, 0.1], [0.4, 0.6], [0.15, 0.85]]),
    }
    _test_cases = [
        ("6", test_model),
        ("3", test_model),
        ("666", test_model),
        ("12666", test_model),
        ("6661235", test_model),
        ("31666662", test_model),
        ("abbab", _three_state_model),
        ("aaabbbba", _three_state_model),
    ]
    _failures = []
    if not viterbi_step_works:
        _failures.append("  Get your viterbi_step function working first.")
    else:
        for _observations, _model in _test_cases:
            _expected_path, _expected_best = _brute_force(_observations, _model)
            try:
                _path, _best = viterbi(_observations, _model)
                _ok = (list(_path) == _expected_path
                       and math.isclose(_best, _expected_best, rel_tol = 1e-9))
                _found = f"path {[int(_s) for _s in _path]}, log probability {_best:.4f}"
                if _ok and not all(type(_state) is int for _state in _path):
                    _ok = False
                    _found += (" (the right path, but use int(...) to store "
                               + "regular Python integers in path)")
            except Exception as _error:
                _found = f"an error ({type(_error).__name__}: {_error})"
                _ok = False
            if not _ok:
                _failures.append(
                    f"  {_observations!r}: expected path {_expected_path}, log "
                    + f"probability {_expected_best:.4f}; got {_found}"
                )

    viterbi_works = len(_failures) == 0
    if viterbi_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, viterbi failed these cases:\n" + "\n".join(_failures))
    return (viterbi_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 6: Plotting the hidden states </font>

    To see how well the Viterbi algorithm does, let's plot the true hidden states
    and the path it finds.
    Complete the `plot_paths` function below, which plots two paths of hidden
    states on the same axes, as ***step plots***: lines that stay flat until the
    hidden state changes, and then jump straight up or down to the new state.
    You'll use this function again in Part 3, so it takes the names of the
    states and the labels of the two paths as arguments.

    A recipe:

    1.  Make a figure with one set of axes:
        `figure, axes = plt.subplots(figsize = (10, 3))`
    2.  Plot the first path as a thick black step plot:
        `axes.step(positions, path_1, where = "post", color = "black", linewidth = 4, label = label_1)`
    3.  Plot the second path the same way, but in `color = "darkorange"`, with
        `linewidth = 1.5`, and `label = label_2` (so we can see it on top of the
        first path)
    4.  Label the y-axis ticks with the names of the states:
        `axes.set_yticks(range(len(state_names)), state_names)`
    5.  Label the x-axis with `axes.set_xlabel("...")` (replace `...` with a
        helpful label), give the plot a title with `axes.set_title(title)`, and
        add a legend with `axes.legend()`
    6.  The function already returns `figure`

    `positions` is already defined for you at the beginning of the function; it
    holds the position number of each hidden state (`0, 1, 2, ...`), plus `start`,
    so that the plot can show where the positions are in a longer sequence.
    """)
    return


@app.function
def plot_paths(path_1, path_2, state_names, label_1, label_2, title = "",
               start = 0):
    """Plot two paths of hidden states as step plots on the same axes.

    Args:
        path_1 (list[int]): The first path (a hidden state number per position).
        path_2 (list[int]): The second path, the same length as `path_1`.
        state_names (list[str]): The name of each hidden state.
        label_1 (str): The legend label of the first path.
        label_2 (str): The legend label of the second path.
        title (str): The title of the plot.
        start (int): The position of the first hidden state.

    Returns:
        matplotlib.figure.Figure: The figure (or None, until the function is
            complete).
    """
    positions = np.arange(len(path_1)) + start
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
    plot_paths_works = True
    _messages = []
    try:
        _figure = plot_paths([0, 0, 1, 1, 0], [0, 1, 1, 1, 0], ["Fair", "Loaded"],
                             "True", "Viterbi", title = "Test")
        if not isinstance(_figure, plt.Figure):
            plot_paths_works = False
            _messages.append(
                f"Your function should return a figure, not {type(_figure).__name__}."
            )
        elif len(_figure.axes) != 1:
            plot_paths_works = False
            _messages.append("Your figure should have one set of axes.")
        else:
            _axes = _figure.axes[0]
            if len(_axes.lines) < 2:
                plot_paths_works = False
                _messages.append("Your axes should have two step plots (lines).")
            if _axes.get_xlabel() == "":
                plot_paths_works = False
                _messages.append("Your x-axis needs a label.")
            if _axes.get_title() != "Test":
                plot_paths_works = False
                _messages.append("Your plot should use the title argument.")
            if _axes.get_legend() is None:
                plot_paths_works = False
                _messages.append("Your plot needs a legend.")
            else:
                _labels = [_t.get_text() for _t in _axes.get_legend().get_texts()]
                if "True" not in _labels or "Viterbi" not in _labels:
                    plot_paths_works = False
                    _messages.append(
                        "Your legend should use the label_1 and label_2 arguments."
                    )
            _tick_labels = [_t.get_text() for _t in _axes.get_yticklabels()]
            if _tick_labels != ["Fair", "Loaded"]:
                plot_paths_works = False
                _messages.append(
                    "The y-axis ticks should be labeled with the state names."
                )
        if isinstance(_figure, plt.Figure):
            plt.close(_figure)
    except Exception as _error:
        plot_paths_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )

    if plot_paths_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your plot_paths function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (plot_paths_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Catching the casino

    The next cell uses your `viterbi` function to find the most probable path for
    our 300 rolls, and uses your `plot_paths` function to compare it to the true
    path.
    It also calculates the ***accuracy***: the fraction of rolls where the
    Viterbi path has the correct die.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(
    casino_model,
    log_joint_probability_works,
    mo,
    night_rolls,
    night_states,
    plot_paths_works,
    simulate_hmm_works,
    viterbi_works,
):
    mo.stop(
        not (simulate_hmm_works and log_joint_probability_works and viterbi_works
             and plot_paths_works),
        mo.md("***Waiting — Get your `simulate_hmm`, `log_joint_probability`, "
              + "`viterbi`, and `plot_paths` functions working first.***"),
    )

    _path, _log_probability = viterbi(night_rolls, casino_model)
    _accuracy = np.mean(np.array(_path) == np.array(night_states))
    _figure = plot_paths(night_states, _path, casino_model["states"],
                         "True path", "Viterbi path",
                         title = "300 rolls at the casino")
    mo.vstack([
        _figure,
        mo.md(
            f"""
    | | |
    |:--|--:|
    | Log probability of the rolls and the Viterbi path | {_log_probability:.2f} |
    | Log probability of the rolls and the true path | {log_joint_probability(night_rolls, night_states, casino_model):.2f} |
    | Accuracy of the Viterbi path | {_accuracy:.3f} |
    | Accuracy of "always fair" | {np.mean(np.array(night_states) == 0):.3f} |
    """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 7: How well did Viterbi do? </font>

    Double-click this cell and answer the questions below.

    1.  **For our 300 rolls, how accurate was the Viterbi path? Where did it make
        mistakes? Why do you think it missed those?**

        **Answer**:

    2.  **The log probability of the rolls and the Viterbi path is higher than
        that of the rolls and the true path. How can that be?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How loaded is the loaded die?

    The slider below changes the probability that the loaded die rolls a 6 (the
    other five numbers share the remaining probability equally).
    For each setting, the next cell simulates 500 rolls, and then finds the
    Viterbi path, using the right probabilities.
    **Use the slider, and watch what happens to the accuracy.**
    **You do not need to edit the next two cells.**

    /// note
    Because the second cell below always uses the same random seed, the casino
    switches dice at exactly the same rolls for every setting of the slider, so the
    true path (black) stays the same.
    Only the rolls change, because the loaded die rolls differently.
    This way, any change in accuracy comes only from how different the two dice
    are, not from a different night at the casino.
    ///
    """)
    return


@app.cell
def _(mo):
    six_slider = mo.ui.slider(
        start = 0.20, stop = 0.90, step = 0.05, value = 0.50, show_value = True,
        label = "Probability that the loaded die rolls a 6",
    )
    return (six_slider,)


@app.cell
def _(
    casino_model,
    mo,
    plot_paths_works,
    simulate_hmm_works,
    six_slider,
    viterbi_works,
):
    mo.stop(
        not (simulate_hmm_works and viterbi_works and plot_paths_works),
        mo.md("***Waiting — Get your `simulate_hmm`, `viterbi`, and `plot_paths` "
              + "functions working first.***"),
    )

    _six = six_slider.value
    _model = dict(casino_model)
    _model["emissions"] = np.array([
        [1 / 6] * 6,
        [(1 - _six) / 5] * 5 + [_six],
    ])
    _rolls, _states = simulate_hmm(_model, 500, random.Random(2026))
    _path, _ = viterbi(_rolls, _model)
    _accuracy = np.mean(np.array(_path) == np.array(_states))
    mo.vstack([
        six_slider,
        plot_paths(_states, _path, _model["states"], "True path", "Viterbi path",
                   title = f"Loaded die rolls a 6 with probability {_six:.2f}: "
                   + f"accuracy = {_accuracy:.3f}"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 8: Emission probabilities and the HMM's accuracy </font>

    Double-click this cell and answer the question below.

    1.  **What happens to the accuracy as the probability of rolling a 6 with the
        loaded die gets closer to 1/6 (about 0.17)? What happens as it gets
        closer to 0.9? Why?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part 3: Finding CpG islands in the human genome

    Now let's use HMMs and the **same** `viterbi` function on DNA.

    ## CpG depletion

    A ***CpG*** is a C followed by a G on the same strand of DNA (the "p" stands
    for the phosphate that links them, to tell it apart from a C–G base pair).
    In vertebrates, the C in most CpGs carries a ***methyl group***.
    A methylated C easily mutates to a T, so over evolutionary time, many CpGs
    have mutated to TpG (or CpA, on the other strand).
    As a result, CpGs are much rarer in vertebrate genomes than we'd expect from
    how often C and G occur.
    This is called ***CpG depletion***.

    But here and there are stretches, a few hundred to a few thousand bases long,
    where CpGs are **not** depleted.
    These are called ***CpG islands***.
    The C's in CpG islands are usually **not** methylated, and many CpG islands
    sit at the start of genes, where they help control when genes are turned on.
    So, finding CpG islands is one way to find genes!

    We'll use a 2-million-base stretch of human Chromosome 19, along with the CpG
    islands found in it by the UCSC Genome Browser (Kent *et al.*, 2002), and
    the start of each gene in it, from the MANE project (Morales *et al.*,
    2022).
    The UCSC Genome Browser found these islands with a set of rules based on the
    length, GC content, and CpG content of each stretch of DNA (Gardiner-Garden
    and Frommer, 1987).
    We'll use them to **train** an HMM, and then see if the HMM can find CpG
    islands on its own.

    The next cell downloads the sequence and its features, and the cell after it
    makes `island_labels`, a NumPy array with the hidden state of each position
    (0 for background, and 1 for a CpG island).
    The table summarizes the sequence.
    The ***observed/expected CpG ratio*** is the number of CpGs, divided by the
    number we'd expect if C's and G's were next to each other only by chance
    (the number of C's times the number of G's, divided by the length).
    A ratio of 1 means no depletion.
    A ratio less than 1 suggests depletion.
    **You do not need to edit the next five cells.**

    /// note
    The fifth cell might take a while to run; that is normal.
    ///
    """)
    return


@app.function
def read_fasta_url(url):
    """Download a FASTA file with one sequence, and return the sequence.

    Returns:
        str: The sequence, in uppercase.
    """
    import urllib.request

    with urllib.request.urlopen(url) as response:
        text = response.read().decode("utf-8")
    sequence_lines = []
    for line in text.splitlines():
        if not line.startswith(">"):
            sequence_lines.append(line.strip())
    return "".join(sequence_lines).upper()


@app.function
def read_features_url(url):
    """Download a tab-separated file of features, and return a list of them.

    Returns:
        list[dict]: One dictionary per feature, with the keys "feature", "start",
            "end", "name", and "strand" (start and end are integers).
    """
    import urllib.request

    with urllib.request.urlopen(url) as response:
        text = response.read().decode("utf-8")
    features = []
    header = None
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        fields = line.split("\t")
        if header is None:
            header = fields
            continue
        feature = dict(zip(header, fields))
        feature["start"] = int(feature["start"])
        feature["end"] = int(feature["end"])
        features.append(feature)
    return features


@app.function
def cpg_ratio(sequence):
    """Calculate the observed/expected CpG ratio of a sequence.

    Returns:
        float: The number of "CG"s divided by (number of C's x number of G's /
            length).
    """
    c_count = sequence.count("C")
    g_count = sequence.count("G")
    expected = c_count * g_count / len(sequence)
    return sequence.count("CG") / expected


@app.cell
def _():
    chr19_sequence = read_fasta_url(CPG_FASTA_URL)
    chr19_features = read_features_url(CPG_FEATURES_URL)
    return chr19_features, chr19_sequence


@app.cell
def _(chr19_features, chr19_sequence, mo):
    island_labels = np.zeros(len(chr19_sequence), dtype = int)
    for _feature in chr19_features:
        if _feature["feature"] == "cpg_island":
            island_labels[_feature["start"]:_feature["end"]] = 1

    _island_runs = get_runs(island_labels, 1)
    _background_runs = get_runs(island_labels, 0)
    _islands = "".join(chr19_sequence[_s:_e] for _s, _e in _island_runs)
    _background = "".join(chr19_sequence[_s:_e] for _s, _e in _background_runs)
    _gc = lambda _seq: (_seq.count("G") + _seq.count("C")) / len(_seq)
    _genes = [_f for _f in chr19_features if _f["feature"] == "gene"]

    # The hidden states of the bases we test our HMMs on
    test_labels = island_labels[TRAINING_END:]

    mo.md(
        f"""
    | | Whole sequence | CpG islands | Background |
    |:--|--:|--:|--:|
    | Length (bases) | {len(chr19_sequence):,} | {len(_islands):,} | {len(_background):,} |
    | Number of stretches | | {len(_island_runs)} | {len(_background_runs)} |
    | GC content | {_gc(chr19_sequence):.3f} | {_gc(_islands):.3f} | {_gc(_background):.3f} |
    | Observed/expected CpG ratio | {cpg_ratio(chr19_sequence):.3f} | {cpg_ratio(_islands):.3f} | {cpg_ratio(_background):.3f} |

    The sequence also has {len(_genes)} protein-coding genes.
    """
    )
    return island_labels, test_labels


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In the background DNA, there are only about 38% as many CpGs as we'd expect,
    but inside the CpG islands, they are much more common.
    Notice that CpG islands are also richer in G and C overall.
    (This part of Chromosome 19 is unusually GC-rich; across the whole human
    genome, the observed/expected CpG ratio is only about 0.2 to 0.25.)

    ## Training an HMM by counting

    So far, someone gave us the probabilities of the model.
    In the real world, we usually need to ***estimate*** them from data.
    When we know the hidden states (like the islands that UCSC found), that's
    easy: We just **count**!

    -   The probability that state $k$ emits symbol $s$ is the number of times
        state $k$ emitted $s$, divided by the number of positions in state $k$
    -   The probability of a transition from state $j$ to state $k$ is the number
        of times state $j$ was followed by state $k$, divided by the number of
        times state $j$ was followed by anything

    Using data to estimate the parameters of a model is called ***training***
    the model.
    You'll see this word a lot when we get to machine learning!

    ## <font color=red> Challenge 9: Training by counting </font>

    Complete the `train_hmm` function below.
    It takes a sequence of observed symbols, and the known hidden state of each
    position, and returns a new HMM (a dictionary like `casino_model`) with the
    estimated probabilities.

    Replace the "`# Add your code here!`" comment using the following recipe:

    1.  Loop over the position indices (`range(number_of_positions)`), and at each
        position `i`, add 1 to `emission_counts[states[i], symbol_index]`, where
        `symbol_index` is the index of `observations[i]` (use the `lookup`
        dictionary: `symbol_index = lookup[observations[i]]`)
    2.  Loop over the position indices starting from 1
        (`range(1, number_of_positions)`), and at each position `i`, add 1 to
        `transition_counts[states[i - 1], states[i]]`

    The rest of the function (which converts the counts into probabilities) is
    already written for you.

    /// note
    Notice that the counts start at 1 instead of 0.
    These extra counts are called ***pseudocounts***.
    They make sure that no probability is exactly 0, even if we never saw
    something in our training data.
    A probability of 0 would make its log $-\infty$, and would make it impossible
    for the HMM to ever use that transition or emission, even if it should.
    ///
    """)
    return


@app.function
def train_hmm(observations, states, symbols, state_names):
    """Estimate the probabilities of an HMM by counting, with pseudocounts of 1.

    Args:
        observations (list[str] or str): The observed symbols at each position.
        states (list[int] or numpy.ndarray): The known hidden state (as a number)
            at each position.
        symbols (list[str]): All the symbols that could be observed.
        state_names (list[str]): The name of each hidden state.

    Returns:
        dict: An HMM with the keys "states", "symbols", "start", "transitions",
            and "emissions".

    Examples:
        >>> train_hmm("AACG", [0, 0, 1, 1], list(BASES), ["Out", "In"])["emissions"]
        array([[0.5       , 0.1666..., 0.1666..., 0.1666...],
               [0.1666..., 0.3333..., 0.3333..., 0.1666...]])
    """
    number_of_positions = len(observations)
    # Make sure observations and states have the same length
    assert number_of_positions == len(states)
    number_of_states = len(state_names)
    # Create a dict for looking up the index of each symbol
    lookup = {symbol: index for index, symbol in enumerate(symbols)}
    # Initialize all emission counts at 1
    emission_counts = np.ones((number_of_states, len(symbols)))
    # Initialize all transition counts at 1
    transition_counts = np.ones((number_of_states, number_of_states))
    # Add your code here!

    # Convert the counts into probabilities (you do not need to edit this part)
    state_counts = np.bincount(np.asarray(states, dtype = int),
                               minlength = number_of_states) + 1
    return {
        "states": list(state_names),
        "symbols": list(symbols),
        "start": state_counts / state_counts.sum(),
        "transitions": transition_counts / transition_counts.sum(axis = 1,
                                                                 keepdims = True),
        "emissions": emission_counts / emission_counts.sum(axis = 1,
                                                           keepdims = True),
    }


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function.
    **Note**: You do not need to edit the code in the cell below.
    """)
    return


@app.cell
def _():
    train_hmm_works = True
    _messages = []
    try:
        _model = train_hmm("AACG", [0, 0, 1, 1], list(BASES), ["Out", "In"])
        _expected_emissions = np.array([[3, 1, 1, 1], [1, 2, 2, 1]]) / 6
        _expected_transitions = np.array([[2 / 4, 2 / 4], [1 / 3, 2 / 3]])
        if not np.allclose(_model["emissions"], _expected_emissions):
            train_hmm_works = False
            _messages.append(
                "For observations 'AACG' and states [0, 0, 1, 1], the emission "
                + f"probabilities should be\n{np.round(_expected_emissions, 4)},\n"
                + f"not\n{np.round(_model['emissions'], 4)}"
            )
        if not np.allclose(_model["transitions"], _expected_transitions):
            train_hmm_works = False
            _messages.append(
                "For states [0, 0, 1, 1], the transition probabilities should be\n"
                + f"{np.round(_expected_transitions, 4)},\nnot\n"
                + f"{np.round(_model['transitions'], 4)}"
            )
        _model = train_hmm(["CG", "GA", "AC", "CG"], [1, 1, 0, 1], ["AC", "CG", "GA"],
                           ["Out", "In"])
        if not train_hmm_works:
            _model = None
        _expected_emissions = np.array([[2, 1, 1], [1, 3, 2]]) / np.array([[4], [6]])
        _expected_transitions = np.array([[1 / 3, 2 / 3], [2 / 4, 2 / 4]])
        if _model is not None and not (
                np.allclose(_model["emissions"], _expected_emissions)
                and np.allclose(_model["transitions"], _expected_transitions)):
            train_hmm_works = False
            _messages.append(
                "Your function doesn't work with symbols that are more than one "
                + "letter long, like 'CG'. Are you using the lookup dictionary?"
            )
    except Exception as _error:
        train_hmm_works = False
        _messages.append(
            f"Calling your function gave an error: {type(_error).__name__}: {_error}"
        )

    if train_hmm_works:
        print("Yay, your function passed the test!")
    else:
        print("Sorry, your train_hmm function has a problem:")
        for _message in _messages:
            print("  " + _message)
        print("Please try again!")
    return (train_hmm_works,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Does counting work?

    Before we use your function on DNA, let's check that it works on rolls where
    we know the true probabilities.
    The next cell simulates 50,000 rolls at the casino, trains a new model from
    the rolls and their true hidden states, and compares the estimates to the
    true probabilities.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(casino_model, mo, simulate_hmm_works, train_hmm_works):
    mo.stop(
        not (simulate_hmm_works and train_hmm_works),
        mo.md("***Waiting — Get your `simulate_hmm` and `train_hmm` functions "
              + "working first.***"),
    )

    _rolls, _states = simulate_hmm(casino_model, 50_000, random.Random(50))
    _trained = train_hmm(_rolls, _states, casino_model["symbols"],
                         casino_model["states"])

    def _row(_name, _true, _estimate):
        return (f"| {_name} | " + ", ".join(f"{_x:.3f}" for _x in _true)
                + " | " + ", ".join(f"{_x:.3f}" for _x in _estimate) + " |")

    mo.md(
        "| | True | Estimated |\n|:--|:--|:--|\n"
        + _row("Transitions from Fair", casino_model["transitions"][0],
               _trained["transitions"][0]) + "\n"
        + _row("Transitions from Loaded", casino_model["transitions"][1],
               _trained["transitions"][1]) + "\n"
        + _row("Emissions of Fair", casino_model["emissions"][0],
               _trained["emissions"][0]) + "\n"
        + _row("Emissions of Loaded", casino_model["emissions"][1],
               _trained["emissions"][1])
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Counting recovers the true probabilities very well!

    ## An HMM for CpG islands

    Now for the real thing.
    We'll train our CpG island HMM on the **first** million bases of our
    sequence, and then test it by asking it to find the CpG islands in the
    **second** million bases, which it never saw during training.
    Testing a model on data it wasn't trained on is important: It tells us how
    well the model will work on new data.
    (We'll see this again in the machine learning exercise.)

    Our first HMM has two hidden states, `Background` and `Island`, and each
    state emits single bases (A, C, G, or T).
    The fourth cell below trains the HMM with your `train_hmm` function, draws it,
    and then uses your `viterbi` function to find the most probable path of hidden
    states for the second million bases.
    It plots the islands in a stretch of 50,000 bases with your `plot_paths`
    function, and adds a gray dashed line at the start of each gene.
    The table compares the islands found by the HMM to the islands found by UCSC.
    This cell might take 20 to 30 seconds to run, because your `viterbi`
    function has to fill in a table with two million cells!
    **You do not need to edit the next four cells.**
    """)
    return


@app.function(hide_code=True)
def compare_islands(true_labels, found_labels):
    """Compare the islands found by an HMM to the true islands.

    Returns:
        dict: Summaries of how well the found islands match the true islands.
    """
    true_labels = np.asarray(true_labels)
    found_labels = np.asarray(found_labels)
    true_runs = get_runs(true_labels, 1)
    found_runs = get_runs(found_labels, 1)

    def overlaps(run, labels):
        return bool(labels[run[0]:run[1]].any())

    return {
        "accuracy": float(np.mean(true_labels == found_labels)),
        "background accuracy": float(np.mean(true_labels == 0)),
        "true islands": len(true_runs),
        "true islands found": sum(overlaps(run, found_labels) for run in true_runs),
        "islands found": len(found_runs),
        "islands found that are true": sum(overlaps(run, true_labels)
                                           for run in found_runs),
    }


@app.function(hide_code=True)
def comparison_table(comparisons):
    """Make a markdown table from one or more results of `compare_islands`.

    Args:
        comparisons (dict): The name of each model, and its `compare_islands`
            results.

    Returns:
        str: A markdown table.
    """
    names = list(comparisons)
    rows = [
        ("Accuracy (fraction of bases in the right state)", "accuracy", "{:.3f}"),
        ("Accuracy of calling everything background", "background accuracy",
         "{:.3f}"),
        ("Number of UCSC islands", "true islands", "{}"),
        ("UCSC islands overlapped by an HMM island", "true islands found", "{}"),
        ("Number of HMM islands", "islands found", "{}"),
        ("HMM islands that overlap a UCSC island", "islands found that are true",
         "{}"),
    ]
    lines = ["| | " + " | ".join(names) + " |",
             "|:--|" + "--:|" * len(names)]
    for label, key, form in rows:
        lines.append(f"| {label} | "
                     + " | ".join(form.format(comparisons[name][key])
                                  for name in names) + " |")
    return "\n".join(lines)


@app.function(hide_code=True)
def gene_starts(features):
    """Get the position where each gene starts (its first base, on its strand).

    Returns:
        list[int]: The start position of each gene.
    """
    starts = []
    for feature in features:
        if feature["feature"] == "gene":
            if feature["strand"] == "+":
                starts.append(feature["start"])
            else:
                starts.append(feature["end"] - 1)
    return starts


@app.cell
def _(
    chr19_features,
    chr19_sequence,
    island_labels,
    mo,
    plot_paths_works,
    test_labels,
    train_hmm_works,
    viterbi_works,
):
    if viterbi_works and train_hmm_works and plot_paths_works:
        # Train on the first million bases
        _model = train_hmm(chr19_sequence[:TRAINING_END],
                           island_labels[:TRAINING_END], list(BASES),
                           ["Background", "Island"])

        # Find the most probable path for the second million bases
        _path, _ = viterbi(chr19_sequence[TRAINING_END:], _model)
        _path = np.array(_path)
        base_comparison = compare_islands(test_labels, _path)

        # Plot a stretch of 50,000 bases
        _a, _b = WINDOW[0] - TRAINING_END, WINDOW[1] - TRAINING_END
        _figure = plot_paths(test_labels[_a:_b], _path[_a:_b], _model["states"],
                             "UCSC islands", "HMM islands",
                             title = "One base at a time", start = WINDOW[0])
        for _start in gene_starts(chr19_features):
            if WINDOW[0] <= _start < WINDOW[1]:
                _figure.axes[0].axvline(_start, color = "gray", linestyle = "--",
                                        linewidth = 1.5)
        # Show positions with commas (e.g., 1,010,000)
        _figure.axes[0].xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        _output = mo.vstack([
            draw_two_state_diagram(_model, colors = ("gray", "seagreen"),
                                   symbol_label = "Base"),
            _figure,
            mo.md(comparison_table({"One base at a time": base_comparison})),
        ])
    else:
        base_comparison = None
        _output = mo.md("***Waiting — Get your `viterbi`, `plot_paths`, and "
                        + "`train_hmm` functions working first.***")
    _output
    return (base_comparison,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The HMM finds many of the islands, but it isn't great: Its accuracy is about
    the same as calling **every** base background!
    Look at its emission probabilities: The islands are richer in C and G, but
    that's **all** this model can see, because it looks at one base at a time.
    It has no idea whether a C is followed by a G.
    But, what makes a CpG island special is the CpGs!

    ## Looking at pairs of bases

    To let our HMM "see" CpGs, we can make each observed symbol a ***pair*** of
    bases: the base at a position, along with the base before it.
    So, the sequence `ACGTT` becomes the symbols `AC`, `CG`, `GT`, `TT`.
    There are $4 \times 4 = 16$ possible pairs, and we can train our HMM on them
    with your `train_hmm` function, without changing it at all!

    There's one more step: The probability that state $k$ emits the pair `CG`
    should be the probability of a `G` **given** that the base before it was a
    `C`, $P(\texttt{G} \mid \texttt{C})$, because the `C` was already accounted
    for at the previous position.
    The next cell does this by dividing each emission probability by the total
    probability of the pairs that start with the same base.
    This makes each state of our HMM a ***Markov chain*** along the sequence:
    The probability of each base depends on the base before it.

    /// details | Optional: Isn't using pairs of bases cheating?
    Our pairs overlap: The `C` in `CG` is also the second base of the pair before
    it.
    That's why we use $P(\texttt{G} \mid \texttt{C})$ instead of the probability
    of the pair: The probability of the whole sequence is then the probability
    of the first base times $P(x_2 \mid x_1) \, P(x_3 \mid x_2) \cdots$, which
    counts each base exactly once.
    This is the same Markov chain we used for substitution models, but along a
    sequence instead of through time!
    ///

    The third cell below trains the new HMM on the first million bases, finds the
    most probable path for the second million bases, and compares the results to
    our first HMM.
    It also shows the probability of each base, given the base before it, in the
    two states of the trained model.
    This cell also takes 20 to 30 seconds to run.
    **You do not need to edit the next three cells.**
    """)
    return


@app.function
def get_pairs(sequence):
    """Get the overlapping pairs of bases in a sequence.

    Examples:
        >>> get_pairs("ACGTT")
        ['AC', 'CG', 'GT', 'TT']
    """
    return [sequence[i - 1:i + 1] for i in range(1, len(sequence))]


@app.function(hide_code=True)
def draw_pair_probabilities(model):
    """Draw P(base | previous base) for each state of a model of pairs of bases.

    Returns:
        matplotlib.figure.Figure: The figure.
    """
    figure, all_axes = plt.subplots(1, 2, figsize = (10, 4.4))
    for k, axes in enumerate(all_axes):
        probabilities = model["emissions"][k].reshape(4, 4)
        axes.imshow(probabilities, cmap = "Blues", vmin = 0, vmax = 0.5)
        for row in range(4):
            for column in range(4):
                value = probabilities[row, column]
                axes.text(column, row, f"{value:.2f}", ha = "center",
                          va = "center", fontsize = 12,
                          color = "white" if value > 0.3 else "black")
        axes.add_patch(plt.Rectangle((2 - 0.5, 1 - 0.5), 1, 1, fill = False,
                                     edgecolor = "darkorange", linewidth = 3))
        axes.set_xticks(range(4), list(BASES))
        axes.set_yticks(range(4), list(BASES))
        axes.set_xlabel("Base")
        axes.set_ylabel("Previous base")
        axes.set_title(f"{model['states'][k]}: P(base | previous base)")
    figure.tight_layout()
    return figure


@app.cell
def _(
    base_comparison,
    chr19_features,
    chr19_sequence,
    island_labels,
    mo,
    test_labels,
):
    if base_comparison is not None:
        # Train on the pairs in the first million bases
        _pair_symbols = [_a + _b for _a in BASES for _b in BASES]
        _model = train_hmm(get_pairs(chr19_sequence[:TRAINING_END]),
                           island_labels[1:TRAINING_END], _pair_symbols,
                           ["Background", "Island"])
        # Convert each P(pair) into P(base | previous base): Each group of four
        # pairs that start with the same base adds up to 1
        _emissions = _model["emissions"].reshape(2, 4, 4)
        _emissions = _emissions / _emissions.sum(axis = 2, keepdims = True)
        _model["emissions"] = _emissions.reshape(2, 16)

        # Find the most probable path for the second million bases (the first
        # pair ends at the first base of the second million)
        _path, _ = viterbi(get_pairs(chr19_sequence[TRAINING_END - 1:]), _model)
        pair_path = np.array(_path)
        _pair_comparison = compare_islands(test_labels, pair_path)

        # Plot the same stretch of 50,000 bases
        _a, _b = WINDOW[0] - TRAINING_END, WINDOW[1] - TRAINING_END
        _figure = plot_paths(test_labels[_a:_b], pair_path[_a:_b],
                             _model["states"], "UCSC islands", "HMM islands",
                             title = "Pairs of bases", start = WINDOW[0])
        for _start in gene_starts(chr19_features):
            if WINDOW[0] <= _start < WINDOW[1]:
                _figure.axes[0].axvline(_start, color = "gray", linestyle = "--",
                                        linewidth = 1.5)
        # Show positions with commas (e.g., 1,010,000)
        _figure.axes[0].xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        _output = mo.vstack([
            _figure,
            mo.md(comparison_table({"One base at a time": base_comparison,
                                    "Pairs of bases": _pair_comparison})),
            draw_pair_probabilities(_model),
        ])
    else:
        pair_path = None
        _output = mo.md("***Waiting — Get your `viterbi`, `plot_paths`, and "
                        + "`train_hmm` functions working first.***")
    _output
    return (pair_path,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 10: Why use pairs of nucleotides? </font>

    Double-click this cell and answer the questions below.

    1.  **In the heat maps of the HMM of pairs of bases, the probability of a G
        after a C is outlined in orange. How different is it in the two states?
        How does this fit with what you know about CpG depletion?**

        **Answer**:

    2.  **Which HMM did a better job of finding the UCSC islands: the one that
        looks at one base at a time, or the one that looks at pairs of bases?
        Why do you think that is?**

        **Answer**:

    3.  **The "true" islands we compared to were found by UCSC with a set of
        rules, not by an experiment. When our HMM disagrees with UCSC, does that
        mean the HMM is wrong? Why or why not?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Islands and genes

    We said that many CpG islands sit at the start of genes.
    Let's check!
    For each gene in the second million bases, the next cell checks if the HMM of
    pairs of bases found an island within 500 bases of where the gene starts,
    and does the same for the UCSC islands.
    It also checks how often a **random** position is near an island, so we have
    something to compare to.
    **You do not need to edit the next cell.**
    """)
    return


@app.cell
def _(chr19_features, mo, pair_path, test_labels):
    mo.stop(
        pair_path is None,
        mo.md("***Waiting — Get your `viterbi`, `plot_paths`, and `train_hmm` "
              + "functions working first.***"),
    )

    def _near_island(_labels, _position, _distance = 500):
        return bool(_labels[max(0, _position - _distance):_position + _distance].any())

    _starts = [_s - TRAINING_END for _s in gene_starts(chr19_features)
               if _s >= TRAINING_END]
    _rng = np.random.default_rng(19)
    _random_positions = _rng.integers(0, len(test_labels), size = 1000)
    mo.md(
        f"""
    | | Near a UCSC island | Near an HMM island |
    |:--|--:|--:|
    | Gene starts (out of {len(_starts)}) | {sum(_near_island(test_labels, _s) for _s in _starts)} | {sum(_near_island(pair_path, _s) for _s in _starts)} |
    | Random positions (out of 1,000) | {sum(_near_island(test_labels, int(_s)) for _s in _random_positions)} | {sum(_near_island(pair_path, int(_s)) for _s in _random_positions)} |
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 11: Islands and genes </font>

    Double-click this cell and answer the questions below.

    1.  **How many of the genes start near an island found by our HMM? How does
        this compare to random positions? What does this tell you about using
        an HMM to find genes?**

        **Answer**:

    2.  **Not every gene has a CpG island. For example, the genes for the β-globin
        proteins in our red blood cells, which are only turned on in the cells
        that make red blood cells, have none. Also, a CpG island tells us roughly
        where a gene starts, but not where its exons and introns are. What other
        hidden states would an HMM need to find the whole structure of a gene?
        What clues in the DNA might it use?**

        **Answer**:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    -   A **hidden Markov model** has hidden **states** that follow a Markov chain
        (with **transition probabilities**), and each state **emits** a symbol we
        can see (with **emission probabilities**)
    -   The probability of the observations **and** a path of hidden states is a
        product of start, transition, and emission probabilities; we work with its
        **log** to avoid underflow
    -   There are far too many paths to try them all, but the **Viterbi
        algorithm** finds the most probable path with **dynamic programming**:
        Fill in a table one column at a time, keeping the best way to reach each
        state, and then **trace back**
    -   How well we can recover hidden states depends on how **different** the
        emission probabilities of the states are
    -   When we know the hidden states for some data sets, we can **train** an HMM
        by **counting** transitions and emissions; **pseudocounts** keep any
        probability from being 0
    -   We should **test** a model on data it wasn't trained on
    -   The same code that caught a cheating casino can find **CpG islands**,
        which mark the start of many genes, especially when each state is a Markov
        chain that can "see" **pairs** of bases

    Real gene finders, like GENSCAN and AUGUSTUS, are HMMs with hidden states for
    each part of a gene, and the most important clues they use are the
    ***splice sites*** at the edges of introns.
    But GT and AG are everywhere in a genome, so what makes a real splice site?
    That's the question for our next exercise, where we'll use machine learning
    to find out!
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

    The occasionally dishonest casino and the CpG island HMM are classic
    examples from Durbin, R., S. R. Eddy, A. Krogh, and G. Mitchison (1998),
    *Biological Sequence Analysis: Probabilistic Models of Proteins and Nucleic
    Acids*, Cambridge University Press.
    Part 3 was inspired by the HMM
    [Jupyter notebook](https://github.com/fayjustin/computational_biology/blob/main/Labs/Lab08.ipynb)
    written by [Justin Fay](https://fayjustin.github.io/).
    The Viterbi algorithm is from Viterbi (1967), *IEEE Transactions on
    Information Theory* 13:260–269.
    The DNA sequence (chr19:1,000,001–3,000,000 of the GRCh38 human genome
    assembly) and its CpG islands are from the UCSC Genome Browser (Kent *et
    al.*, 2002, *Genome Research* 12:996–1006), whose CpG islands follow the
    rules of Gardiner-Garden and Frommer (1987), *Journal of Molecular Biology*
    196:261–282.
    The genes are the MANE Select transcripts (Morales *et al.*, 2022, *Nature*
    604:310–315).
    I used Anthropic's Claude (Opus 5.5 model) to help draft this notebook.
    """)
    return


if __name__ == "__main__":
    app.run()
