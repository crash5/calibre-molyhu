from lxml.etree import strip_tags


def book_page_urls_from_seach_page(xml_root):
    book_list_root = xml_root.xpath('//a[@class="book_selector"]')
    matches = set()
    for book_item in book_list_root:
        strip_tags(book_item, 'strong')
        for url in book_item.xpath('@href'):
            matches.add(url)
    return matches
