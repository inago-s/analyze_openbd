# analyze_openbd
ラノベの杜提供のtsvファイルを基に，WebAPIのOpenBDからライトノベルの情報をデータベース(SQLite)に保存します．

## 実行手順
1. analyze_openbdのダウンロード
    ```shell
    git clone https://github.com/inago-s/analyze_openbd.git
    ```
2. ラノベの杜からtsvファイルをダウンロード
3. sourceフォルダを作成し，そこにtsvファイルを入れる．（複数ファイル可能）
    ```shell
    analyze_openbd
        ├── README.md
        ├── config.ini
        ├── frequent_word.py
        ├── lanove_2020.sqlite3
        ├── make_database.py
        ├── source
        │   ├── 2020.tsv
        │   └── 2021.tsv
        └── stopword.txt
    ```
4. config.iniにデータベース名とフィールド名の設定を記述．
5. make_database.pyの実行
    ```python
    pip install joblib pandas
    python make_database.py
    ```

## config.iniについて
config.iniにデータベース名と，データベース名のフィールド名（取得する項目）を記述してください．

取得できる項目は以下のとおりです．
- isbn : 13桁のISBN
- title : タイトル
- author : 著者
- illustrator : イラストレーター
- content : あらすじ
- prise : 価格
- pages : ページ数
- pubdate : 発売日
- label : レーベル
- publisher : 出版社
