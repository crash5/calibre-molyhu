from calibre import browser
from calibre.utils.cleantext import clean_ascii_chars

from calibre.ebooks.metadata.sources.base import Source
from calibre.ebooks.metadata.book.base import Metadata


from calibre_plugins.moly_hu_reloaded.moly_hu.moly_hu import MetadataSearch


def get_url_content(url):
    br = browser()
    response = br.open(url)
    raw = response.read().strip()
    raw = raw.decode('utf-8', errors='replace')
    return clean_ascii_chars(raw)


class Molyhu(Source):
    name = 'Moly_hu Reloaded'
    description = _('Downloads metadata and covers from moly.hu. Based on Hokutya Moly_hu plugin.')
    author = 'Imre NAGY'
    version = (6, 0, 0)
    minimum_calibre_version  = (6, 0, 0)

    can_get_multiple_covers = True
    capabilities = frozenset(['identify', 'cover'])
    touched_fields = frozenset([
        'title',
        'authors',
        'identifier:isbn',
        'identifier:moly_hu',
        'tags',
        'comments',
        'rating',
        'series',
        'series_index',
        'publisher',
        'pubdate',
        'language',
        'languages'
    ])


    MOLY_DOMAIN = 'https://moly.hu'
    MOLY_BOOK_URL = MOLY_DOMAIN + '/konyvek'
    MOLY_ID_KEY = 'moly_hu'

    def identify(self, log, result_queue, abort, title, authors, identifiers, timeout):
        error_message = None

        x = MetadataSearch(fetch_page_content=get_url_content)
        x.search(title, authors, identifiers)
        for book in x.books:
            metadata = Metadata(book.title(), book.authors())
            metadata.source_relevance = 0
            metadata.set_identifier(self.MOLY_ID_KEY, book.moly_id())
            metadata.set_identifier('isbn', book.isbn())
            metadata.comments = book.description()
            metadata.tags = book.tags()
            metadata.languages = book.languages()
            metadata.publisher = book.publisher()
            metadata.pubdate = book.publication_date()
            metadata.rating = book.rating()
            if book.series():
                metadata.series = book.series()[0]
                metadata.series_index = book.series()[1]

            self.clean_downloaded_metadata(metadata)
            result_queue.put(metadata)

        return error_message

    def get_book_url(self, identifiers: dict[str, str]):
        moly_id = identifiers.get(self.MOLY_ID_KEY, None)
        if moly_id:
            return (self.MOLY_ID_KEY, moly_id, f'{self.MOLY_BOOK_URL}/{moly_id}')
        return None

    def get_book_url_name(self, idtype, idval, url):
        return 'moly.hu'
