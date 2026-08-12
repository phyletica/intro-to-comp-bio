# Class website

This directory contains the source files for the class website, which is built
via quarto.

## Create and activate conda env

To build the website, first create the conda environment that contains quarto:

    micromamba env create --file docs-env.yml --name cb-web

Then, activate the conda env:

    micromamba activate cb-web

## Building and publishing the class website

The source content for the documentation is in the `.qmd` markdown-formatted
files in this directory.
To build the html documentation from these source files, you can use the
following quarto command from inside this directory:

    quarto render --to html

We don't technically need `--to html` because currently, no other format gets
rendered.
But keeping it in case in the future we compile any docs to other formats
we don't want included in the html for the website.

After running this command, the generated HTML files will be in the `_site`
directory.
To publish the HTML documentation in the `_site` directory to GitHub Pages
(via the gh-pages branch of the repo), use the following command from inside
this directory:

    quarto publish gh-pages --no-render
