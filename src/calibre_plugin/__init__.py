from queue import Empty, Queue
import datetime

from calibre.utils.cleantext import clean_ascii_chars
from calibre.ebooks.metadata.sources.base import Source, Option
from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata import check_isbn

import calibre_plugins.moly_hu_reloaded.moly_hu as moly_hu


def book_to_metadata(book) -> Metadata:
    metadata = Metadata(book.title(), book.authors())
    # FIXME(crash): handle results' relevance from isbn/molyid?
    metadata.source_relevance = 0
    metadata.set_identifier(Molyhu.MOLY_ID_KEY, book.moly_id())
    metadata.set_identifier('isbn', check_isbn(book.isbn()))
    metadata.comments = book.description()
    metadata.tags = book.tags()
    metadata.languages = book.languages()
    metadata.publisher = book.publisher()
    metadata.pubdate = datetime.datetime(book.publication_date(), 1, 1)
    metadata.rating = book.rating()
    if book.series():
        metadata.series = book.series()[0]
        metadata.series_index = book.series()[1]
    return metadata


class Molyhu(Source):
    name = 'Moly.hu Reloaded'
    description = _('Downloads metadata and covers from moly.hu. Based on Hokutya Moly_hu plugin.')
    author = 'Imre NAGY'
    minimum_calibre_version  = (6, 0, 0)
    version = (6, 0, 0)

    MOLY_ID_KEY = 'moly_hu'

    # Capabilities
    capabilities = frozenset(['identify', 'cover'])
    touched_fields = frozenset([
        'title',
        'authors',
        'identifier:isbn',
        f'identifier:{MOLY_ID_KEY}',
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

    # Options
    KEY_MAX_BOOKS = 'max_books'
    options = (
        Option(KEY_MAX_BOOKS, 'number', 3, _('Maximum number of books to get'), _('The maximum number of books to process from the moly.hu search result')),
    )

    def identify(self, log, result_queue, abort, title, authors, identifiers, timeout):
        max_books = self.prefs[self.KEY_MAX_BOOKS]

        search_terms = moly_hu.generate_search_terms(title, authors, identifiers)
        log.info(f'Search terms: {search_terms}')

        book_ids = []

        moly_id = identifiers.get(self.MOLY_ID_KEY)
        if moly_id:
            book_ids.append(moly_id)

        for search_term in search_terms:
            if len(book_ids) >= max_books:
                break
            if abort.is_set():
                log.info('Abort request received, returning.')
                return
            log.info(f'Search for: {search_term}')
            book_ids.extend(moly_hu.search(search_term, self._fetch_page))

        for index, id in enumerate(book_ids):
            if abort.is_set():
                log.info('Abort request received, returning.')
                return
            if index >= max_books:
                log.info(f'Max book limit reached, returning. (limit: {max_books})')
                return

            book = moly_hu.book_for_id(id, self._fetch_page)
            if not book:
                log.warning(f'No book found with id {id}')
                continue
            if covers := book.cover_urls():
                self.cache_identifier_to_cover_url(book.moly_id(), covers[0])
            self.cache_isbn_to_identifier(book.isbn(), book.moly_id())

            metadata = book_to_metadata(book)
            self.clean_downloaded_metadata(metadata)
            result_queue.put(metadata)

        error_message = None
        return error_message

    def _fetch_page(self, url):
        br = self.browser
        response = br.open(url)
        raw = response.read().strip()
        raw = raw.decode('utf-8', errors='replace')
        return clean_ascii_chars(raw)

    def get_book_url(self, identifiers: dict[str, str]):
        moly_id = identifiers.get(self.MOLY_ID_KEY, None)
        if moly_id:
            return (self.MOLY_ID_KEY, moly_id, moly_hu.book_url_for_id(moly_id))
        return None

    def get_book_url_name(self, idtype, idval, url):
        return 'moly.hu'

    def get_cached_cover_url(self, identifiers):
        moly_id = identifiers.get(self.MOLY_ID_KEY, None)
        if not moly_id:
            isbn = identifiers.get('isbn', None)
            moly_id = self.cached_isbn_to_identifier(isbn)
        return self.cached_identifier_to_cover_url(moly_id)

    # original from: calibre/src/calibre/ebooks/metadata/sources/amazon.py
    def download_cover(self, log, result_queue, abort, title=None, authors=None, identifiers={}, timeout=30, get_best_cover=False):
        cached_url = self.get_cached_cover_url(identifiers)
        if cached_url is None:
            log.info('No cached cover found, running identify')
            rq = Queue()
            self.identify(log, rq, abort, title=title, authors=authors, identifiers=identifiers, timeout=timeout)
            if abort.is_set():
                return
            results = []
            while True:
                try:
                    results.append(rq.get_nowait())
                except Empty:
                    break
            results.sort(key=self.identify_results_keygen(title=title, authors=authors, identifiers=identifiers))
            for mi in results:
                cached_url = self.get_cached_cover_url(mi.identifiers)
                if cached_url is not None:
                    break
        if cached_url is None:
            log.info('No cover found')
            return

        if abort.is_set():
            return

        log('Downloading cover from:', cached_url)
        try:
            br = self.browser
            cdata = br.open_novisit(cached_url, timeout=timeout).read()
            result_queue.put((self, cdata))
        except:
            log.exception('Failed to download cover from:', cached_url)
