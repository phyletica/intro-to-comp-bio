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
    # Introduction to Python & marimo notebooks

    This notebook is a hands-on introduction to two things at once:

    1. **The Python programming language**: The basics you'll need for the rest of the course.
    2. **marimo notebooks**: The primary tool we'll use to write and run Python code.

    There's no need to memorize anything today; the goal is to get comfortable
    clicking around and running code. We'll use these same ideas over and over
    throughout the semester.

    ## How to use this notebook

    Click on a cell, then press `Shift + Enter` to run it and move to the next one.
    You can also click the run icon near the top-right of a cell when your
    cursor is hovering over it.
    Feel free to edit any cell and re-run it to see what changes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Two kinds of cells

    A marimo notebook is built out of **cells**, and there are two kinds you'll see today:

    - **Python cells**: Contain Python code that gets executed.
    - **Markdown cells**: Contain formatted text, like the one you're reading right now.
      They're used for explanations, notes, and instructions, not for running code.

    You're reading a markdown cell right now. Under the hood, it's actually just a Python
    cell that calls a function called `mo.md(...)` with some text inside it.
    Marimo renders that text as formatted markdown instead of showing it as code.
    If you double-click this cell, marimo will reveal the plain text with
    Markdown syntax.

    **A quick note about SQL cells:** molab also supports a third cell type for SQL
    queries. We're going to ignore those for now and focus on Python and Markdown
    cells.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A crash course in Markdown

    Markdown is a simple way to format text using plain characters.
    For the next cell below,
    I've "told" marimo to show both the plain "raw" text with Markdown syntax,
    and the formatted HTML text that gets created from this plain text.
    Compare the plain text at the top of the next cell to the "pretty"
    HTML text it encodes at the bottom of the cell.
    **This will show you the basics of Markdown syntax.**

    **Pro tip**: You can tell marimo to show the plain text for any cell by
    clicking the icon with three dots near the top-right of the cell your
    cursor is over, and then clicking "Show code". You can also use the
    `Ctrl + H` keyboard shortcut.
    """)
    return


@app.cell(hide_code=False)
def _(mo):
    mo.md(r"""
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

    You can use single backticks for code statements, like `print(x)` in a line
    of regular text.

    To create a block of code (multiple lines of code), use three backticks
    before and after the code:

    ```
    x = "Python is great!"
    print(x)
    ```

    **NOTE**: This is how you display code in a Markdown cell, not how you
    write code you want to run. We'll see how to do that in just a bit.
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
    Notice, the output of the the Python code in the cell appears under the cell when
    it is run.

    ## Variables

    A **variable** is just a name that points to a piece of data. In Python, you create
    one with the `=` symbol. Let's store some (made-up) information about a gene.
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
    output when you run it.
    This is a marimo/Python notebook convention: the value of the last expression in
    a cell gets shown, similar to Jupyter.

    ### An important marimo rule

    One thing that trips people up coming from other notebook tools: **In marimo, a
    variable name can only be defined in one cell in the whole notebook.**
    If you try to reassign a name like `gene_name` in a different cell, marimo will
    show an error instead of letting you overwrite it.
    This is different from Jupyter, where you can reassign the same variable name
    anywhere.

    This is a deliberate design choice. It keeps the notebook's logic consistent no
    matter what order you run cells in, which will make more sense as we go. For now,
    just remember: **Give each new variable a distinct name**.
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

    Python supports the usual math operators: `+`, `-`, `*`, `/`.
    Let's use them to compute the **GC content** of our sequence — the
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

    - `dna_sequence.count("G")`: Strings have built-in **methods** (functions attached to
      them) — `.count()` counts how many times a character appears.
    - `len(dna_sequence)`: The built-in `len()` function gives the length of a string
      (or other collection types like lists).
    - `/` performs division, giving us a decimel number (a proportion in this case).

    ## Strings and f-strings

    We already saw a string above (`dna_sequence`). One extremely useful trick is the
    **f-string**, which lets you drop values of variables directly into a string by putting an `f`
    before the quotes and wrapping variable names in `{ }`.
    Checkout the f-string in the next cell as an example.
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
    The `:.2f` inside the curly braces just tells Python to round to 2 decimal
    places.
    You'll see this formatting trick a lot when reporting numeric results.

    ## Lists

    A **list** holds multiple values in order, written with square brackets `[ ]`.
    Lists are everywhere in computational biology.
    In the next cell we create a list of genes.
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
    Let's add one more gene to our list, using the `.append()` method that all
    lists have.
    """)
    return


@app.cell
def _(gene_list):
    gene_list.append("NADH")
    gene_list
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You can access items in a list by their **index**. Python counts starting at
    `0`, not `1`, so the first item in a list has an index of zero.
    This trips up almost everyone at first, so don't worry if it feels strange.
    """)
    return


@app.cell
def _(gene_list):
    first_gene = gene_list[0]
    third_gene = gene_list[2]
    number_of_genes = len(gene_list)

    print("The first gene is", first_gene)
    print("The third gene is", third_gene)
    print("The number of genes is", number_of_genes)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Learning the lingo**: In other coding languages, a list might be called
    an array or vector.

    ## Lists and strings are both sequences

    Lists and strings are both part of a larger class of Python types called
    sequence types.
    This means they both share attributes and behaviors, like indexing.
    Below, we represent the same sequence as a string and a list and see how
    indexing is the same for both data types.
    """)
    return


@app.cell
def _():
    seq_str = "AGTATTC"
    seq_list = ["A", "G", "T", "A", "T", "T", "C"]
    print(seq_str[1])
    print(seq_list[1])
    print(seq_str[-1])
    print(seq_list[-1])
    return seq_list, seq_str


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    What is the negative one (`-1`) index doing above?

    Negative numbers start at the end of the list (or string) and count
    backward!
    So, you can always use the index `-1` to access the last item in a list or
    string. `-2` will be the second to last item, etc.

    ## Slicing
    ***Slicing*** a list or string (or any sequence type) in Python is similar to
    indexing, but allows you to extract a specific portion of the items in
    the sequence.
    Let's try slicing our `seq_str` and `seq_list`:
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
    Notice, the resulting slice goes from the item indexed by the number left of the
    colon (`:`) up to, but not including, the index on the right of the colon.
    Let's look at a diagram of the `seq_list[1:4]` example above:

        Included in slice:        *    *    *
        Index:               0    1    2    3    4    5    6
        Item:              ["A", "G", "T", "A", "T", "T", "C"]

    The slice included Index 1, up to, but not including, Index 4.

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
    cytb_seq = gene_dict["CYTB"] # We use the key to get the value, not an index!
    coi_seq = gene_dict["COI"]
    number_of_genes_in_dict = len(gene_dict)

    print("The sequence for CYTB is", cytb_seq)
    print("The sequence for COI is", coi_seq)
    print("The number of genes is", number_of_genes_in_dict)
    return(gene_dict,)



@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice, above, instead of using a number (index) to access items,
    we use the key the item is paired with.
    We can also use the `len` function with dictionaries; it returns the number of
    entries (key-value pairs).

    Let's add one more gene to our dictionary.
    """)
    return


@app.cell
def _(gene_dict):
    gene_dict["ND4"] = "GGCCTTAAAT" # Adding a key-value pair to an existing dict
    gene_dict


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Learning the lingo**: In other coding languages, a dictionary might be
    called a map, hash, hashmap, or an associative array.

    ## Loops

    A `for` loop lets you repeat an action for every item in a list (or other
    collection type).
    For example, instead of writing the same line of code five times for five genes,
    you write it once:
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
    Notice the **indentation** (four spaces) before `print`.
    Python uses indentation to know what's "inside" the loop.
    This is different from many other languages that use curly braces `{ }` instead.
    Getting the indentation right matters a lot in Python!
    Most modern text editors (including marimo notebooks) will create the
    correct indents for you.

    ## Conditionals

    `if` / `elif` / `else` statements let your code make decisions.
    Let's classify our GC content from earlier.
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

    A **function** packages up a block of code so you can reuse the code without
    retyping it.
    You've already been using functions like `len()` and `print()`.
    Now, let's write our own, generalizing the GC content calculation from before so
    it works on *any* sequence, not just `dna_sequence`.
    """)
    return


@app.function
def gc_content_of(sequence):
    g = sequence.count("G")
    c = sequence.count("C")
    return (g + c) / len(sequence)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, let's use our new function to calculate the GC content of any sequence.
    """)
    return


@app.cell
def _():
    gc_content_of("ATGCGTACGTTAGC")
    return


@app.cell
def _():
    gc_content_of("GGCCGGCC")
    return


@app.cell
def _():
    gc_content_of("ATATATAT")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Defining `gc_content_of` once means we can now reuse it on as many sequences as we
    want, as shown above, without copy-pasting the calculation each time. This kind of
    reuse is a big part of why we write code instead of doing calculations by hand.

    ## File IO (Input/Output)

    Of course, we usually can't type sequences "by hand," like we've been doing
    in our toy examples.
    We want to read real sequences (or other data) from a file.
    FASTA-formatted files are a common convention in Computational Biology and
    Bioinformatics and are used for storing named sequences of nucleotides.

    The hallmark of the FASTA format is that it contains two types of lines:

    1. Lines with the identifier (name) of a sequence; these lines always begin with
       the `>` symbol.
    2. Lines containing nucleotide sequence.

    A sequence identifier line must only take up one line, and so is separated from
    nucleotide sequence by the newline character (`\n`).

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
    # Open the file with a `with` statement to ensure it gets closed
    with open(file_name, "r") as in_stream:
        # Loop over each line of the file
        for line in in_stream:
            line = line.strip() # Remove any empty spaces from the ends of the line
            if not line:
                continue  # Line is empty, skip it!
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
    from a FASTA-formatted file called "SARS-CoV-2-short.fasta".
    It contains sequences of several strains of the SARS-CoV-2 virus.
    Below, we use a for-loop to print the first 10 bases of each viral
    sequence.
    """)
    return


@app.cell
def _(local_files):
    local_files # Ignore this line, it's just my molab trick to ensure the fasta file is present
    sars_file_name = "SARS-CoV-2-short.fasta"
    sars_sequences = parse_fasta_file(sars_file_name)
    print("Number of SARS-CoV-2 sequences:", len(sars_sequences))
    # Loop over all the keys in the dict of sequences
    for seq_name in sars_sequences:
        # The first square brackets get the sequence from the dict
        # The second square brackets get the first 50 bases from the sequence
        first_50_bases = sars_sequences[seq_name][:50]
        print(f"Sequence {seq_name} starts with: {first_50_bases}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We will use the data in the `sars_sequences` dictionary in the exercise below.

    ## Why marimo? A quick reactivity demo

    One feature that makes marimo different from a typical notebook: When a variable
    changes, **every cell that depends on it re-runs automatically**.
    You never need to remember to manually re-run downstream cells.
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
    No `Shift + Enter` needed for that last cell; it updated by itself.
    This "reactive" behavior sets marimo apart from tools like Jupyter, and it's
    especially handy for building interactive tools to explore your data.

    Another feature that makes marimo unique is that each notebook is pure Python.
    Other types of notebooks embed the Python code inside another data
    structure, which makes it impossible to read when you peak under the hood.

    ## Your turn: Exercise what you've learned

    You can work with your classmates on these questions, but please do your own work.
    Edit the empty cells below and run them with `Shift + Enter` (or the run/play icon).
    Remember the marimo rule from earlier: Give any new variable you create a name that
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
    the `"Omicron"` sequence from the 227th base to the 239th base.
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

    Write a function that will print any section of a given sequence.
    I've started a function called `print_sequence_section`
    that takes three arguments: the sequence, and the start and stop index
    associated with the section to be printed.
    See if you can complete the function and get it working.
    """)
    return


@app.function
def print_sequence_section(sequence, start_index, stop_index):
    # replace the line below with your Challenge 5 code
    print("Not working yet!")


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
    print_sequence_section(test_seq, 1, 4)
    print_sequence_section(test_seq, 8, -1)
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
    - **File IO**

    This is most of the core Python you'll need to get started.
    Everything else this semester builds on these same pieces.
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
        "SARS-CoV-2-short.fasta",
    ]
    local_files = [setup_local_file(f) for f in file_names]
    return (local_files,)


if __name__ == "__main__":
    app.run()
