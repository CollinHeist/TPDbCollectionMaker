# TPDbCollectionMaker
Python script to quickly make Plex-Meta-Manager poster entries from [ThePosterDatabase](https://theposterdb.com) (TPDb) sets.

Because TPDb doesn't permit automated scraping, this tool reads HTML files.

This tool will read handle collections, movies, shows, and season posters all in one file and output YAML that can be used in Plex-Meta-Manager metadata files. An example of part of the output for TheDoctor30's [Marvel Television Set](https://theposterdb.com/set/11318) is shown below:

```yaml
# --------------------------------------------------------------------------------
# Collections
Marvel Television:
  url_poster: https://theposterdb.com/api/assets/19724
# --------------------------------------------------------------------------------
# Shows
Marvel's Daredevil:
  url_poster: https://theposterdb.com/api/assets/19725
  seasons:
    1: {url_poster: https://theposterdb.com/api/assets/19726}
    2: {url_poster: https://theposterdb.com/api/assets/19727}
    3: {url_poster: https://theposterdb.com/api/assets/19728}
Marvel's Jessica Jones:
  url_poster: https://theposterdb.com/api/assets/19729
  seasons:
    1: {url_poster: https://theposterdb.com/api/assets/19730}
    2: {url_poster: https://theposterdb.com/api/assets/19731}
    3: {url_poster: https://theposterdb.com/api/assets/19732}
Marvel's Luke Cage:
  url_poster: https://theposterdb.com/api/assets/19733
  seasons:
    1: {url_poster: https://theposterdb.com/api/assets/19734}
    2: {url_poster: https://theposterdb.com/api/assets/19735}
# etc..
```

# How to Use
## Help Menu
This is a Python command-line tool. All arguments are shown with `--help`:

```console
$ pipenv run python main.py -h
usage: main.py [-h] [-p] [-q] HTML_FILE

TPDb Collection Maker

positional arguments:
  HTML_FILE           file with TPDb Collection page HTML to scrape

optional arguments:
  -h, --help          show this help message and exit
  -p, --primary-only  only parse the primary set (ignore any Additional Sets)
  -q, --always-quote  put all titles in quotes ("")
  ```

## Installation
> NOTE: If copying these commands, do __not__ copy the `$` - that is just to show this is a _command_.
1. Install `pipenv`:
```console
$ pip3 install pipenv
```
2. Install required packages:
```console
$ pipenv install
```
3. Download this tool:
```console
$ git clone https://github.com/CollinHeist/TPDbCollectionMaker/
```

## Getting Page HTML
Because TPDb doesn't permit automated scraping, this tool reads HTML files. To get the HTML of a set, right-click the set page and select `Inspect`:

<img src="https://user-images.githubusercontent.com/17693271/168729610-42ac80fc-afb7-40b4-a6bd-39b3f310619c.jpg" width="600"/>

This should launch your browser's HTML inspector. It should look something like:

<img src="https://user-images.githubusercontent.com/17693271/168729837-eacfc4d8-29d3-4968-80f2-17ed164a8884.jpg" width="600"/>

Go to the top-most HTML element (if HTML is selected, hold the left-arrow key to collapse all the HTML). The top-most HTML should look like:

```html
<!DOCTYPE html>
<html class="h-100" lang="en"><head>
...
```

Right-click the `<html class="h-100" lang="en"><head>` element, go to `Copy` > `Inner HTML`. Your clipboard now has the complete HTML of the set page; paste this into some file alongside the `main.py` file of this project. This file will be the input to the script (see below).

## Arguments
### `html`
Input HTML file to parse.

### `-p`, `--primary-only`
Only parse the primary content on the given HTML page, ignoring any Additional Sets. If unspecified, then the entire page is parsed.

### `-q`, `--always-quote`
Quote all titles in the output. If unspecified, only titles with colons are titled.

Below is an example of this argument:

```console
$ pipenv run python main.py in.html --always-quote
"Iron Man (2008)":
  url_poster: https://theposterdb.com/api/assets/9773
"The Incredible Hulk (2008)":
  url_poster: https://theposterdb.com/api/assets/9775
"Iron Man 2 (2010)":
  url_poster: https://theposterdb.com/api/assets/9776
```
