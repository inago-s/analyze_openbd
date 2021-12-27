import pandas as pd
import re
import glob
import sqlite3
import requests
from configparser import ConfigParser
from joblib import Parallel, delayed

OPENBD_ENDPOINT = 'https://api.openbd.jp/v1/'


def get_list():
    tsv_list = glob.glob('source/*.tsv')
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
    config_ini = ConfigParser()
    config_ini.read('config.ini')
    user_config = config_ini['User']
    default_config = config_ini['DEFAULT']

    if user_config.get('db_name') is None:
        db_name = default_config.get('db_name')
    else:
        db_name = user_config.get('db_name')

    if user_config.get('field_name') is None:
        field_name = default_config.get('field_name')
    else:
        field_name = user_config.get('field_name')

    conn = make_db(db_name, field_name)
    c = conn.cursor()

    field_name = field_name.split(',')
    query_count = len(field_name)
    excute = 'insert into book_info values (' + \
        ','.join(['?']*query_count)+')'

    isbn_list = split(get_list(), 1000)
    book_list = Parallel(n_jobs=4)(delayed(get_info)
                                   (isbn) for isbn in isbn_list)

    for books in book_list:
        for book in books:
            query = []
            # isbn
            try:
                isbn = book['summary']['isbn']
            except (KeyError, TypeError):
                continue
            if 'isbn' in field_name:
                query.append(isbn)

            # タイトル
            try:
                title = book['summary']['title']
            except (KeyError, TypeError):
                title = ''
            if 'title' in field_name:
                query.append(title)

            # 著者/イラストレーター
            author_list = []
            illustrator_list = []

            try:
                for author in book['onix']['DescriptiveDetail']['Contributor']:
                    for authortype in author['ContributorRole']:
                        if authortype == "A01":
                            author_list.append(
                                author['PersonName']['content'])
                        elif authortype == 'A12':
                            illustrator_list.append(
                                author['PersonName']['content'])

                if author_list:
                    author_list = "/".join(author_list)
                else:
                    author_list = ''

                if illustrator_list:
                    illustrator_list = "/".join(illustrator_list)
                else:
                    illustrator_list = ''
            except (KeyError, TypeError):
                author_list = ''
                illustrator_list = ''

            if 'author' in field_name:
                query.append(author_list)
            if 'illustrator' in field_name:
                query.append(illustrator_list)

            # コンテンツ内容
            temp = []
            try:
                for Content in book['onix']['CollateralDetail']['TextContent']:
                    temp.append(Content['Text'])
                content = sorted(temp, reverse=True, key=len)[0]
                content = re.sub(r"\s", "", content)
            except (KeyError, TypeError):
                content = ''

            if 'content' in field_name:
                query.append(content)

            # 価格
            try:
                prise = book['onix']["ProductSupply"]["SupplyDetail"]["Price"][0]["PriceAmount"]
            except (KeyError, TypeError):
                prise = None

            if 'prise' in field_name:
                query.append(prise)

            # ページ数
            try:
                pages = book['onix']['DescriptiveDetail']['Extent'][0]['ExtentValue']
            except (KeyError, TypeError):
                pages = ''

            if 'pages' in field_name:
                query.append(pages)

            # 発売日
            try:
                pubdate = book['summary']['pubdate']
            except (KeyError, TypeError):
                pubdate = ''

            if 'pubdate' in field_name:
                query.append(pubdate)

            # レーベル
            try:
                label = ''
                for Label in book['onix']['DescriptiveDetail']['Collection']['TitleDetail']['TitleElement']:
                    if 'TitleElementLevel' in Label and (Label['TitleElementLevel'] == "02"):
                        label = Label['TitleText']['content']
                        break
                    elif 'TitleElementLevel' in Label and (Label['TitleElementLevel'] == "03"):
                        label = Label['TitleText']['content']
                        break
            except (KeyError, TypeError):
                label = ''

            if 'label' in field_name:
                query.append(label)

            # 出版社
            try:
                publisher = book['summary']['publisher']
            except (KeyError, TypeError):
                publisher = ''

            if 'publisher' in field_name:
                query.append(publisher)

            c.execute(excute, query)
            conn.commit()

    c.close()
    conn.close()


if __name__ == '__main__':
    main()
