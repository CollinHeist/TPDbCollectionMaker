from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
from re import match

try:
    from bs4 import BeautifulSoup
except ImportError:
    print(f'Missing required packages - execute "pipenv install"')
    exit(1)

POSTER_URL = 'https://theposterdb.com/api/assets/{id}'

def positive_int(arg: str) -> int:
    try:
        assert arg.isdigit() and int(arg) > 0
        return int(arg)
    except Exception:
        raise ArgumentTypeError(f'Must be positive integer')

# Create ArgumentParser object and arguments
parser = ArgumentParser(description='TPDb Collection Maker')
parser.add_argument(
    '--html', '--html-file',
    dest='html_file',
    type=Path,
    required=True,
    metavar='HTML_FILE',
    help='File with TPDb Collection page HTML to scrape')
parser.add_argument(
    '--spaces', '--spacing',
    type=positive_int,
    default=2,
    metavar='NUM_SPACES',
    help='How many spaces to use in indentation')
parser.add_argument(
    '--indent',
    type=positive_int,
    default=0,
    metavar='NUM_SPACES',
    help='How many spaces to indent output')
parser.add_argument(
    '--always-quote',
    action='store_true',
    help='Whether to put all titles in quotes ("")')

# Parse given arguments
args = parser.parse_args()

# Get page HTML from file if provided
if args.html_file:
    # Verify file exists
    if not args.html_file.exists():
        print(f'File "{args.html_file.resolve()}" does not exist')
        exit(1)

    # Open file and read content
    with args.html_file.open('r') as file_handle:
        html = file_handle.read()

# Create BeautifulSoup element of HTML
webpage = BeautifulSoup(html, 'html.parser')

# Get all posters in this set, classify by content type
outputs = {'Collection': [], 'Movie': [], 'Show': []}
for poster_element in webpage.find_all('div', class_='overlay rounded-poster'):
    # Get this poster's ID for URL recreation, content type, and title
    poster_id = poster_element.attrs['data-poster-id']
    content_type = poster_element.attrs['data-poster-type']
    title = poster_element.find('p', class_='p-0 mb-1 text-break').string

    # Whether to quote title
    quote = args.always_quote or any(char in title for char in (':', ))
    title = f'"{title}"' if quote else title

    # Create strings for output
    url = POSTER_URL.format(id=poster_id)
    outputs[content_type].append(f'{title}:')
    outputs[content_type].append(f'{" " * args.spaces}url_poster: {url}')

# Output each content type
for content_type, content in outputs.items():
    # Skip empty content
    if len(content) == 0:
        continue

    indent = " " * args.indent
    print(f'{indent}# {content_type}s')
    print(indent + f'\n{indent}'.join(content))
    print()

