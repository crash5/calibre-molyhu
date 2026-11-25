import argparse
import urllib.request

import moly_hu.moly_hu as molyhu

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "search_for", type=str, help="What to search for eg: Raymond Feist Magus"
    )
    parser.add_argument("-c", "--count", type=int, default=1)
    args = parser.parse_args()
    search_for = args.search_for
    max_result = args.count

    browser = (
        lambda url: urllib.request.urlopen(
            urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; CalibreMolyhu/1.0)"},
            )
        )
        .read()
        .decode("utf-8")
    )

    for count, book in enumerate(molyhu.search(search_for, browser), start=1):
        if count > max_result:
            break
        print(book)
