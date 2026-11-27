import json
import re
from urllib.parse import quote_plus

DOMAIN = "https://moly.hu"
BOOK_URL = f"{DOMAIN}/konyvek"
API_URL = f"{DOMAIN}/api/calibre"

YEAR_RE = re.compile(r"(\d{4})")
ISBN_RE = re.compile(r"(\d{13}|\d{10})")

LANG_MAP = {
    "magyar": "hu",
    "magyar nyelvű": "hu",
    "angol": "en",
    "angol nyelvű": "en",
    "német": "de",
    "német nyelvű": "de",
    "francia": "fr",
    "francia nyelvű": "fr",
    "olasz": "it",
    "olasz nyelvű": "it",
    "spanyol": "es",
    "spanyol nyelvű": "es",
    "orosz": "ru",
    "orosz nyelvű": "ru",
    "török": "tr",
    "török nyelvű": "tr",
    "görög": "el",
    "görög nyelvű": "el",
    "kínai": "zh",
    "kínai nyelvű": "zh",
    "japán": "ja",
    "japán nyelvű": "ja",
}


def generate_search_terms(title, authors, identifiers):
    search_terms = []
    if isbn := identifiers.get("isbn"):
        search_terms.append(isbn)
    if authors and title:
        search_terms.extend(f"{author} {title}" for author in authors)
    if title:
        search_terms.append(title)
    return list(dict.fromkeys(search_terms))


def search(keyword, fetch_page_content):
    search_url = f"{API_URL}?q={quote_plus(keyword)}"
    content = fetch_page_content(search_url)
    if not content:
        return []
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return [Book(item) for item in data if isinstance(item, dict)]


def book_for_id(book_id, fetch_page_content):
    target_id = str(book_id)
    books = search(target_id, fetch_page_content)
    for book in books:
        if book.moly_id() == target_id:
            return book
    return books[0] if books else None


def book_url_for_id(book_id):
    return f"{BOOK_URL}/{book_id}"


def _flatten_strings(value):
    result = []
    if isinstance(value, list):
        for item in value:
            result.extend(_flatten_strings(item))
    elif value is not None:
        text = str(value)
        if text:
            result.append(text)
    return result


class Book:
    def __init__(self, data: dict):
        self._data = data

    def __str__(self) -> str:
        authors = self.authors()
        author = authors[0] if authors else "Unknown"
        series_info = self.series()
        series = f" [{series_info[0]} / {series_info[1]}]" if series_info else ""
        return f"{author}: {self.title()}{series} ({self.publisher()}, {self.publication_date()}, {self.isbn()}, {self.moly_id()})"

    def moly_id(self):
        book_id = self._data.get("id")
        return str(book_id) if book_id is not None else None

    def authors(self):
        raw_author = self._data.get("author")
        if not raw_author:
            return None

        if isinstance(raw_author, list):
            authors = _flatten_strings(raw_author)
        else:
            authors = [a for a in str(raw_author).split(" - ") if a]

        return authors or None

    def title(self):
        title = self._data.get("title")
        return str(title) if title else None

    def series(self):
        series_name = self._data.get("series")
        if not series_name:
            return None
        series_index = self._data.get("series_index")
        try:
            index_val = float(series_index) if series_index is not None else 1.0
            if index_val.is_integer():
                index_val = int(index_val)
        except (ValueError, TypeError):
            index_val = 1
        return [str(series_name), index_val]

    def publisher(self):
        publishers = _flatten_strings(self._data.get("publisher"))
        return publishers[0] if publishers else None

    def publication_date(self):
        for date_val in _flatten_strings(self._data.get("pubdate")):
            if match := YEAR_RE.search(date_val):
                return int(match.group(1))
        return None

    def isbn(self):
        for isbn_val in _flatten_strings(self._data.get("isbn")):
            clean = isbn_val.replace("-", "")
            if match := ISBN_RE.search(clean):
                return match.group(1)
        return None

    def cover_urls(self):
        urls = []
        for url in _flatten_strings(self._data.get("cover")):
            if url.startswith("http"):
                urls.append(url)
            elif url.startswith("/"):
                urls.append(f"{DOMAIN}{url}")
        return urls or None

    def tags(self):
        return _flatten_strings(self._data.get("tags")) or None

    def rating(self):
        raw_rating = self._data.get("rating")
        if raw_rating is None:
            return None
        try:
            val = float(raw_rating)
            return round(val, 2) if val > 0 else None
        except (ValueError, TypeError):
            return None

    def languages(self):
        langs = []
        for lang in _flatten_strings(self._data.get("languages")):
            code = self._translateLanguageToCode(lang)
            if code and code not in langs:
                langs.append(code)

        if not langs and (book_tags := self.tags()):
            for tag in book_tags:
                code = self._translateLanguageToCode(tag)
                if code and code not in langs:
                    langs.append(code)

        return langs or ["hu"]

    def _translateLanguageToCode(self, displayLang):
        return LANG_MAP.get(displayLang.lower()) if displayLang else None

    def description(self):
        desc = self._data.get("description") or self._data.get("comments")
        return str(desc) if desc else None
