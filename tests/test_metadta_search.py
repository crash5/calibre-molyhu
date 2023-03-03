import unittest
from pathlib import Path

# from lxml.html import fromstring

# from molyhu.book import Book
# from molyhu.search_page import book_page_urls_from_seach_page

from moly_hu.metadata_search import MetadataSearch

inputs_path = Path(__file__).parent / 'inputs'


def content_fetcher(url):
    yield Path(inputs_path / 'search_page_raymond_feist.htm').read_text(encoding='utf-8')
    yield Path(inputs_path / 'book_page_raymond_feist_az_erzoszivu_magus.htm').read_text(encoding='utf-8')


class TestMetadaSearch(unittest.TestCase):
    @unittest.skip
    def test_b1(self):
        s = MetadataSearch(content_fetcher)
        s.search('', [], {})
        self.assertEqual(s.books[0].title(), 'Az érzőszívű mágus')
