# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.0",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Finding sequences

    **BIOL 5/6800 — Introduction to Computational Biology**

    ### <font color=red> Add your name </font>

    Double-click this cell and add your name below.

    **Name**: Your name here
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## String search

    For this exercise, we will use different data structures and search methods
    to locate a shorter DNA sequence (***substring***) within a longer one
    (***string***).

    In bioinformatics,
    the term **$k$-mer** is used to refer to a short substring of $k$ nucleotides
    found inside a longer genetic sequence.
    For example, a 19-mer could be any sequence of 19 nucleotides found inside a
    longer DNA sequence.
    **Note**: You will sometimes see $k$-mers called ***words***.

    Today, we will use strings, dictionaries, and a suffix array to represent DNA
    sequences.
    The type of data structure and algorithm to apply to a problem often depends on
    whether you are looking for a substring of fixed or variable length.

    Before we embark on our string searching adventure, let's add a few more tools
    to our growing Python toolbox.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Learning more Python

    ### Operations

    Python uses the arithmetic operators just like a calculator.
    However, a couple of the operators are not found on a calculator and some of the
    familiar ones have multiple purposes.

    In the examples below, pay attention to the difference between `/` and `//`.
    Division with `/` always gives a **float**, even when it comes out even.
    Floor division with `//` divides and throws away the remainder, giving an
    **int**.
    We will use `//` later to find the middle of a list, where asking for "position
    4.5" would not make sense.
    """)
    return


@app.cell
def _():
    # `+`, `-`, and `*` behave the way you would expect
    print(7 + 3)
    print(7 - 3)
    print(7 * 3)

    # `/` is division, and ALWAYS gives a float
    print()
    print(7 / 3)
    print(6 / 3)

    # `//` is floor division: divide, then throw away the remainder
    print()
    print(7 // 3)

    # `**` is exponentiation ("7 raised to the power of 3")
    print()
    print(7**3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `+` and `*` also work on **sequences** such as strings and lists:

    - `+` joins two sequences together (***concatenation***)
    - `*` repeats a sequence

    /// warning
    Generally, `+` needs both sides to be the same type (*e.g.*, a string or int).
    If you try `"ATG" + 3`, it will raise a
    `TypeError`, because Python will not try to guess what you are trying to do.
    ///
    """)
    return


@app.cell
def _():
    # `+` glues two strings together
    left_half = "GAATT"
    right_half = "CATG"
    print(left_half + right_half)

    # `*` repeats a string
    print("AT" * 6)

    # Both operators work on lists, too
    print([0, 1] + [2, 3])
    print(["A", "T"] * 3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Operation shortcut for updating a variable

    We often want to change a variable based on its current value, such as adding
    one to a counter variable.
    Writing `count = count + 1` works, but `count += 1` is a shortcut that does
    exactly the same thing.
    Every operator above has a matching shortcut (`-=`, `*=`, `/=`, `//=`, `**=`).
    """)
    return


@app.cell
def _():
    gc_count = 0
    gc_count = gc_count + 1  # the long way
    gc_count += 1  # the shortcut; it does exactly the same thing
    print(gc_count)

    # `+=` works on strings and lists as well
    repeat_unit = "CAG"
    repeat_unit += "CAG"
    print(repeat_unit)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Tuples

    A ***tuple*** holds an ordered collection of items, just like a list, and you
    index and slice it the same way.
    There are two important differences between tuples and lists:

    1.  A tuple is written with parentheses `("TTCAG", 5)` instead of square
        brackets `["TTCAG", 5]`.
    2.  A tuple is ***immutable***. Once you create it, you cannot change it.

    "Mutable" just means "changeable." Lists and dictionaries are mutable, so you
    can add, remove, and replace items after creating them.
    Tuples, strings, and numbers are immutable, so to "change" one you actually need
    to create a new one.

    Tuples are very useful for groups of values that belong together, should travel
    as a unit, and shouldn't be changed.
    """)
    return


@app.cell
def _():
    # A list uses square brackets and CAN be changed
    suffix_list = ["TTCAG", 5]
    suffix_list[1] = 500 # Change 5 to 500
    print(suffix_list)

    # A tuple uses parentheses and CANNOT be changed
    suffix_tuple = ("TTCAG", 5)
    print(suffix_tuple)
    print(suffix_tuple[0])
    print(len(suffix_tuple))

    # Trying to change it is an error. The `try`/`except` below catches that error
    # and prints it, so it doesn't stop the notebook. You won't need to write
    # `try`/`except` yourself today.
    try:
        suffix_tuple[1] = 500 # Trying to change 5 raises an error!
    except TypeError as _tuple_error:
        print("Python said:", _tuple_error)
    return suffix_list, suffix_tuple


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// tip
    It's very easy to create a tuple from a list and vice versa using the `list()`
    and `tuple()` functions.
    ///
    """)
    return


@app.cell
def _(suffix_list, suffix_tuple):
    print(list(suffix_tuple))
    print(tuple(suffix_list))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Unpacking sequences

    In Python, we can ***unpack*** sequences, like lists, tuples, and strings.
    Unpacking is assigning items to separate variables in one step.
    One example where this can be handy is when we need to do a `for` loop over a
    list of tuples.
    """)
    return


@app.cell
def _(suffix_tuple):
    # Unpack the two items into two variables at once
    suffix, position = suffix_tuple
    print(suffix)
    print(position)

    # Unpacking in a `for` loop over a list of tuples
    suffix_table = [("AG", 8), ("CAG", 7), ("TCAG", 6)]
    for one_suffix, one_position in suffix_table:
        print(one_position, one_suffix)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Sorting lists

    Python gives us two ways to sort a list:

    -   `sorted(my_list)` returns a **brand new** sorted list and leaves the
        original alone.
    -   `my_list.sort()` sorts the list **in place**, changing the original, and
        returns `None`.

    A very common mistake is writing `my_list = my_list.sort()`, which throws the
    list away and leaves you with `my_list` set to `None`.

    Sorting a list of **tuples** sorts by the first item in each tuple, using the
    second item only to break ties.
    We will use this behavior below when we learn about suffix arrays.
    Make sure the last line of output in the next cell makes sense.
    """)
    return


@app.cell
def _():
    kmers = ["TTC", "ATC", "GTT", "CAT"]
    # `sorted()` returns a NEW sorted list and leaves the original alone
    print(sorted(kmers))
    print(kmers) # kmers has NOT changed

    same_kmers = ["TTC", "ATC", "GTT", "CAT"]
    # `.sort()` sorts in place and returns None
    print(same_kmers.sort()) # .sort() doesn't return anything!
    print(same_kmers) # same_kmers HAS changed

    # Sorting tuples sorts by the first item in each tuple
    suffix_pairs = [("TCAG", 6), ("AG", 8), ("CAG", 7)]
    suffix_pairs.sort()
    print(suffix_pairs)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Better docstrings

    Compared to our previous notebook, the functions below have *much* more detailed
    docstrings.
    Below, we demonstrate **best practices** for writing docstrings for functions.
    These docstrings can be very helpful when someone needs to use
    Python's `help()` function to remember/learn how to use the function.

    /// tip
    Drafting docstrings is one thing that AI agents tend to be very good at!
    You will still need to read and edit them, but they will get all the
    syntax and formatting in place for you.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Linear string search

    Perhaps the simplest search algorithm is the linear search.
    You move through every position (index) of a sequence, from the first toward the
    last, and check if there is a match to a substring of interest.
    You can think of this as a sliding window of substring comparisons.
    For example, given the string "CGATGCATGC" and substring "ATG",
    we check for "ATG" at every position in the longer sequence:

        CGATGCATGC
        CGA
         GAT
          ATG <- Match!
           TGC
            GCA
             CAT
              ATG <- Match!
               TGC

    Now, let's write some code to do this!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 1: Linear search </font>

    In the Python cell below, write a function that takes a sequence and subsequence
    as input and returns a list of the position(s) where the subsequence is present
    as a substring of the sequence.
    If the subsequence is not present at all in the sequence, the function should
    return an empty list.

    The positions should be zero-based; 0 is the first position, 1 is the second,
    etc.
    For example, the output using the example in the cell above should be `[2, 6]`.

    I've started the function `linear_search` below for you.
    You need to replace the `pass` statement in the `for` loop below with your own
    code to get the function working.
    Two cells down is a Python cell that tests if your function is working.
    You don't need to edit the test cell, just run it to see if your `linear_search`
    function is working.

    /// note
    The docstring below follows best practices and is much more detailed than our
    docstrings in prevous notebooks.
    ///
    """)
    return


@app.function
def linear_search(sequence, subsequence):
    """Find every position where `subsequence` occurs in `sequence`.

    Slides a window the same length as `subsequence` along `sequence`, and
    compares the window to `subsequence` at every position.

    Args:
        sequence (str): The sequence to search.
        subsequence (str): The shorter sequence to search for.

    Returns:
        list[int]: The zero-based positions where a match starts, in increasing
            order. The list is empty if there are no matches.

    Raises:
        AssertionError: If `subsequence` is longer than `sequence`.

    Examples:
        >>> linear_search("CGATGCATGC", "ATG")
        [2, 6]
        >>> linear_search("CGATGCATGC", "GGG")
        []
    """
    # Ensure sequence is not shorter than subsequence
    assert len(sequence) >= len(subsequence)
    # Create an empty list to store matches when we find them
    match_positions = []
    stop_index = len(sequence)
    # Loop over every position in the `sequence`
    for index in range(0, stop_index):
        # Below, delete `pass` and add an `if` statement that uses slicing to
        # check if the current position of `sequence` matches `subsequence`.
        # If there is a match, use the `.append()` list method to add the
        # current index to `match_positions`
        pass
    return match_positions


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function above. **Note**: you do not need to edit the
    code in the cell below.

    Once your function above is working correctly, the output of the test code below
    should be "Yay, your function passed the test!"
    """)
    return


@app.cell
def _():
    test_seq = "CGATGCATGC"
    test_subseq = "ATG"
    test_positions = linear_search(test_seq, test_subseq)
    expected_positions = [2, 6]

    if test_positions != expected_positions:
        _message = f"""Sorry, your linear_search function should have returned
    {expected_positions}, but it returned {test_positions}. Please try again!"""
    else:
        _message = "Yay, your function passed the test!"

    print(_message)
    return expected_positions, test_seq, test_subseq


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### <font color=red> Stretch goal </font>

    If you got `linear_search` to work, congratulations!

    If you look at the `stop_index` variable inside the function and the `for` loop
    that follows it, you might notice that the function (algorithm) could be more
    efficient.
    Currently, we are checking for matches toward the end of `sequence` that are
    shorter than (and thus can't match) `subsequence`.
    For example, in the test example above, when `index = 8`, we check if the `GC`
    at the end of `sequence` matches `ATG`.
    That's a waste! `TGC` at the end of `sequence` should be our last check for a
    match.

    Try editing the line that defines `stop_index` in your `linear_search` function
    above to make the function more efficient, by avoiding the checks toward the end
    of `sequence` that are shorter than `subsequence`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## $k$-mer dictionary

    Our `linear_search` above needs to iterate over every position of every sequence
    we want to search.
    That starts to take a lot of time if we need to search a huge database of
    sequences.

    Using a data structure called a $k$-mer dictionary is an alternative approach
    that uses memory to save time.
    To get an understanding of what a $k$-mer dictionary is and how it works, let's
    look at an example.
    A 3-mer dictionary of the sequence "ATCGTTCATCG" would have keys for all
    3-nucleotide subsequences found in the sequence, and the value of each is a list
    of the positions (indexes) where the subsequence occurs in the sequence:

        Index:    0 1 2 3 4 5 6 7 8 9 10
        Sequence: A T C G T T C A T C G
        3-mer dict: {
            "ATC" : [0, 7],
            "CAT" : [6],
            "CGT" : [2],
            "GTT" : [3],
            "TCA" : [5],
            "TCG" : [1, 8],
            "TTC" : [4],
        }

    **Note**: The order of the keys (3-mers) is not important.

    There's an initial cost of time and memory to create the dictionary of $k$-mer
    positions, but once it's created, a $k$-mer's position(s) can be looked up nearly
    instantaneously; the time complexity is constant ($O(1)$).

    There are two main disadvantages to using a dictionary of $k$-mer positions.

    1.  It costs memory.
        Some implementations reserve a slot for *every possible* $k$-mer, and that
        grows exponentially with $k$.
        For example, for DNA there are $4^k$ possible $k$-mers, which is roughly
        $1.1 \times 10^{12}$ for a 20-mer ($k = 20$).
        A Python dictionary is thriftier than that, because it only stores the
        $k$-mers that actually occur, so it can never hold more entries than the
        sequence is long.
        Even so, it has to store a key and a position for nearly every position in
        the sequence, so expect it to take up several times more memory than the
        sequence itself.
    2.  Once the $k$-mer dictionary is made, the $k$-mer length is fixed.
        If you need to search for a subsequence longer than $k$, you need to use
        **$k$-mer expansion**.
        For example, if we needed to search for the subsequence (5-mer) "ATCAG"
        using our 3-mer dictionary above, we would need to check all the occurrences
        of the 3-mer "ATC" to see if they end with "AG", using something like our
        linear search from above.

    ### Learn the lingo

    What we are calling a $k$-mer dictionary in this exercise goes by a few other
    names,
    including
    $k$-mer index, $k$-mer table, $k$-mer hash table, word index, word table, or
    word hash table.

    ### An example in Python

    In the Python cell below, we create the sequence "ATCGTTCATCG" and an empty
    dictionary called `three_mer_positions`.
    We then use a `for` loop to add all the 3-mers in the sequence as keys, the
    value of each is a list of the zero-based positions the 3-mer occurs in the
    sequence.

    You don't need to edit the code in the next cell, but read it carefully, because
    you are going to use it as a guide in Challenge 2 to define a function that will
    do this for any sequence and $k$.
    """)
    return


@app.cell
def _():
    seq = "ATCGTTCATCG"
    # Create empty dictionary to store our 3-mer dictionary
    three_mer_positions = {}
    # A stop index of 9 ensures the last index we visit in our for loop below is 8,
    # corresponding with the last "T" in our sequence
    stop_index = 9
    for index in range(stop_index):
        three_mer = seq[index : index + 3]
        if three_mer in three_mer_positions:
            # This 3-mer is already in our dictionary, so we just need to add
            # (append) the current index to record another position of this 3-mer
            three_mer_positions[three_mer].append(index)
        else:
            # This 3-mer is NOT in our dictionary yet, so we need to add it and
            # assign it the value of a list containing the current index
            three_mer_positions[three_mer] = [index]

    print(three_mer_positions)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 2: Building a $k$-mer dictionary </font>

    In the Python cell below, write a function that takes a DNA sequence and $k$-mer
    size (integer) as input and returns a dictionary of all the $k$-mers in the
    sequence (keys) with a list of zero-based positions as values.

    Use the example in the Python cell above as a guide.
    Note, one thing to think about is that `stop_index = 9` only works when the
    sequence is 11 nucleotides long and $k$ = 3.
    How can you generalize the `stop_index = 9` line so that it works for sequences
    of any length and any $k$ value?

    /// tip
    Work out how to set `stop_index` on a small example first.
    *E.g.*, the sequence above was 11 nucleotides long, $k$ was 3, and the answer we
    needed wass 9.
    ///
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
    # Add your code here!
    return kmer_positions


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function above. **Note**: you do not need to edit the
    code in the cell below.

    Once your function above is working correctly, the output of the test code below
    should be "Yay, your function passed the test!"
    """)
    return


@app.cell
def _():
    test_seq2 = "ATCGTTCATCG"
    test_dict = get_kmer_dict(test_seq2, 3)
    expected_dict = {
        "ATC": [0, 7],
        "TCG": [1, 8],
        "CGT": [2],
        "GTT": [3],
        "TTC": [4],
        "TCA": [5],
        "CAT": [6],
    }
    if test_dict == expected_dict:
        _message = "Yay, your function passed the test!"
    else:
        _message = f"""Sorry, your get_kmer_dict function should have returned
    {expected_dict}
    but it returned
    {test_dict}
    Please try again!"""

    print(_message)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Searching with a $k$-mer dictionary

    Once you have built the $k$-mer dictionary, finding the position(s) of any
    $k$-length subsequence within the sequence is easy.
    You simply look it up in the dictionary!

    ## <font color=red> Challenge 3: Searching a $k$-mer dictionary </font>

    In the next Python cell below, I've started defining the `kmer_dict_search`
    function for finding all the positions of a subsequence within a sequence.

    Notice that this function does **not** build the $k$-mer dictionary itself.
    Instead, it takes a dictionary that has already been built by `get_kmer_dict`
    as its first argument.
    This is deliberate, and it is the whole point of using a dictionary: we build
    it once, and then search it as many times as we like.

    Currently the function always returns an empty list.
    Replace `return []` below with the code to return the position(s) of
    `subsequence`.
    **Note**: If `subsequence` is not one of the keys in the dictionary, the
    function should still return an empty list.
    """)
    return


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

    Note:
        The list that is returned is the one stored inside `kmer_dict`, not a
        copy of it, so changing the returned list would also change the
        dictionary.

    Examples:
        >>> kmer_dict = get_kmer_dict("ATCGATC", 3)
        >>> kmer_dict_search(kmer_dict, "ATC")
        [0, 4]
        >>> kmer_dict_search(kmer_dict, "GGG")
        []
    """
    return [] # Replace this!


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function above. **Note**: you do not need to edit the
    code in the cell below.

    Once your function above is working correctly, the output of the test code below
    should be "Yay, your function passed the test!"
    """)
    return


@app.cell
def _(expected_positions, test_seq, test_subseq):
    # Re-using test_seq and test_subseq from our test above
    kmer_dict = get_kmer_dict(test_seq, len(test_subseq))
    kmer_test_positions = kmer_dict_search(kmer_dict, test_subseq)

    if kmer_test_positions != expected_positions:
        _message = f"""Sorry, your kmer_dict_search function should have returned
    {expected_positions}
    but it returned
    {kmer_test_positions}
    Please try again!"""
    else:
        _message = "Yay, your function passed the test!"

    print(_message)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Suffix arrays

    Another data structure that can facilitate string searches is a
    [***suffix array***](https://en.wikipedia.org/wiki/Suffix_array).
    Before we define a suffix array, let's first define what a ***suffix*** is.
    Given a string, a suffix is any substring which includes the last letter of the
    string.

    A [suffix array](https://en.wikipedia.org/wiki/Suffix_array)
    is an alphabetically sorted array of all the suffixes of a given string, whose
    values are the starting positions of each suffix in the original string.

    /// note
    Technically, the suffixes are sorted lexicographically, but for the purposes of
    DNA sequences, that is the same as alphabetically.
    ///

    For example, the suffixes of the sequence "ATTCGTTCAG" are:

    | Suffix     | Index |
    |------------|-------|
    | ATTCGTTCAG | 0     |
    | TTCGTTCAG  | 1     |
    | TCGTTCAG   | 2     |
    | CGTTCAG    | 3     |
    | GTTCAG     | 4     |
    | TTCAG      | 5     |
    | TCAG       | 6     |
    | CAG        | 7     |
    | AG         | 8     |
    | G          | 9     |

    To facilitate searching, suffix arrays are sorted lexicographically
    (alphabetically for our purposes):

    | Suffix     | Index |
    |------------|-------|
    | AG         | 8     |
    | ATTCGTTCAG | 0     |
    | CAG        | 7     |
    | CGTTCAG    | 3     |
    | G          | 9     |
    | GTTCAG     | 4     |
    | TCAG       | 6     |
    | TCGTTCAG   | 2     |
    | TTCAG      | 5     |
    | TTCGTTCAG  | 1     |

    ### How is this useful?

    As you can see in the table of the sorted suffix array above,
    it is easy to find all the T's in the sequence, because the last four entries
    show they start at positions 6, 2, 5, and 1.

    Notice that those four entries are **right next to each other**, and that
    sorting guarantees this.
    Nothing that fails to start with "T" could sneak in between them.
    The same holds for any substring we search for, and we will use this fact
    to our advantage below.

    Unlike the $k$-mer dictionary, the suffix array can be used to **find substrings
    of any length**.
    For example, using the suffix array table above, it is very easy to locate the
    substring "TTCAG".
    However, if we built a 3-mer dictionary of the sequence above, we would need to
    use **$k$-mer expansion** to check every occurrence of "TTC" to see if it ends
    with "AG".

    ### Minimizing the cost of a suffix array

    Storing the sorted array of suffixes requires more memory than the length of the
    original string.
    To avoid this memory cost, suffix arrays only store the positions of the
    suffixes in the original string,
    because given the original string and the suffix positions, it is easy to
    extract the suffixes (*e.g.*, using slicing in Python!).

    Let's use some Python code to work with our suffix array from above:
    """)
    return


@app.cell
def _():
    new_seq = "ATTCGTTCAG"
    seq_suffix_array = [8, 0, 7, 3, 9, 4, 6, 2, 5, 1]
    # The entry at index 8 of the suffix array is the number 5, which tells us
    # that the 9th suffix starts at position 5 of the sequence. Slicing from
    # position 5 to the end should therefore give us "TTCAG".
    print(seq_suffix_array[8])
    print(new_seq[seq_suffix_array[8] : ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 4: Building a suffix array </font>

    In the Python cell below, we will write a function that takes a sequence as
    input and returns a sorted suffix array.

    Using the example above, if the function is given "ATTCGTTCAG",
    it should return
    [8, 0, 7, 3, 9, 4, 6, 2, 5, 1].

    I've started the function `get_suffix_array` for you. Currently, the function
    creates a list of each suffix and its position (as a tuple), and then sorts this
    list by the suffixes (alphabetically, because they are strings of letters).

    You need to add a `for` loop that adds only the positions of the sorted suffixes
    to the empty `positions` list.

    Two cells down is a Python cell that tests if your function is working.
    You don't need to edit the test cell, just run it to see if your
    `get_suffix_array` function is working.
    """)
    return


@app.function
def get_suffix_array(sequence):
    """Build the sorted suffix array of a sequence.

    Sorts every suffix of `sequence` alphabetically, then returns the starting
    position of each one. The suffixes themselves are not returned, because any
    suffix can be recovered by slicing `sequence` from its starting position.

    Args:
        sequence (str): The sequence to build the suffix array for.

    Returns:
        list[int]: The zero-based starting position of each suffix, ordered by
            how the suffixes sort alphabetically.

    Examples:
        >>> get_suffix_array("ATTCGTTCAG")
        [8, 0, 7, 3, 9, 4, 6, 2, 5, 1]
    """
    # Create an empty list to store our suffixes
    suffixes = []
    # Loop over every position in the sequence
    for i in range(len(sequence)):
        # Create a tuple of the current suffix and its index
        suffix_index_tuple = (sequence[i:], i)
        # Add the tuple to our suffixes list
        suffixes.append(suffix_index_tuple)

    # Use the `.sort()` method to sort our suffix list. By default it will use
    # the first element in each tuple to sort, which is what we want (we want to
    # sort the list by the suffixes!)
    suffixes.sort()

    positions = []
    # Add a for loop here to add the index of each suffix to the `positions`
    # list

    return positions


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests your function above. **Note**: you do not need to edit the
    code in the cell below.

    Once your function above is working correctly, the output of the test code below
    should be "Yay, your function passed the test!"
    """)
    return


@app.cell
def _():
    test_seq3 = "ATTCGTTCAG"
    test_suffix_array = get_suffix_array(test_seq3)
    expected_suffix_array = [8, 0, 7, 3, 9, 4, 6, 2, 5, 1]

    if test_suffix_array == expected_suffix_array:
        _message = "Yay, your function passed the test!"
    else:
        _message = f"""Sorry, your get_suffix_array function should have returned
    {expected_suffix_array}
    but it returned
    {test_suffix_array}
    Please try again!"""

    print(_message)
    return test_seq3, test_suffix_array


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// note
    Our `get_suffix_array` function is very inefficient when it comes to memory,
    because to sort the suffix array, it temporarily stores all the suffixes of the
    sequence in memory.
    For a sequence of length $n$, our version builds $n$ suffixes of length $n$,
    $n - 1$, $n - 2$, etc., which is about $n^2 / 2$ characters in all.
    This keeps the function relatively simple and easy to understand, which is great
    for learning.
    However, there are tricks to get the sorted suffix array (of only the positions)
    without storing all the suffixes themselves.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How to search using a suffix array?

    Okay, we now know how to create a suffix array for any sequence.
    But, how can we **use** the suffix array to find a subsequence of the original
    sequence?

    We could loop over our suffix array and look for the suffix that matches the
    subsequence for which we are searching.
    However, this would have a time complexity of $O(n)$ where $n$ is the length of
    the original sequence.
    That is not very efficient; we can do better than that.

    When we covered "divide and conquer" algorithms, we introduced the idea of a
    ***binary search***,
    which narrows its search for a target within an array of sorted values by
    throwing away the upper or lower half of the array each iteration.
    More specifically, a binary search finds the position of a target within a
    sorted array repeating the following steps:

    1.  Compare the target to the middle element of the array.
    2.  If the target is greater/less than the middle element, discard the
        left/right half of the array and go back to Step 1

    The binary search stops when the target is found or the array is exhausted.
    Because each step throws away half of what's left, the number of steps grows
    with $\log_2 n$ rather than $n$.
    For a 5,000-nucleotide sequence, that's about 13 comparisons instead of 5,000.

    ### One catch

    A binary search answers "**where is** the target?" and stops as soon as it finds
    *one*. But we want **every** position where our subsequence occurs, and a binary
    search discards half the array at each step, so other matches get thrown away.

    We already highlighted a solution to this issue above.
    In a sorted suffix array, all the suffixes beginning with our target sit in
    **one unbroken block of neighboring rows**.
    So, we can use a suffix array to search for all occurrences of a target
    substring in two stages:

    1.  Use a binary search to find **any one** matching row.
    2.  Walk outward from that row, up and then down, collecting matches until we
        hit a row that doesn't match.

    Stage 1 is fast due to the "divide and conquer" trick of the binary search, and
    Stage 2 only needs to visit the neighboring matches (i.e., we don't need to
    search in Stage 2).

    **Note**: You do not need to edit the next two cells, but read and try to
    understand them.
    """)
    return


@app.function
# This is a "helper" function that we will use in Stage 2 of the main function
# below
def suffix_starts_with(sequence, suffix_start, target_seq):
    """Check whether one suffix of a sequence begins with a target sequence.

    Args:
        sequence (str): The sequence that the suffix comes from.
        suffix_start (int): The zero-based position where the suffix begins.
        target_seq (str): The sequence to look for at the start of the suffix.

    Returns:
        bool: True if the suffix beginning at `suffix_start` starts with
            `target_seq`, and False otherwise.

    Examples:
        >>> suffix_starts_with("ATTCGTTCAG", 5, "TTC")
        True
        >>> suffix_starts_with("ATTCGTTCAG", 6, "TTC")
        False
    """
    slice_stop = suffix_start + len(target_seq)
    return sequence[suffix_start:slice_stop] == target_seq


@app.function
def suffix_binary_search(sequence, suffix_array, target_seq):
    """Find every position of a target sequence using a suffix array.

    Works in two stages. First, a binary search over `suffix_array` finds any
    one row whose suffix starts with `target_seq`. Second, because the suffix
    array is sorted, every remaining match must sit in a neighboring row, so
    the search walks outward from that row until the neighbors stop matching.

    Args:
        sequence (str): The sequence to search.
        suffix_array (list[int]): The sorted suffix array of `sequence`, as
            returned by `get_suffix_array`.
        target_seq (str): The sequence to search for.

    Returns:
        list[int]: The zero-based positions where `target_seq` starts, in
            increasing order. The list is empty if `target_seq` does not occur
            in `sequence`.

    Examples:
        >>> sequence = "ATTCGTTCAG"
        >>> suffix_array = get_suffix_array(sequence)
        >>> suffix_binary_search(sequence, suffix_array, "TC")
        [2, 6]
        >>> suffix_binary_search(sequence, suffix_array, "GGG")
        []
    """
    # first_row/last_row are the limits of our search window; we start with the
    # whole array!
    first_row = 0
    last_row = len(suffix_array) - 1
    # No matching row found yet, so use None as a "nothing found" placeholder
    match_row = None

    # STAGE 1: binary search for ANY ONE row of the suffix array that matches
    while first_row <= last_row:
        # Get the middle row of our search window using floor division
        mid = (first_row + last_row) // 2
        # Slice out the first len(target_seq) letters of that middle suffix
        slice_start = suffix_array[mid]
        slice_stop = slice_start + len(target_seq)
        mid_prefix = sequence[slice_start:slice_stop]
        if mid_prefix == target_seq:
            # We've got a hit! Remember the row and stop looping
            match_row = mid
            break  # this stops the `while` loop
        if mid_prefix < target_seq:
            # Target sorts after the middle suffix, so it can only be in rows
            # below; move the lower limit to one row below the current midpoint
            first_row = mid + 1
        else:
            # Target sorts before the middle suffix, so it can only be above;
            # move the upper limit to one row above the current midpoint
            last_row = mid - 1

    positions = []
    # If match_row is NOT None, we found a match and need to start Stage 2
    if match_row is not None:
        # STAGE 2: the array is sorted, so every other match must be in a row
        # neighboring `match_row`. Start there and walk outward both ways.
        positions = [suffix_array[match_row]]

        # Walk UP until a row doesn't match (or we run off the top of the array)
        row = match_row - 1
        while row >= 0 and suffix_starts_with(
            sequence, suffix_array[row], target_seq
        ):
            positions.append(suffix_array[row])
            row -= 1

        # Now walk DOWN in the same way
        row = match_row + 1
        while row < len(suffix_array) and suffix_starts_with(
            sequence, suffix_array[row], target_seq
        ):
            positions.append(suffix_array[row])
            row += 1

    # Sort the positions before returning them
    return sorted(positions)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below tests the function above. **Note**: you do not need to edit it.
    The tests will fail initially, because
    **you need to get the `get_suffix_array` function working above**.

    Notice that it checks several targets at once, including one that isn't in the
    sequence at all.
    A single passing test is weak evidence that a function is correct; it is
    surprisingly easy to write a buggy search that gets one answer right.
    I did this myself when creating this notebook!! 🙂
    """)
    return


@app.cell
def _(test_seq3, test_suffix_array):
    # We use test_seq3 ("ATTCGTTCAG") and test_suffix_array from the previous test
    # above
    sbs_test_cases = [
        ("TTC", [1, 5]),
        ("TC", [2, 6]),
        ("T", [1, 2, 5, 6]),
        ("A", [0, 8]),
        ("TTCAG", [5]),
        ("GGG", []),
    ]

    sbs_failures = []
    for _target, _expected in sbs_test_cases:
        _found = suffix_binary_search(test_seq3, test_suffix_array, _target)
        if _found != _expected:
            sbs_failures.append(f"  {_target}: expected {_expected}, got {_found}")

    if sbs_failures:
        _message = "Sorry, suffix_binary_search failed these cases:\n" + "\n".join(
            sbs_failures
        )
    else:
        _message = "Yay, your function passed the test!"

    print(_message)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A real-world example

    Let's compare our three algorithms for finding subsequences
    using the genome of the bacteriophage **phiX174**, which is a virus
    that infects *E. coli*.

    The phiX174 genome is about 5,400 nucleotides long and was the first DNA genome
    ever sequenced (Sanger and colleagues, 1977).
    The phiX174 genome is more important than ever, because it is the standard
    "spike-in" control for Illumina sequencing.

    Our target in the phiX174 genome will be **"GAATTC"**, which is the sequence
    recognized by the restriction enzyme *Eco*RI.
    *Eco*RI cuts double-stranded DNA wherever it finds this sequence, so "where does
    GAATTC occur?" is the same question as "where would this enzyme cut the genome?"

    /// note
    "GAATTC" is a ***palindrome*** in the biological sense.
    Its reverse complement is also GAATTC, so a single search of one strand finds
    the cut sites on both.
    ///

    ### Reading a FASTA file

    Genome sequences are often distributed as ***FASTA*** files:

        >NC_001422.1 Escherichia phage phiX174, complete genome
        GAGTTTTATCGCTTCCATGACGCAGAAGTTAACACTTTCGGATATTTCTG
        ATGAGTCGAAAAATTATCTTGATAAAGCAGGAATTACTACTGCTTGTTTA
        ...

    Lines beginning with `>` are description lines, and every other line is
    sequence, split across many lines to make it more readable.
    The function below takes a URL to a FASTA file on the web (*e.g.*, on GenBank),
    downloads the data, and parses it into a dictionary.

    We used a very similar function in our first notebook.
    The main difference with the function below is that it parses the FASTA file
    directly from the web, rather than from a local text file.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below downloads the phiX174 genome from NCBI.
    If the download fails for any reason (no internet, or NCBI is busy), it falls
    back on a randomly generated stand-in sequence so the rest of the notebook
    still runs.
    Check the genome name in the output to see which one you got.
    """)
    return


@app.cell
def _():
    import random

    phix_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        "?db=nuccore&id=NC_001422.1&rettype=fasta&retmode=text"
    )

    try:
        phix_sequence_data = parse_fasta_url(phix_url)
        # Get the first key in the dictionary of sequences (there should only be
        # one)
        genome_name = list(phix_sequence_data.keys())[0]
        genome = phix_sequence_data[genome_name]
    except Exception:
        # Couldn't get the phiX174 data, so make a random sequence to practice
        # on. The seed makes sure everyone gets the same stand-in sequence.
        rng = random.Random(1234)
        genome = "".join(rng.choices("ACGT", k=5386))
        genome_name = "randomly generated stand-in sequence"

    print(f"Loaded genome: {genome_name}")
    print(f"Length: {len(genome)} nucleotides")
    print(f"First 60 nucleotides: {genome[:60]}")
    return (genome,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 5: Timing all three searches </font>

    Now we can compare the three search algorithms we created above by using each to
    find all the occurrences of the *Eco*RI restriction site in the phiX174
    genome.
    We will use `time.perf_counter()`, which returns the current time in seconds.
    Recording the current time before and after some code and subtracting tells us
    how long the code ran.

    The cell below also checks that all three functions return the *same* answer.

    All the code to do the timing and compare the answers is in place below, but you
    need to add the code that uses each algorithm we created above to do the search.
    Where you need to add code is indicated in three places with:

        #######################################################################
        ## YOUR CODE GOES HERE ################################################
        ...
        #######################################################################

    Please read the other code too, to help you learn.
    Read all the comments too, they are there to help you.
    """)
    return


@app.cell
def _():
    # Import the time module for timing the searches
    import time

    # Here is the target we will search for
    # I'm cheating a little by only using the first 5 nucleotides of the EcoRI
    # recognition sequence to make the results a bit more interesting
    ecori_site = "GAATT"

    # The genome you want to search is contained in the `genome` variable we defined
    # in the previous Python cell

    # 1. Linear search
    _start = time.perf_counter()

    # Replace the line below with the code to search `genome` for `ecori_site`
    # using a linear search. Use the `linear_search` function from above!
    ############################################################################
    ## YOUR LINEAR SEARCH CODE GOES HERE #######################################
    linear_positions = [] # Replace this!
    ############################################################################

    linear_run_time = time.perf_counter() - _start

    # 2. Kmer dictionary search
    _start = time.perf_counter()

    # Replace the line below with the code to use a kmer dictionary search of
    # `genome` for `ecori_site`. REMEMBER, using a kmer dictionary search takes 2
    # steps!
    ############################################################################
    ## YOUR K-MER DICT SEARCH CODE GOES HERE ###################################
    kmer_positions = [] # Replace this!
    ############################################################################

    kmer_run_time = time.perf_counter() - _start

    # 3. Binary search of a suffix array
    _start = time.perf_counter()

    # Replace the line below with the code to use a suffix array to search `genome`
    # for `ecori_site`. REMEMBER, using a suffix array search takes 2 steps!
    ############################################################################
    ## YOUR SUFFIX ARRAY SEARCH CODE GOES HERE #################################
    suffix_positions = [] # Replace this!
    ############################################################################

    suffix_run_time = time.perf_counter() - _start

    print(f"linear_search:        {linear_run_time:.4f} seconds")
    print(f"kmer_dict_search:     {kmer_run_time:.4f} seconds")
    print(f"suffix_binary_search: {suffix_run_time:.4f} seconds")
    print()
    print("Do all three agree?", linear_positions == kmer_positions == suffix_positions)
    print(f"Number of {ecori_site} sites found: {len(linear_positions)}")
    print("Positions:", linear_positions)
    return (time,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Why was the linear search fastest?

    You may be surprised that the `linear_search` beat both of our fancy
    data structures, and that `suffix_binary_search` was slowest by a wide margin.

    Both `kmer_dict_search` and `suffix_binary_search` have to **build their data
    structure first**, and building it means walking through the whole genome!
    We paid the full setup cost, then used the result only once.
    This is analogous to alphabetizing a whole library to find one book.

    The point of an $k$-mer index or suffix array is that you build it **once** and
    use it to search **many** times.

    ### Building once and searching many times

    Below we look for the recognition sites of 14 restriction enzymes.
    The linear search starts over for every one, while the $k$-mer dictionary and
    suffix array are each built once and then searched for all 14 restriction
    sites.
    **NOTE**: You don't need to edit the code below.
    """)
    return


@app.cell
def _(genome, time):
    # Again, I'm cheating by only using 5 of the nucleotides of the recognition site
    # for each enzyme
    enzyme_sites = {
        "EcoRI":   "GAATT",
        "BamHI":   "GGATC",
        "HindIII": "AAGCT",
        "PstI":    "CTGCA",
        "SmaI":    "CCCGG",
        "XhoI":    "CTCGA",
        "PciI":    "CATGT",
        "BsrI":    "ACTGG",
        "BglII":   "GATCT",
        "PaqCI":   "CACCT",
        "BtsI":    "CAGTG",
        "BsrBI":   "CCGCT",
        "PspXI":   "TCGAG",
        "PacI":    "TTAAT",
    }

    # Approach 1: a linear search of the genome for every enzyme
    _start = time.perf_counter()

    scan_positions = {}
    for _name, _site in enzyme_sites.items():
        scan_positions[_name] = linear_search(genome, _site)

    scan_seconds = time.perf_counter() - _start

    # Approach 2a: build ONE 5-mer dictionary of the whole genome
    _start = time.perf_counter()
    genome_5mers = get_kmer_dict(genome, 5)
    kmer_build_seconds = time.perf_counter() - _start

    # Approach 2b: Use the 5-mer dictionary to look up each enzyme site
    _start = time.perf_counter()

    kmer_lookup_positions = {}
    for _name, _site in enzyme_sites.items():
        kmer_lookup_positions[_name] = kmer_dict_search(genome_5mers, _site)

    kmer_lookup_seconds = time.perf_counter() - _start

    # Approach 3a: build ONE suffix array of the whole genome
    _start = time.perf_counter()
    genome_sarray = get_suffix_array(genome)
    sarray_build_seconds = time.perf_counter() - _start

    # Approach 3b: Use the suffix array to look up each enzyme site
    _start = time.perf_counter()

    sarray_lookup_positions = {}
    for _name, _site in enzyme_sites.items():
        sarray_lookup_positions[_name] = suffix_binary_search(genome, genome_sarray, _site)

    sarray_lookup_seconds = time.perf_counter() - _start

    print("Cut sites found in the genome:")
    for _name, _site in enzyme_sites.items():
        print(f"  {_name:<8} {_site}  {len(sarray_lookup_positions[_name])} site(s)")

    print()
    print("Do all three approaches agree?",
          scan_positions == kmer_lookup_positions == sarray_lookup_positions,
    )
    print()
    print(f"Building the 5-mer dict:   {kmer_build_seconds:.4f} seconds  (paid once)")
    print(f"Building the suffix array: {sarray_build_seconds:.4f} seconds  (paid once)")
    print(f"14 separate linear scans:  {scan_seconds:.4f} seconds")
    print(f"14 dictionary lookups:     {kmer_lookup_seconds:.6f} seconds")
    print(f"14 suffix array lookups:   {sarray_lookup_seconds:.6f} seconds")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Comparing the results

    Building the $k$-mer dictionary and suffix array costs almost as much as one
    linear search.
    But the lookups afterward are very fast, hundreds of times
    faster than the linear searches.

    If you do enough searches, the initial cost of building a data structure like a
    $k$-mer dictionary or suffix array pays off, and every additional search widens
    the gap.
    This is why tools like BLAST index a database before you ever submit a query.
    The setup cost gets spread across an enormous number of searches.

    ### What about the suffix array?

    The 14 searches of the suffix array are still slower than the 14 $k$-mer
    dictionary lookups.
    So why would we ever want to use a suffix array?

    ## <font color=red> Challenge 6: Why use a suffix array? </font>

    Double-click this cell and write your answer to the question below.

    **When would you use a suffix array over a $k$-mer dictionary?**

    **HINT**: What is (artificially) true about all 14 restriction sites we searched
    for?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## <font color=red> Challenge 7: Choosing an approach </font>

    Double-click this cell and for the three scenarios below, write which of our
    three approaches you would choose and why.

    1.  One sequence, one motif, searched once.

        **Your answer**:

    2.  A reference genome that will not change, and thousands of 20-nucleotide
        sequencing reads to locate within it.

        **Your answer**:

    3.  The same reference genome, but queries varying from 8 to 200 nucleotides,
        with the lengths unknown ahead of time.

        **Your answer**:

    4.  A reference genome that is rebuilt from scratch every night, with a few
        hundred searches run against it during the day.

        **Your answer**:
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

    Sections of this exercise were modified from a
    [Jupyter notebook](https://github.com/fayjustin/computational_biology/blob/main/Labs/Lab03.ipynb)
    written by
    [Justin Fay](https://fayjustin.github.io/).
    I used Anthropic's Claude (Opus 5 model) to proofread and test this notebook.
    I also used it to generate drafts of the doctstrings for the functions.
    """)
    return


if __name__ == "__main__":
    app.run()
