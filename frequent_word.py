import sqlite3
import spacy
from collections import Counter
import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd

con = sqlite3.connect('lanove_2020.db')
cursor = con.cursor()
nlp = spacy.load('ja_ginza_electra')

with open('stopword.txt', 'r') as f:
    stopword = f.read().split('\n')


def get_noun_list(doc):
    noun_list = []
    noun_flag = False
    temp = ''
    for sent in doc.sents:
        for token in sent:
            tag = token.tag_.split('-')[0]
            if noun_flag:
                if tag == '名詞' or tag == '接尾辞':
                    temp += token.orth_
                else:
                    if temp not in stopword:
                        noun_list.append(temp)
                        temp = ''
                        noun_flag = False
            else:
                if tag == '名詞' or tag == '接頭辞':
                    temp += token.orth_
                    noun_flag = True
        if not temp == '' and temp not in stopword:
            noun_list.append(temp)

    return noun_list


word_list = []
for row in cursor.execute('select * from book_info'):
    doc = nlp(row[1])
    word_list.extend(get_noun_list(doc))


counter = Counter(word_list)
df = pd.DataFrame.from_dict(counter, orient='index', columns=['frequent'])
df = df.sort_values('frequent', ascending=False)
df.to_csv('word_2020.csv')

for data in df.head(20).itertuples():
    plt.bar(data.Index, data.frequent)

plt.grid(axis='y')
plt.xlabel('単語')
plt.xticks(rotation=90)
plt.ylabel('出現回数')
plt.savefig('word_2021.png', facecolor="azure",
            bbox_inches='tight', pad_inches=0, dpi=300)
