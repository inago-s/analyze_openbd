# analyze_openbd
ラノベの杜提供のtsvファイルを基に，WebAPIのOpenBDからライトノベルの情報をデータベース(SQLite)に保存します．

## 実行手順
1. ラノベの杜からtsvファイルをダウンロード
2. config.iniにデータベース名とフィールド名の設定を記述．
3. make_database.pyの実行
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
