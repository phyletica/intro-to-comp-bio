# /// script
# dependencies = ["marimo"]
# requires-python = ">=3.14"
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
    # Welcome to Computational Biology: Python & marimo Basics

    This notebook is a hands-on introduction to two things at once:

    1. **The Python programming language** — the basics you'll need for the rest of the course.
    2. **marimo notebooks** — the tool we'll use to write and run Python code.

    You should be able to work through this in about 45–60 minutes. There's no need to
    memorize anything today — the goal is just to get comfortable clicking around and
    running code. We'll use these same ideas over and over throughout the semester.

    **How to use this notebook:** click on a cell, then press `Shift + Enter` to run it
    and move to the next one. Feel free to edit any cell and re-run it to see what changes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Two kinds of cells

    A marimo notebook is built out of **cells**, and there are two kinds you'll see today:

    - **Python cells** — contain Python code that gets executed.
    - **Markdown cells** — contain formatted text, like the one you're reading right now.
      They're used for explanations, notes, and instructions, not for running code.

    You're reading a markdown cell right now. Under the hood, it's actually just a Python
    cell that calls a function called `mo.md(...)` with some text inside it — marimo
    renders that text as formatted markdown instead of showing it as code. In molab, you
    can also switch a cell into "markdown mode" from the cell menu, which hides the
    `mo.md(...)` wrapper and lets you type formatted text directly.

    **A quick note about SQL cells:** molab also supports a third cell type for SQL
    queries. We're going to completely ignore those for now — just Python and Markdown
    today.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A crash course in Markdown

    Markdown is a simple way to format text using plain characters.
    To show you the basics of Markdown,
    the next cell is created using the Markdown-formatted text below:

        # A Big Heading

        ## A sub-heading

        ### A sub-sub-heading

        Here is some **bold text** and *italicised text*.

        Maybe you want ***bold italics***?

        Note, this
        sentence gets shown
        on one line!

        It's easy to make bulleted lists

        - Item 1
        - Item 2

        And enumerated lists

        1. Notice
        3. The numbers
        2. Get worked out automatically

        You can use single backticks for statements, like `print(x)` in a line
        of regular text.

        To create a block of code (multiple lines of code), use three backticks
        before and after the code:

        ```
        x = "Python is great!"
        print(x)
        ```

    Using Markdown cells is a great way to explain and document your code
    within a notebook!
    In case you're curious, the entire course website is created with Markdown!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # A Big Heading

    ## A sub-heading

    ### A sub-sub-heading

    Here is some **bold text** and *italicised text*.

    Maybe you want ***bold italics***?

    Note,
    this
    sentence gets
    rendered
    on on line!

    It's easy to make bulleted lists

    - Item 1
    - Item 2

    And enumerated lists

    1. Notice
    3. The numbers
    2. Get worked out automatically

    You can use single backticks for `code` statements in a line of regular
    text.

    You use three backticks to create a block of code:

    ```
    x = "Python is great!"
    print(x)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Markdown cells are useful!

    Using Markdown cells is a great way to explain and document your code
    within a notebook!
    In case you're curious, the entire course website is created with Markdown!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Your first Python cell

    Below is a Python cell. Click it and press `Shift + Enter` to run it.
    """)
    return


@app.cell
def _():
    print("Hello, computational biology!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Variables

    A **variable** is just a name that points to a piece of data. In Python, you create
    one with `=`. Let's store some information about a made-up gene.
    """)
    return


@app.cell
def _():
    # Any text after a '#' is a comment and ignored by Python!
    gene_name = "BRCA1"
    dna_sequence = "ATGCGTACGTTAGC"
    exon_count = 24
    average_expression = 3.72

    gene_name, dna_sequence, exon_count, average_expression
    return average_expression, dna_sequence, exon_count, gene_name


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice that the last line of a cell — just `gene_name, dna_sequence, exon_count,
    average_expression` with no `print()` — is displayed automatically as the cell's
    output. This is a marimo/Python notebook convention: the value of the last expression
    in a cell gets shown, similar to Jupyter.

    ### An important marimo rule

    One thing that trips people up coming from other notebook tools: **in marimo, a
    variable name can only be defined in one cell in the whole notebook.** If you try to
    reuse a name like `gene_name` in a different cell, marimo will show an error instead
    of letting you overwrite it. This is different from Jupyter, where you can reassign
    the same variable name anywhere.

    This is a deliberate design choice — it keeps the notebook's logic consistent no
    matter what order you run cells in, which will make more sense as we go. For now,
    just remember: **give each new variable a distinct name.**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Basic data types

    Every piece of data in Python has a **type**. The four you'll use constantly:

    - `int` — whole numbers, like `24`
    - `float` — decimal numbers, like `3.72`
    - `str` — text ("strings"), like `"ATGCGTACGTTAGC"`
    - `bool` — `True` or `False`

    You can check any value's type with the `type()` function.
    """)
    return


@app.cell
def _(average_expression, dna_sequence, exon_count):
    type(exon_count), type(average_expression), type(dna_sequence)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Doing arithmetic

    Python supports the usual math operators: `+`, `-`, `*`, `/`. Let's use them to
    compute something biologically meaningful: the **GC content** of our sequence — the
    fraction of bases that are G or C, which affects things like DNA stability and melting
    temperature.
    """)
    return


@app.cell
def _(dna_sequence):
    g_count = dna_sequence.count("G")
    c_count = dna_sequence.count("C")
    sequence_length = len(dna_sequence)

    gc_content = (g_count + c_count) / sequence_length
    gc_content
    return (gc_content,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A few new things happened in that cell:

    - `dna_sequence.count("G")` — strings have built-in **methods** (functions attached to
      them) — `.count()` counts how many times a character appears.
    - `len(dna_sequence)` — the built-in `len()` function gives the length of a string
      (or list).
    - `/` performs division, giving us a proportion.

    ## Strings and f-strings

    We already saw a string above (`dna_sequence`). One extremely useful trick is the
    **f-string**, which lets you drop variables directly into text by putting an `f`
    before the quotes and wrapping variable names in `{ }`.
    """)
    return


@app.cell
def _(gc_content, gene_name):
    summary_message = f"The GC content of {gene_name} is {gc_content:.2f}"
    summary_message
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `:.2f` inside the curly braces just tells Python to round to 2 decimal places —
    you'll see this formatting trick a lot when reporting numeric results.

    ## Lists

    A **list** holds multiple values in order, written with square brackets `[ ]`. Lists
    are everywhere in computational biology — a list of gene names, a list of sequences, a
    list of expression values.
    """)
    return


@app.cell
def _():
    gene_list = ["BRCA1", "TP53", "EGFR", "MYC", "PTEN"]
    gene_list
    return (gene_list,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You can access items in a list by their **index**. Python counts starting at `0`, not
    `1` — this trips up almost everyone at first, so don't worry if it feels strange.
    """)
    return


@app.cell
def _(gene_list):
    first_gene = gene_list[0]
    third_gene = gene_list[2]
    number_of_genes = len(gene_list)

    first_gene, third_gene, number_of_genes
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Learning the lingo**: In other coding languages, a list might be called
    an array or vector.

    ## Lists and strings are both sequences

    Lists and strings are both part of larger class of Python types called
    sequence types.
    This means they both share attributes and behaviors, like indexing.
    """)
    return


@app.cell
def _():
    seq_str = "ATTATGC"
    seq_list = ["A", "G", "T", "A", "T", "T", "C"]
    print(seq_str[1])
    print(seq_list[1])
    print(seq_str[-1])
    print(seq_list[-1])
    return seq_list, seq_str


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    What is the negative one index (`-1`) index doing above?

    Negative numbers start at the end of the list (or string) and count
    backward!

    ## Slicing
    ***Slicing*** a list or string (or any sequence type) in Python is similar to
    indexing, but allows you to extract a specific portion of the elements in
    the sequence.
    """)
    return


@app.cell
def _(seq_list, seq_str):
    print(seq_str[1:4])
    print(seq_list[1:4])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dictionaries

    A **dictionary** stores data in key-value pairs, and is written with curly
    brackets `{ }`
    and colons `:` separating the key and value of each pair.
    Dictionaries are super useful for organizing data you need to reference
    later using an identifier (key).
    """)
    return


@app.cell
def _():
    gene_dict = {"CYTB" : "AAGCTTCGA", "ND2" : "TGCCAATGC", "COI" : "GATCCGCA" }
    cytb_seq = gene_dict["CYTB"]
    coi_seq = gene_dict["COI"]
    number_of_genes_in_dict = len(gene_dict)

    cytb_seq, coi_seq, number_of_genes_in_dict
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice, above, instead of using a number (index) to access items,
    we use the key the item is paired with.

    **Learning the lingo**: In other coding languages, a dictionary might be
    called a map, hash, hashmap, or an associative array.

    ## Loops

    A `for` loop lets you repeat an action for every item in a list — instead of writing
    the same line of code five times for five genes, you write it once.
    """)
    return


@app.cell
def _(gene_list):
    for gene in gene_list:
        print(f"Gene: {gene}, name length: {len(gene)}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice the **indentation** (the spaces before `print`) — Python uses indentation to
    know what's "inside" the loop. This is different from many other languages that use
    curly braces `{ }` instead. Getting the indentation right matters a lot in Python!

    ## Conditionals

    `if` / `elif` / `else` statements let your code make decisions. Let's classify our GC
    content from earlier.
    """)
    return


@app.cell
def _(gc_content):
    if gc_content > 0.6:
        gc_category = "GC-rich"
    elif gc_content < 0.4:
        gc_category = "AT-rich"
    else:
        gc_category = "balanced"

    gc_category
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Functions

    A **function** packages up a block of code so you can reuse it without retyping it.
    You've already been using functions like `len()` and `print()` — now let's write our
    own, generalizing the GC content calculation from before so it works on *any*
    sequence, not just `dna_sequence`.
    """)
    return


@app.function
def gc_content_of(sequence):
    g = sequence.count("G")
    c = sequence.count("C")
    return (g + c) / len(sequence)


@app.cell
def _():
    gc_content_of("ATGCGTACGTTAGC"), gc_content_of("GGCCGGCC"), gc_content_of("ATATATAT")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Defining `gc_content_of` once means we can now reuse it on as many sequences as we
    want, as shown above, without copy-pasting the calculation each time. This kind of
    reuse is a big part of why we write code instead of doing calculations by hand.

    ## File IO (Input/Output)

    In many cases one would want to read sequences (or other data) from a file.
    FASTA-formatted files are a common convention in Computational Biology and
    Bioinformatics and are used for storing named sequences of nucleotides.

    The hallmark of the FASTA format is that it contains two types of lines;
    some sequence identifier line that will always begin with the `>` symbol,
    and actual nucleotide sequence.
    The sequence identifier line needs to only take up one line, and so is
    separated from nucleotide sequence by the newline character (`\n`).

    The nucleotide sequence itself consists of the 4 nucleotides, Adenine,
    Thymine, Cytosine and Guanine, indicated by A, T, C and G.

    FASTA files often store very long sequences such as entire chromosomes.
    For this reason, it is syntactically and aesthetically practical for
    FASTA sequences to be interrupted by line breaks.
    A common default is to have sequence break to the next line every
    80 nucleotides.

    FASTA files can also store more than one sequence, with the '>' symbol
    indicating when a new sequence entry is starting and its name.

    Let's define a function for parsing a fasta file and storing the
    data as a dictionary.
    Read through the function and see if you can
    figure out how it works.
    """)
    return


@app.function
def parse_fasta_file(file_name):
    sequences = {}
    current_id = None
    with open(file_name, "r") as in_stream:
        for line in in_stream:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            if line[0] == ">":
                # Extract sequence name (removing the ">" symbol)
                current_id = line[1:]
                # Remove any space between ">" and the name
                current_id = current_id.strip()
                sequences[current_id] = ""
            else:
                # Concatenate this chunk of sequence
                if current_id is not None:
                    sequences[current_id] += line
    return sequences


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's use our new `parse_fasta_file` function to load sequence data
    from a FASTA-formatted file called "SARS-CoV-2.fasta".
    It contains sequences of several strains of the SARS-CoV-2 virus.
    Below, we use a for-loop to print the first 10 bases of each viral
    sequence.
    """)
    return


@app.cell
def _(local_files):
    local_files # Ignore this line, it just ensures the fasta file exists
    sars_file_name = "SARS-CoV-2.fasta"
    sars_sequences = parse_fasta_file(sars_file_name)
    print(f"Number of SARS-CoV-2 sequences: {len(sars_sequences)}")
    # Loop over all the keys the dict of sequences
    for seq_name in sars_sequences:
        # The first square brackets get the sequence from the dict
        # The second square brackets get the first 10 bases from the sequence
        first_10_bases = sars_sequences[seq_name][:10]
        print(f"Sequence {seq_name} starts with: {first_10_bases}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We will use the data in the `sars_sequences` dictionary in an exercise below.

    ## Why marimo? A quick reactivity demo

    Here's the feature that makes marimo different from a typical notebook: when a
    variable changes, **every cell that depends on it re-runs automatically** — you never
    need to remember to manually re-run downstream cells.
    Try running the next 2 cells and then drag the slider below and watch the
    cell underneath it update on its own.
    """)
    return


@app.cell
def _(mo):
    gc_slider = mo.ui.slider(start=0, stop=100, value=50, label="GC content (%)")
    gc_slider
    return (gc_slider,)


@app.cell
def _(gc_slider, mo):
    mo.md(f"""
    You set the GC content to **{gc_slider.value}%**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    No `Shift + Enter` needed for that last cell — it updated by itself. This "reactive"
    behavior is the main thing that sets marimo apart from tools like Jupyter, and it's
    especially handy for building little interactive tools to explore your data.

    ## Your turn: Exercise what you've learned

    You can work with your classmates on these questions, but please do your own work.
    Edit the empty cells below and run them with `Shift + Enter`.
    Remember the marimo rule from earlier — give any new variable you create a name that
    hasn't been used already in this notebook!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### <font color=red> Challenge 1 </font>

    Create a variable called `my_sequence` containing any short DNA
    sequence of your choosing (only the letters A, T, G, and C), then print its length
    using `len()`.
    """)
    return


@app.cell
def _():
    # Write your Challenge 1 code here
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### <font color=red> Challenge 2 </font>

    Use the `gc_content_of` function we defined earlier to compute the GC
    content of your `my_sequence` from Exercise 1.
    """)
    return


@app.cell
def _():
    # Write your Challenge 2 code here
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### <font color=red> Challenge 3 </font>

    Create a list called `my_gene_list` with at least 3 gene names (as
    strings), then write a `for` loop that prints each one.
    """)
    return


@app.cell
def _():
    # Write your Challenge 3 code here
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### <font color=red> Challenge 4 </font>

    Using the `sars_sequences` dictionary we created earlier,
    add code to the cell below to print the part of
    the `"Omicron"` sequence from the 127th base to the 139th base.
    Remember, the first base is stored at index 0 in the list.
    """)
    return


@app.cell
def _():
    # Write your Challenge 4 code here
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### <font color=red> Challenge 5 </font>

    Write a function that will print any section of a sequence
    Using the `sars_sequences` dictionary we created earlier,
    add code to the cell below to print the part of
    the `"Omicron"` sequence from the 127th base to the 139th base.
    Remember, the first base is stored at index 0 in the list.
    """)
    return


@app.function
def print_sequence_section(sequence, start_index, stop_index):
    # Write your Challenge 5 code here
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the cell below to see if your function above is working
    the way you expect.
    """)
    return


@app.cell
def _():
    test_seq = "AAGCCGCCTAAT"
    print(print_sequence_section(test_seq, 1, 4))
    print(print_sequence_section(test_seq, 8, -1))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    You've learned:

    - The difference between **Python cells** and **Markdown cells** in marimo
    - Basic **markdown** formatting
    - **Variables**, and marimo's one-name-per-notebook rule
    - Core **data types**: `int`, `float`, `str`, `bool`, `list`, `dict`
    - **Arithmetic operators**
    - F-strings
    - Flow control: **Loops** and **conditionals**
    - **Functions**
    - marimo's signature feature: **reactivity**

    This is most of the core Python you'll need to get started — everything else
    this semester builds on these same pieces.
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
        "SARS-CoV-2.fasta",
    ]
    local_files = [setup_local_file(f) for f in file_names]
    return (local_files,)


if __name__ == "__main__":
    app.run()
