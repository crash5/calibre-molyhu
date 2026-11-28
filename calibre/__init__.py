import datetime
from queue import Empty, Queue

import calibre_plugins.moly_hu_reloaded.moly_hu as moly_hu

from calibre.ebooks.metadata import check_isbn
from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata.sources.base import Option, Source


def book_to_metadata(
    book, remove_paragraph_spacing=False, source_relevance=0
) -> Metadata:
    metadata = Metadata(
        book.title() or _("Unknown title"), book.authors() or [_("Unknown")]
    )
    metadata.source_relevance = source_relevance

    if moly_id := book.moly_id():
        metadata.set_identifier(Molyhu.MOLY_ID_KEY, moly_id)

    if raw_isbn := book.isbn():
        if isbn := check_isbn(raw_isbn):
            metadata.set_identifier("isbn", isbn)

    if desc := book.description():
        metadata.comments = desc
        if remove_paragraph_spacing:
            metadata.comments = metadata.comments.replace("\r\n\r\n", "\r\n")

    metadata.tags = book.tags()
    metadata.languages = book.languages()
    metadata.publisher = book.publisher()

    if publication_year := book.publication_date():
        metadata.pubdate = datetime.datetime(publication_year, 1, 1)

    metadata.rating = book.rating()

    if series := book.series():
        metadata.series, metadata.series_index = series[0], series[1]

    return metadata


class Molyhu(Source):
    name = "Moly.hu Reloaded"
    description = _(
        "Downloads metadata and covers from moly.hu. Based on Hokutya Moly_hu plugin and moly.hu API"
    )
    author = "Imre NAGY"
    version = (0, 0, 0)
    minimum_calibre_version = (5, 0, 0)

    MOLY_ID_KEY = moly_hu.MOLY_ID_KEY

    # Capabilities
    capabilities = frozenset(["identify", "cover"])
    touched_fields = frozenset(
        [
            "title",
            "authors",
            "identifier:isbn",
            f"identifier:{MOLY_ID_KEY}",
            "tags",
            "comments",
            "rating",
            "series",
            "series_index",
            "publisher",
            "pubdate",
            "language",
            "languages",
        ]
    )

    # Options
    KEY_MAX_BOOKS = "max_books"
    KEY_REMOVE_PARAGRAPH_SPACING = "remove_paragraph_spacing"
    options = (
        Option(
            name=KEY_MAX_BOOKS,
            type_="number",
            default=3,
            label=_("Maximum number of books to get"),
            desc=_(
                "The maximum number of books to process from the moly.hu search result"
            ),
        ),
        Option(
            name=KEY_REMOVE_PARAGRAPH_SPACING,
            type_="bool",
            default=False,
            label=_("Remove paragraph spacing in comments field"),
            desc=_(
                'Remove additional empty space between paragraphs ("double line breaks")'
            ),
        ),
    )

    def identify(self, log, result_queue, abort, title, authors, identifiers, timeout):
        max_books = max(1, int(self.prefs.get(self.KEY_MAX_BOOKS, 3)))
        seen_ids = set()
        ordered_books = []

        if moly_id := identifiers.get(self.MOLY_ID_KEY):
            try:
                book = moly_hu.book_for_id(str(moly_id), self._fetch_page)
                if book:
                    if b_id := book.moly_id():
                        seen_ids.add(b_id)
                    ordered_books.append(book)
            except Exception as err:
                log.warning(f"Moly.hu lookup failed for id {moly_id!r}: {err}")

        search_terms = moly_hu.generate_search_terms(title, authors, identifiers)
        log.info(f"Search terms: {search_terms}")

        for search_term in search_terms:
            if len(ordered_books) >= max_books:
                break
            if abort.is_set():
                log.info("Abort request received, returning.")
                return

            log.info(f"Search for: {search_term}")
            try:
                for book in moly_hu.search(search_term, self._fetch_page):
                    b_id = book.moly_id()
                    if b_id:
                        if b_id in seen_ids:
                            continue
                        seen_ids.add(b_id)
                    ordered_books.append(book)
                    if len(ordered_books) >= max_books:
                        break
            except Exception as err:
                log.warning(f"Moly.hu search failed for {search_term!r}: {err}")

        for idx, book in enumerate(ordered_books[:max_books]):
            if abort.is_set():
                log.info("Abort request received, returning.")
                return

            b_id = book.moly_id()
            if b_id:
                if covers := book.cover_urls():
                    self.cache_identifier_to_cover_url(b_id, covers[0])
                if isbn := book.isbn():
                    self.cache_isbn_to_identifier(isbn, b_id)

            metadata = book_to_metadata(
                book, bool(self.prefs.get(self.KEY_REMOVE_PARAGRAPH_SPACING)), idx
            )
            self.clean_downloaded_metadata(metadata)

            result_queue.put(metadata)

        return None

    def _fetch_page(self, url):
        raw = self.browser.open(url).read()
        return raw.decode("utf-8", errors="replace")

    def get_book_url(self, identifiers):
        result = []
        if moly_id := identifiers.get(self.MOLY_ID_KEY):
            result.append((self.MOLY_ID_KEY, moly_id, moly_hu.book_url_for_id(moly_id)))
        if isbn := identifiers.get("isbn"):
            result.append(
                ("isbn", isbn, f"http://www.mokka.hu/mokka/CCL/q=MEGA%3D{isbn}")
            )
        return tuple(result) or None

    def get_book_urls(self, identifiers):
        return self.get_book_url(identifiers) or ()

    def get_book_url_name(self, idtype, idval, url):
        if idtype == self.MOLY_ID_KEY:
            return "moly.hu"
        if idtype == "isbn":
            return "mokka.hu"
        return None

    def get_cached_cover_url(self, identifiers):
        moly_id = identifiers.get(self.MOLY_ID_KEY) or self.cached_isbn_to_identifier(
            identifiers.get("isbn")
        )
        return self.cached_identifier_to_cover_url(moly_id)

    # original from: calibre/src/calibre/ebooks/metadata/sources/amazon.py
    def download_cover(
        self,
        log,
        result_queue,
        abort,
        title=None,
        authors=None,
        identifiers=None,
        timeout=30,
        get_best_cover=False,
    ):
        identifiers = identifiers or {}
        cached_url = self.get_cached_cover_url(identifiers)

        if cached_url is None:
            log.info("No cached cover found, running identify")
            rq = Queue()
            self.identify(
                log,
                rq,
                abort,
                title=title,
                authors=authors,
                identifiers=identifiers,
                timeout=timeout,
            )
            if abort.is_set():
                return

            results = []
            while True:
                try:
                    results.append(rq.get_nowait())
                except Empty:
                    break

            results.sort(
                key=self.identify_results_keygen(
                    title=title, authors=authors, identifiers=identifiers
                )
            )
            for mi in results:
                if (
                    cached_url := self.get_cached_cover_url(mi.identifiers)
                ) is not None:
                    break

        if cached_url is None:
            log.info("No cover found")
            return

        if abort.is_set():
            return

        log("Downloading cover from:", cached_url)
        try:
            cdata = self.browser.open_novisit(cached_url, timeout=timeout).read()
            result_queue.put((self, cdata))
        except Exception:
            log.exception("Failed to download cover from:", cached_url)
