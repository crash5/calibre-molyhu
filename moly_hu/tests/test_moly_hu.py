from pathlib import Path

from lxml.html import fromstring

from moly_hu.moly_hu import Book, book_page_urls_from_seach_page, generate_search_terms

test_inputs_path = Path(__file__).parent / "inputs"


def read_book(file_name: str) -> Book:
    book_page_content = Path(test_inputs_path / file_name).read_text(encoding="utf-8")
    return Book(fromstring(book_page_content))


def test_book_page_v2():
    book = read_book("book_page_raymond_feist_az_erzoszivu_magus.htm")

    assert book.authors() == ["Raymond E. Feist"]
    assert book.title() == "Az érzőszívű mágus"
    assert book.series() == ["A Résháború", 1]
    assert book.publisher() == "Unikornis"
    assert book.publication_date() == 1991
    assert book.isbn() == "9637519416"
    assert book.cover_urls() == [
        "https://moly.hu/system/covers/big/covers_4959.jpg?1395344202"
    ]
    assert book.rating() == 5
    assert book.languages() == ["hu"]

    expected_tags = [
        "amerikai szerző",
        "elf",
        "fantasy",
        "felnőtté válás",
        "háború",
        "heroikus fantasy",
        "high fantasy",
        "ifjúsági",
        "kaland",
        "mágia",
        "magyar nyelvű",
        "portál fantasy",
        "regény",
        "sárkány",
        "sorozat része",
        "tündér",
        "varázsló",
    ]
    assert sorted(book.tags()) == sorted(expected_tags)  # type:ignore

    expected_description = "Pug, a varázsló inasa megmenti Carline hercegnőt a koboldoktól, ezért nemesi rangot kap… Barátját, Tomast, az utolsó aranysárkány gyönyörű aranykarddal és vérttel ajándékozza meg. A Királyságot több oldalról fenyegeti veszély: a harcias tsuranik és a Fekete Testvériség kegyetlen harcosai megpróbálják elfoglalni a földet, amelyet emberek, tündérek, törpék együtt védelmeznek. Pug egy Résen át másik térdimenzióba kerül, új személyiséget kap, de mágikus képességeivel felülkerekedik az elnyomó Nagy Emberek praktikáin…"
    assert book.description() == expected_description


def test_book_with_empty_input():
    book = Book(fromstring("dummy data"))

    assert book.authors() == None
    assert book.title() == None
    assert book.series() == None
    assert book.publisher() == None
    assert book.publication_date() == None
    assert book.isbn() == None
    assert book.cover_urls() == None
    assert book.tags() == None
    assert book.rating() == None
    assert book.languages() == None
    assert book.description() == None


def test_search_page():
    expected_urls = {
        "raymond-e-feist-janny-wurts-a-birodalom-leanya",
        "raymond-e-feist-a-demonkiraly-duhe-i-ii",
        "raymond-e-feist-janny-wurts-a-birodalom-szolgaloja-i-ii",
        "raymond-e-feist-sethanon-alkonya",
        "raymond-e-feist-a-kiraly-kaloza-i-ii",
        "raymond-e-feist-magus-a-mester",
        "raymond-e-feist-magus-a-tanitvany",
        "raymond-e-feist-ezusttovis",
        "raymond-e-feist-verbeli-herceg",
        "raymond-e-feist-az-erzoszivu-magus",
    }

    page_content = fromstring(
        Path(test_inputs_path / "search_page_raymond_feist.htm").read_text(
            encoding="utf-8"
        )
    )
    book_urls = book_page_urls_from_seach_page(page_content)

    assert book_urls == expected_urls


def test_search_author_and_title():
    authors = ["Raymond E. Feist", "Dummy Additional Author"]
    title = "Az ​érzőszívű mágus"
    authors = [authors[0]]
    title = title
    identifiers = {}
    expected = [
        "Raymond E. Feist Az ​érzőszívű mágus",
        "Az ​érzőszívű mágus",
    ]
    result = generate_search_terms(title, authors, identifiers)
    assert result == expected


def test_search_isbn_only():
    identifiers = {
        "isbn": "9637519416",
        "moly_hu": "raymond-e-feist-az-erzoszivu-magus",
    }
    authors = []
    title = ""
    identifiers = {"isbn": identifiers["isbn"]}
    expected = [
        "9637519416",
    ]
    result = generate_search_terms(title, authors, identifiers)
    assert result == expected


def test_search_title_only():
    authors = []
    title = "Az ​érzőszívű mágus"
    identifiers = {}
    expected = [
        "Az ​érzőszívű mágus",
    ]
    result = generate_search_terms(title, authors, identifiers)
    assert result == expected


def test_search_order_if_everything_available():
    authors = ["Raymond E. Feist", "Dummy Additional Author"]
    title = "Az ​érzőszívű mágus"
    identifiers = {
        "isbn": "9637519416",
        "moly_hu": "raymond-e-feist-az-erzoszivu-magus",
    }
    authors = [authors[0]]
    title = title
    identifiers = identifiers
    expected = [
        "9637519416",
        "Raymond E. Feist Az ​érzőszívű mágus",
        "Az ​érzőszívű mágus",
    ]
    result = generate_search_terms(title, authors, identifiers)
    assert result == expected


def test_search_multiple_author():
    authors = ["Raymond E. Feist", "Dummy Additional Author"]
    title = "Az ​érzőszívű mágus"
    identifiers = {}
    expected = [
        "Raymond E. Feist Az ​érzőszívű mágus",
        "Dummy Additional Author Az ​érzőszívű mágus",
        "Az ​érzőszívű mágus",
    ]
    result = generate_search_terms(title, authors, identifiers)
    assert result == expected
