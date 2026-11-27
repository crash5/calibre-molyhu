from moly_hu.moly_hu import generate_search_terms


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
