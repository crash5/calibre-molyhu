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
