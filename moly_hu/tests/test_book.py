from moly_hu.moly_hu import Book


def test_book_with_empty_input():
    book = Book({})

    assert book.authors() == None
    assert book.title() == None
    assert book.series() == None
    assert book.publisher() == None
    assert book.publication_date() == None
    assert book.isbn() == None
    assert book.cover_urls() == None
    assert book.tags() == None
    assert book.rating() == None
    assert book.languages() == ["hu"]
    assert book.description() == None


def test_book_with_2_hyphenated_authors():
    book = Book({"author": "Neil Gaiman - Terry Pratchett"})

    assert book.authors() == ["Neil Gaiman", "Terry Pratchett"]


def test_book_with_3_hyphenated_authors():
    book = Book({"author": "John Green - Maureen Johnson - Lauren Myracle"})

    assert book.authors() == ["John Green", "Maureen Johnson", "Lauren Myracle"]

def test_book_with_1_author():
    book = Book({"author": "John Green"})

    assert book.authors() == ["John Green"]
