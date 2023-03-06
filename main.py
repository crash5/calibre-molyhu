import urllib.request

import moly_hu.moly_hu as molyhu


if __name__ == '__main__':
    print('start')

    dl = lambda x: urllib.request.urlopen(x).read().decode('utf-8')
    search = lambda x: molyhu.search(x, dl)

    book_ids = molyhu.book_ids_for('magus', ['raymond feist'], {}, search)
    book = molyhu.book_for_id(book_ids[0], dl)
    print(book)
    print('end')
