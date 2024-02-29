from argparse import ArgumentParser
from pathlib import Path
from re import compile as re_compile
from typing import Iterable, Literal

try:
    from bs4 import BeautifulSoup
except ImportError:
    print(f'Missing required packages - execute "pipenv install"')
    exit(1)


# Create ArgumentParser object and arguments
parser = ArgumentParser(description='TPDb Collection Maker')
parser.add_argument(
    'html',
    type=Path,
    metavar='HTML_FILE',
    help='file with TPDb Collection page HTML to scrape')
parser.add_argument(
    '-p', '--primary-only',
    action='store_true',
    help='only parse the primary set (ignore any Additional Sets)')
parser.add_argument(
    '-q', '--always-quote',
    action='store_true',
    help='put all titles in quotes ("")')


ContentType = Literal[
    'category', 'collection', 'show', 'movie', 'company', 'season'
]
PRIMARY_CONTENT_CLASS: str = 'row d-flex flex-wrap m-0 w-100 mx-n1 mt-n1'


class Content:
    """
    This class describes some type of content. Content contains a poster ID,
    a type, title, year, and a URL.
    """

    """Poster URL format for all TPDb posters"""
    POSTER_URL = 'https://theposterdb.com/api/assets/{id}'

    """Regex to match yearless titles and season names from full titles"""
    YEARLESS_REGEX=re_compile(r'^(.*) \(\d+\)($| - (?:Season \d+|(Specials)))$')
    SEASON_REGEX = re_compile(r'^.* - (?:Season (\d+)|(Specials))$')

    __slots__ = (
        'poster_id', 'content_type', 'title', 'use_year', 'must_quote', 'url',
        'yearless_title', 'season_number', 'sub_content',    
    )

    def __init__(self, poster_id: int,
            content_type: ContentType,
            title: str, *,
            must_quote: bool = False) -> None:
        """
        Initialize the content described by the given attributes.

        Args:
            poster_id: TPDb poster ID of the content.
            content_type: Type of content being created.
            title: Title of the content.
            must_quote: Override for whether the finalized title of this
                content should be quoted or not. Keyword only.
        """

        self.poster_id = poster_id
        self.content_type = content_type
        self.title = title
        self.use_year = False
        self.must_quote = must_quote or ': ' in self.title
        self.url = self.POSTER_URL.format(id=self.poster_id)

        # Attempt to parse the yearless title
        if (group := self.YEARLESS_REGEX.match(self.title)) is None:
            self.yearless_title = self.title
        else:
            self.yearless_title = group.group(1)

        # If season name is in the title, parse 
        if (season_group := self.SEASON_REGEX.match(self.title)) is None:
            self.season_number = None
        else:
            self.content_type = 'season'
            if season_group.group(2) == 'Specials':
                self.season_number = 0
            else:
                self.season_number = int(season_group.group(1))

        # No subcontent yet
        self.sub_content = {}


    @property
    def final_title(self) -> str:
        """
        Get the finalized title for this Content. Quoted and utilizing
        the year if necessary.
        """

        title = self.title if self.use_year else self.yearless_title
        return f'"{title}"' if self.must_quote else title


    def __repr__(self) -> str:
        attributes = ', '.join(
            f'{attr}={getattr(self, attr)!r}' for attr in self.__slots__
            if not attr.startswith('__')
        )

        return f'<Content {attributes}>'


    def __str__(self) -> str:
        """
        Get the string representation of this content. This is the
        formatted content string used within PMM, and the return format
        depends on the content type of this object.
        """

        if self.content_type in ('category', 'collection', 'movie', 'company'):
            return f'{self.final_title}:\n  url_poster: {self.url}'
        elif self.content_type == 'show':
            base = f'{self.final_title}:\n  url_poster: {self.url}'
            if len(self.sub_content) > 0:
                sub = '\n    '.join(str(self.sub_content[season])
                                    for season in sorted(self.sub_content))
                return f'{base}\n  seasons:\n    {sub}'
            
            return base
        elif self.content_type == 'season':
            return f'{self.season_number}: ' + '{url_poster: ' + self.url + '}'

        return f'<Bad content type "{self.content_type}">'


    def is_sub_content_of(self, content: 'Content') -> bool:
        """
        Determine whether the given content object is the parent content
        of this object. 

        Args:
            content: Object being compared against.

        Returns:
            True if the given object is the parent of this content.
            False otherwise.
        """

        # Only a show can have a season child
        if self.content_type != 'season' or content.content_type != 'show':
            return False

        return (content.yearless_title == self.yearless_title
                and content.title in self.title)

    
    def is_parent_content_of(self, content: 'Content') -> bool:
        """Logical composite of `is_sub_content_of` on this object."""

        return content.is_sub_content_of(self)


    def add_sub_content(self, content: 'Content') -> None:
        """
        Add the given content as sub content of this object.

        Args:
            content: Sub-content being added.
        """

        self.sub_content[content.season_number] = content


class ContentList:
    """
    This class describes a container list of Content objects. This is
    a glorified dictionary of lists for each content type
    """


    def __init__(self) -> None:
        self.content: dict[ContentType, Iterable[Content]] = {
            'category': [],
            'collection': [],
            'movie': [],
            'show': [],
            'season': [],
            'company': [],
        }


    def __bool__(self) -> bool:
        """Whether this object contains any content."""

        return any(content for content in self.content.values())
    

    def __repr__(self) -> str:
        return f'<ContentList {self.content}>'
    

    def __divider(self, label: str, /) -> str:
        return f'\n# {"-"*80}\n# {label}\n# {"-" * 80}'


    def add_content(self, new: Content) -> None:
        """
        Add the given content to this object. This finds any existing
        content the new content could be a child or parent of, and adds
        this object to them if indicated.

        Args:
            new: Content being added.
        """

        # Check if new content belongs to any existing shows
        for existing in self.content['show']:
            if new.is_sub_content_of(existing):
                existing.add_sub_content(new)
                # Can only belong to one show, stop looping
                break

        # Check if any existing seasons belong to new content
        for existing in self.content['season']:
            if new.is_parent_content_of(existing):
                new.add_sub_content(existing)

        # Check for content of this same title
        for existing in self.content[new.content_type]:
            if existing.title == new.title:
                new.use_year = True
                break

        self.content[new.content_type].append(new)


    def print(self) -> None:
        """
        Print this object. This prints segmented sections of each type
        of Content in this object.
        """

        # Print each content group
        for content_type, content_list in self.content.items():
            # Don't print empty content sets, or base seasons
            if not content_list or content_type == 'season':
                continue

            # Print divider, content type header, and all content
            print(self.__divider(content_type + 's'))
            for content in content_list:
                # print(f'{content=!r}')
                print(str(content))

        # Print season content if no parent show content was parsed
        if self.content['season'] and not self.content['show']:
            print(self.__divider('Unassigned Content'))
            for content in self.content['season']:
                print(str(content))


"""If file is entrypoint, parse args"""
if __name__ == '__main__':
    # Parse given arguments
    args = parser.parse_args()

    # Get page HTML from file if provided
    if not args.html.exists():
        print(f'File "{args.html_file.resolve()}" does not exist')
        exit(1)

    # Open file and read content
    with args.html.open('r') as file_handle:
        html = file_handle.read()

    # Create BeautifulSoup element of HTML
    webpage = BeautifulSoup(html, 'html.parser')

    # If only doing primary content, filter webpage
    if args.primary_only:
        webpage = webpage.find('div', class_=PRIMARY_CONTENT_CLASS)

    # Get all posters in this set, create Content and add to list
    content_list = ContentList()
    for poster_element in webpage.find_all('div',
                                           class_='overlay rounded-poster'):
        content = Content(
            poster_element.attrs['data-poster-id'],
            poster_element.attrs['data-poster-type'].lower(),
            poster_element.find('p', class_='p-0 mb-1 text-break').string,
            must_quote=args.always_quote,
        )
        content_list.add_content(content)

    if content_list:
        content_list.print()
    else:
        print(f'No content identified!')
