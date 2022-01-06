import os
import pandas as pd
import re
import glob
import sqlite3
import requests
from configparser import ConfigParser
from joblib import Parallel, delayed

OPENBD_ENDPOINT = 'https://api.openbd.jp/v1/'


def get_list():
    tsv_list = glob.glob('source/test.tsv')
    isbn_list = []
    for tsv in tsv_list:
        isbn = pd.read_table(tsv, encoding='shift_jis', usecols=['ISBN'])
        isbn_list.extend(isbn['ISBN'])

    return isbn_list


def split(isbn_list, n):
    return [isbn_list[x:x+n] for x in range(0, len(isbn_list), n)]


def get_info(isbns):
    return requests.post(OPENBD_ENDPOINT + 'get', data={'isbn': ','.join(isbns)}).json()


def make_db(db_name: str, field_name: str):
    field_name.replace('isbn', 'isbn text')\
        .replace('title', 'title text')\
        .replace('author', 'author text')\
        .replace('illustrator', 'illustrator text')\
        .replace('content', 'content text')\
        .replace('pubdate', 'pubdate text')\
        .replace('prise', 'prise int')\
        .replace('pages', 'pages int')\
        .replace('label', 'label text')\
        .replace('publisher', 'publisher text')
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    query = 'CREATE TABLE IF NOT EXISTS book_info(' + field_name + ')'
    c.execute(query)
    conn.commit()
    c.close()

    return conn


def main():
    save_folder = 'thumbnail'
    os.makedirs(save_folder, exist_ok=True)
    isbn_list = split(get_list(), 1000)
    book_list = Parallel(n_jobs=4)(delayed(get_info)
                                   (isbn) for isbn in isbn_list)

    for books in book_list:
        for book in books:
            try:
                isbn = book['summary']['isbn']
            except (KeyError, TypeError):
                continue

            url = book['summary']['cover']
            file_name = isbn+'.jpg'
            response = requests.get(url)
            image = response.content

            file_path = os.path.join(save_folder, file_name)
            with open(file_path, 'wb')as f:
                f.write(image)


if __name__ == '__main__':
    main()
