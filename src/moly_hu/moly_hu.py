from urllib.parse import quote_plus
import datetime
import re

from lxml.etree import strip_tags
from lxml.html import fromstring


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
        # FIXME(crash): check for empty book_page
        return Book(xml_root=fromstring(book_page), moly_id=url.rsplit('/', 1)[-1])


def book_page_urls_from_seach_page(xml_root):
    book_list_root = xml_root.xpath('//a[@class="book_selector"]')
    matches = set()
    for book_item in book_list_root:
        strip_tags(book_item, 'strong')
        for url in book_item.xpath('@href'):
            matches.add(url)
    return matches


# FIXME(crash): andd isvalid() method to check the required values (id, isbn, title etc.)
class Book:
    def __init__(self, xml_root, moly_id = None):
        self._xml_root = xml_root
        self._moly_id = moly_id

    def __str__(self) -> str:
        author = (self.authors()[0:1] or ('Unknown',))[0]
        return f'{author}: {self.title()} ({self.publisher()}, {self.publication_date()}, {self.isbn()}, {self.moly_id()})'

    def moly_id(self):
        return self._moly_id

    def authors(self):
        author_nodes = self._xml_root.xpath('//*[@id="content"]//div[@class="authors"]/a/text()')
        if author_nodes:
            return [str(author) for author in author_nodes]
        return []

    def title(self):
        title_node = self._xml_root.xpath('//*[@id="content"]//*[@class="fn"]/text()') \
            or self._xml_root.xpath('//*[@id="content"]//*[@class="item"]/text()')
        if title_node:
            #Cimből a ZWJ (zero-width joiner = nulla szélességű szóköz) karakter (\u200b) eltávolítása
            return title_node[0].strip().replace('\u200b', '')
        return None

    def series(self):
        series_node = self._xml_root.xpath('//*[@id="content"]//*[@class="action"]/text()')
        if series_node:
            series = series_node[0].strip('().').rsplit(' ', 1)
            try:
                # FIXME(crash): what to do if the index is '1-2' and has to be an int?
                series[1] = int(series[1])
            except:
                series[1] = 1
            return series
        return None

    def publisher(self):
        old_publisher = self._publisher('//*[@id="content"]//*[@class="items"]/div/div[1]/a/text()')
        if old_publisher and old_publisher != '+':
            return old_publisher
        return self._publisher('//*[@id="content"]//*[@class="items"]/div/div[2]/a/text()')

    def _publisher(self, xpath):
        publisher_node = self._xml_root.xpath(xpath)
        if publisher_node:
            return publisher_node[0]
        return None

    def publication_date(self):
        date_str = self._publication_date('//*[@id="content"]//*[@class="items"]/div/div[1]/text()') \
             or self._publication_date('//*[@id="content"]//*[@class="items"]/div/div[2]/text()')
        if date_str:
            # FIXME(crash): return year as int only
            return datetime.datetime(int(date_str), 1, 1)

    def _publication_date(self, xpath):
        publication_node = self._xml_root.xpath(xpath)
        for publication_value in publication_node:
            match = re.search(r'(\d{4})', publication_value)
            if match:
                return match.group(1)
        return None

    def isbn(self):
        return self._isbn('//*[@id="content"]//*[@class="items"]/div/div[2]/text()') \
            or self._isbn('//*[@id="content"]//*[@class="items"]/div/div[3]/text()')

    def _isbn(self, xpath):
        isbn_node = self._xml_root.xpath(xpath)
        for isbn_value in isbn_node:
            match = re.search(r'(\d{13}|\d{10})', isbn_value)
            if match:
                return match.group(1)
        return None

    def cover_urls(self):
        book_covers = self._xml_root.xpath('(//*[@class="coverbox"]//a/@href)')
        if book_covers:
            return [cover_url for cover_url in book_covers]
        return None

    def tags(self):
        tags_node = self._xml_root.xpath('//*[@id="tags"]//*[@class="hover_link"]/text()') \
            or self._xml_root.xpath('//*[@id="book_tags"]//*[@class="hover_link"]/text()')
        tags = [str(text) for text in tags_node if text.strip()]
        if tags:
            return tags
        return None

    def rating(self):
        rating_node = self._xml_root.xpath('//*[@id="content"]//*[@class="rating"]//*[@class="like_count"]/text()')
        if rating_node:
            return round(float(rating_node[0].strip('%').strip())*0.05)
        return None

    def languages(self):
        tags = self.tags()
        if not tags:
            return None
        langs = []
        for tag in tags:
            langId = self._translateLanguageToCode(tag)
            if langId is not None:
                langs.append(langId)
        if not langs:
            return ['hu']
        return langs

    def _translateLanguageToCode(self, displayLang):
        displayLang = displayLang.lower().strip() if displayLang else None
        langTbl = {
            None: 'und',
            'angol nyelvű': 'en',
            'német nyelvű': 'de',
            'francia nyelvű': 'fr',
            'olasz nyelvű': 'it',
            'spanyol nyelvű': 'es',
            'orosz nyelvű': 'ru',
            'török nyelvű': 'tr',
            'görüg nyelvű': 'gr',
            'kínai nyelvű': 'cn',
            'japán nyelvű': 'jp',
            'magyar nyelvű': 'hu'
        }
        return langTbl.get(displayLang, None)

    def description(self):
        description_node = self._xml_root.xpath('//*[@id="content"]//*[@class="text" and @id="full_description"]/p/text()') \
            or self._xml_root.xpath('//*[@id="content"]//*[@class="text"]/p/text()')
        if description_node:
            join_desc_node = '\n'.join(description_node)
            join_desc_node = join_desc_node.replace('\n\n', '\n')
            join_desc_node = join_desc_node.replace('\n \n', '\n')
            join_desc_node = join_desc_node.replace('Vigyázat! Cselekményleírást tartalmaz.\n', '')
            return join_desc_node
        return None
