# TPDbCollectionMaker
Python script to quickly make Plex-Meta-Manager poster entries from [ThePosterDatabase](https://theposterdb.com) (TPDb) sets.

Because TPDb doesn't permit automated scraping, this tool reads HTML files.

# How to Use
## Help Menu
This is a Python command-line tool. All arguments are shown with `--help`:

```console
# pipenv run python main.py --help
usage: main.py [-h] --html HTML_FILE [--spaces NUM_SPACES] [--indent NUM_SPACES] [--always-quote]

TPDb Collection Maker

positional arguments:
  HTML_FILE             File with TPDb Collection page HTML to scrape

optional arguments:
  -h, --help            show this help message and exit
  --always-quote        Whether to put all titles in quotes ("")
```

## Installation
1. Install `pipenv`:
```console
# pip3 install pipenv
```
2. Install required packages:
```console
# pipenv install
```
3. Download this tool:
```console
# git clone https://github.com/CollinHeist/TPDbCollectionMaker/
```

## Getting Page HTML
Because TPDb doesn't permit automated scraping, this tool reads HTML files. To get the HTML of a set, right-click the set page and select `Inspect`:

<img src="https://user-images.githubusercontent.com/17693271/168729610-42ac80fc-afb7-40b4-a6bd-39b3f310619c.jpg" width="600"/>

This should launch your browser's HTML inspector. It should look something like:

<img src="https://user-images.githubusercontent.com/17693271/168729837-eacfc4d8-29d3-4968-80f2-17ed164a8884.jpg" width="600"/>

Go to the top-most HTML element (if HTML is selected, use the left-arrow key to collapse all the HTML). The top-most HTML should look like:

```html
<!DOCTYPE html>
<html class="h-100" lang="en"><head>
# Stuff here
</html>
```

Right-click the `<html class="h-100" lang="en"><head>` element, go to `Copy` > `Inner HTML`. Your clipboard now has the coplete HTML of the set page; paste this into some file alongside the `main.py` file of this project. This file will be the input of the [--html](#--html---html-file) argument (see below).

## Arguments
### `html`
Input HTML file to parse.

### `--always-quote`
Whether to quote all titles in the output. If unspecified, only titles with colons are titled.

Below is an example of this argument:

```console
# pipenv run python main.py in.html --always-quote
"Iron Man (2008)":
  url_poster: https://theposterdb.com/api/assets/9773
"The Incredible Hulk (2008)":
  url_poster: https://theposterdb.com/api/assets/9775
"Iron Man 2 (2010)":
  url_poster: https://theposterdb.com/api/assets/9776
```
