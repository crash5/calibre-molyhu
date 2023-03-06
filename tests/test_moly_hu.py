import unittest
from pathlib import Path

from lxml.html import fromstring

from moly_hu.moly_hu import Book, book_page_urls_from_seach_page


inputs_path = Path(__file__).parent / 'inputs'


class TestBookWithPageV2(unittest.TestCase):
    def setUp(self):
        book_page_content = Path(inputs_path / 'book_page_raymond_feist_az_erzoszivu_magus.htm').read_text(encoding='utf-8')
        self.book = Book(fromstring(book_page_content))

    def test_author(self):
        self.assertEqual(self.book.authors(), ['Raymond E. Feist'])

    def test_title(self):
        self.assertEqual(self.book.title(), 'Az érzőszívű mágus')

    def test_series(self):
        self.assertEqual(self.book.series(), ['A Résháború', 1])

    def test_publisher(self):
        self.assertEqual(self.book.publisher(), 'Unikornis')

    def test_publication_date(self):
        self.assertEqual(self.book.publication_date(), 1991)

    def test_isbn(self):
        self.assertEqual(self.book.isbn(), '9637519416')

    def test_cover_urls(self):
        self.assertEqual(self.book.cover_urls(), ['/system/covers/big/covers_4959.jpg?1395344202'])

    def test_tags(self):
        expected = [
            'amerikai szerző',
            'elf',
            'fantasy',
            'felnőtté válás',
            'háború',
            'heroikus fantasy',
            'high fantasy',
            'ifjúsági',
            'kaland',
            'mágia',
            'magyar nyelvű',
            'portál fantasy',
            'regény',
            'sárkány',
            'sorozat része',
            'tündér',
            'varázsló',
        ]
        self.assertEqual(sorted(self.book.tags()), sorted(expected))

    def test_rating(self):
        self.assertEqual(self.book.rating(), 5)

    def test_languages(self):
        self.assertEqual(self.book.languages(), ['hu'])

    def test_description(self):
        expected= 'Pug, a varázsló inasa megmenti Carline hercegnőt a koboldoktól, ezért nemesi rangot kap… Barátját, Tomast, az utolsó aranysárkány gyönyörű aranykarddal és vérttel ajándékozza meg. A Királyságot több oldalról fenyegeti veszély: a harcias tsuranik és a Fekete Testvériség kegyetlen harcosai megpróbálják elfoglalni a földet, amelyet emberek, tündérek, törpék együtt védelmeznek. Pug egy Résen át másik térdimenzióba kerül, új személyiséget kap, de mágikus képességeivel felülkerekedik az elnyomó Nagy Emberek praktikáin…'
        self.assertEqual(self.book.description(), expected)


class TestSearchPage(unittest.TestCase):
    def test_book_page_urls_from_seach_page(self):
        expected_urls = {
            'raymond-e-feist-janny-wurts-a-birodalom-leanya',
            'raymond-e-feist-a-demonkiraly-duhe-i-ii',
            'raymond-e-feist-janny-wurts-a-birodalom-szolgaloja-i-ii',
            'raymond-e-feist-sethanon-alkonya',
            'raymond-e-feist-a-kiraly-kaloza-i-ii',
            'raymond-e-feist-magus-a-mester',
            'raymond-e-feist-magus-a-tanitvany',
            'raymond-e-feist-ezusttovis',
            'raymond-e-feist-verbeli-herceg',
            'raymond-e-feist-az-erzoszivu-magus'}

        page_content = fromstring(Path(inputs_path / 'search_page_raymond_feist.htm').read_text(encoding='utf-8'))
        book_urls = book_page_urls_from_seach_page(page_content)

        self.assertEqual(book_urls, expected_urls)


class TestBookWithEmptyInput(unittest.TestCase):
    def setUp(self):
        self.book = Book(fromstring('dummy data'))

    def test_author(self):
        self.assertEqual(self.book.authors(), [])

    def test_title(self):
        self.assertEqual(self.book.title(), None)

    def test_series(self):
        self.assertEqual(self.book.series(), None)

    def test_publisher(self):
        self.assertEqual(self.book.publisher(), None)

    def test_publication_date(self):
        self.assertEqual(self.book.publication_date(), None)

    def test_isbn(self):
        self.assertEqual(self.book.isbn(), None)

    def test_cover_urls(self):
        self.assertEqual(self.book.cover_urls(), None)

    def test_tags(self):
        self.assertEqual(self.book.tags(), None)

    def test_rating(self):
        self.assertEqual(self.book.rating(), None)

    def test_languages(self):
        self.assertEqual(self.book.languages(), None)

    def test_description(self):
        self.assertEqual(self.book.description(), None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
