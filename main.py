import urllib.request
from pathlib import Path

from lxml.html import fromstring

from molyhu.book import Book
from molyhu.search_page import book_page_urls_from_seach_page
from molyhu.metadata_search import MetadataSearch


if __name__ == '__main__':
    print('start')

    # inputs_path = Path(__file__).parent / 'tests/inputs'
    # search_page_content = Path(inputs_path / 'search_page_raymond_feist.htm').read_text(encoding='utf-8')
    # print(book_page_urls_from_seach_page(fromstring(search_page_content)))
    # book_page_content = Path(inputs_path / 'book_page_raymond_feist_az_erzoszivu_magus.htm').read_text(encoding='utf-8')
    # print(Book(fromstring(book_page_content)))

    s = MetadataSearch(lambda x: urllib.request.urlopen(x).read().decode('utf-8'), max_results=1)
    # s.search('Az érzőszívű mágus', ['Raymond E. Feist'], {})
    # s.search('Az érzőszívű mágus', [], {})
    s.search('a', ['Raymond E. Feist'], {})
    # s.search('', [], {'moly_hu': 'raymond-e-feist-az-erzoszivu-magus'})
    print(list(map(str, s.books)))

    print('end')
