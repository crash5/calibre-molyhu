from typing import List, Optional
from datetime import datetime

import requests

from cps import logger
from cps.isoLanguages import get_lang3, get_language_name
from cps.services.Metadata import MetaRecord, MetaSourceInfo, Metadata

import cps.metadata_provider.moly_hu_provider as moly_hu


log = logger.create()


def book_to_metadata(book: moly_hu.Book, source_info: MetaSourceInfo, locale) -> MetaRecord:
    metadata = MetaRecord(
         id=book.moly_id(),
         title=book.title(),
         authors=book.authors(),
         url=moly_hu.book_url_for_id(book.moly_id()),
         source=source_info
    )

    if covers := book.cover_urls():
        metadata.cover =  covers[0]
    metadata.description = book.description()
    if book.series():
        metadata.series = book.series()[0]
        metadata.series_index = book.series()[1]
    metadata.identifiers[source_info.id] = book.moly_id()
    metadata.identifiers['isbn'] = book.isbn()
    metadata.publisher = book.publisher()
    if pubdate := book.publication_date():
        metadata.publishedDate = datetime(pubdate, 1, 1).strftime('%Y-%m-%d')
    metadata.rating = book.rating()
    metadata.languages = parse_languages(book.languages(), locale)
    metadata.tags = book.tags()

    return metadata


def parse_languages(langs, locale: str) -> List[str]:
    languages = [get_language_name(locale, get_lang3(lang)) for lang in langs]
    return languages


def fetch_page(page):
    return requests.get(page).text


class Molyhu(Metadata):
    __name__ = 'Moly.hu'
    __id__ = 'moly_hu'
    MOLY_ID_KEY = __id__
    MOLY_SOURCE_INFO = MetaSourceInfo(id=MOLY_ID_KEY, description=__name__, link=moly_hu.DOMAIN)

    def search(self, query: str, generic_cover: str = '', locale: str = 'en') -> Optional[List[MetaRecord]]:
        log.info(f'Search for: {query}')
        found_books = []

        if self.active:
            title_tokens = list(self.get_title_tokens(query, strip_joiners=False))
            if title_tokens:
                query = ' '.join(title_tokens)
                log.info(f'Query: {query}')

                book_ids = moly_hu.search(query, fetch_page)
                log.info(f'Found book ids: {book_ids}')
                for id in book_ids:
                    book = moly_hu.book_for_id(id, fetch_page)
                    if not book:
                        log.warning(f'No book found with id: {id}')
                        continue
                    found_books.append(book_to_metadata(book, self.MOLY_SOURCE_INFO, locale))

        return found_books
