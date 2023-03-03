from urllib.parse import quote_plus

from lxml.html import fromstring

try:
    from moly_hu.book import Book
    from moly_hu.search_page import book_page_urls_from_seach_page
except:
    # TODO: handle somehow the calibre import style
    from calibre_plugins.moly_hu_reloaded.moly_hu.book import Book
    from calibre_plugins.moly_hu_reloaded.moly_hu.search_page import book_page_urls_from_seach_page


class MetadataSearch:
    def __init__(self, fetch_page_content, max_results = 3):
        self.books = []
        self._page_fetcher = fetch_page_content
        self._max_results = max_results

    def search(self, title: str, authors: list[str], identifiers: dict[str, str]):
        book_urls = set()

        if 'moly_hu' in identifiers:
            book_urls.add('/konyvek/' + identifiers['moly_hu'])

        search_for = None
        if len(authors) > 0 and title:
            search_for = f'{authors[0]} {title}'
        elif title:
            search_for = title
        if search_for:
            urls = self._search_for(search_for)
            if not urls and title:
                urls = self._search_for(title)
            book_urls.update(urls)

        self.books = self._get_books(book_urls)

    def _search_for(self, keyword):
        content = self._page_fetcher('https://moly.hu/kereses?utf8=%E2%9C%93&q=' + quote_plus(keyword))
        return book_page_urls_from_seach_page(fromstring(content))

    def _get_books(self, urls):
        books = list()
        for index, book_url in enumerate(urls):
            if index >= self._max_results:
                break
            books.append(self._get_book(book_url))
        return books

    def _get_book(self, url):
        book_page = self._page_fetcher('https://moly.hu/' + url)
        return Book(xml_root=fromstring(book_page), moly_id=url.rsplit('/', 1)[-1])
