import argparse
import urllib.request

import moly_hu.moly_hu as molyhu


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('search_for', type=str, help='What to search for eg: Raymond Feist Magus')
    parser.add_argument('-c', '--count', type=int, default=1)
    args = parser.parse_args()
    search_for = args.search_for
    max_result = args.count

    browser = lambda url: urllib.request.urlopen(url).read().decode('utf-8')

    book_ids = molyhu.search(search_for, browser)
    for count, book_id in enumerate(book_ids, start=1):
        if count > max_result:
            break
        book = molyhu.book_for_id(book_id, browser)
        print(book)
