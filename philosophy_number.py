from urllib.parse import urljoin
from bs4 import BeautifulSoup
from itertools import count
from urllib import request
import argparse
import bs4
import re

wikipedia_address = 'http://en.wikipedia.org/'


def build_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'pages',
        help='Pages to crawl.',
        type=str,
        nargs='*'
    )

    parser.add_argument(
        '-r', '--random',
        help='Display this many random pages',
        type=int,
        default=0
    )

    parser.add_argument(
        '--examples',
        help='Display some examples',
        action='store_true',
        default=False
    )

    return parser


def prune_parenthesised(paragraph):
    paren_start = paragraph.find(text=re.compile('\('))
    if paren_start is None:
        return

    open_parens = 0
    current_element = paren_start
    to_remove = []
    while current_element is not None:
        if isinstance(current_element, bs4.element.NavigableString):
            open_parens += current_element.count('(')
            open_parens -= current_element.count(')')

        to_remove.append(current_element)
        current_element = current_element.next_element

        if open_parens == 0:
            break

    for item in to_remove:
        item.extract()


def get_number(starting_page, print_page=True, seen=None):
    if seen is None:
        seen = set()

    if print_page:
        print(starting_page)

    # Cycle
    if starting_page in seen:
        return float('inf')
    else:
        seen.add(starting_page)

    url = urljoin(wikipedia_address, starting_page)

    if starting_page == '/wiki/Philosophy':
        return 0

    content = request.urlopen(url).read()
    soup = BeautifulSoup(content, 'html.parser')
    tables = soup.findAll('table')
    for table in tables:
        table.extract()
    paragraphs = soup.findAll('p')
    for paragraph in paragraphs:
        prune_parenthesised(paragraph)
        prune_list = (
            paragraph.findAll('sup', 'reference') +
            paragraph.findAll('div', 'thumbinner') +
            paragraph.findAll('i') +
            paragraph.findAll('span', 'unicode haudio')
        )
        for item in prune_list:
            item.extract()

        link = paragraph.find('a')
        if link is not None:
            break
    if link is None:
        return float('inf')

    return 1 + get_number(link['href'], seen=seen)


def main():
    args = build_parser().parse_args()

    if args.examples:
        pages = [
            'Beige',
            '502nd_Military_Intelligence_Battalion',
            'E._P._Thompson',
            'Johann_Georg_Fuchs_von_Dornheim',
            'List_of_animals_with_fraudulent_diplomas',
            'Lil_jon',
            'spanish_cuisine',
            'Norwegian_butter_crisis'
        ]

        for page in pages:
            number = get_number('/wiki/' + page)
            print(number)

    for page in args.pages:
        number = get_number('/wiki/' + page)
        print(number)

    for iteration in count(0):
        if args.random != -1:
            if iteration >= args.random:
                break
        random = request.urlopen(
            'https://en.wikipedia.org/wiki/Special:Random'
        ).url.split('/')[-1]
        number = get_number('/wiki/' + random)
        print(number)


if __name__ == '__main__':
    main()
