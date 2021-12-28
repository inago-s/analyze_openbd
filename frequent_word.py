import sqlite3
import spacy
from collections import Counter
import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd

con = sqlite3.connect('lanove_2020.sqlite3')
cursor = con.cursor()
nlp = spacy.load('ja_ginza_electra')

with open('stopword.txt', 'r') as f:
    stopword = f.read().split('\n')


def get_isekai_fantasy(doc):
    noun_list = []
    noun_flag = False
    prefix_flag = False
    temp = ''
    for sent in doc.sents:
        for token in sent:
            tag = token.tag_.split('-')[0]
            if tag == '接頭辞':
                if noun_flag and temp not in stopword:
                    noun_list.append(temp)
                noun_flag = False
                prefix_flag = True
                temp = token.orth_
            elif tag == '名詞':
                if prefix_flag:
                    temp += token.orth_
                    prefix_flag = False
                    noun_flag = True
                    continue
                elif noun_flag:
                    temp += token.orth_
                    continue
                temp = token.orth_
                prefix_flag = False
                noun_flag = True
            elif tag == '接尾辞':
                if noun_flag:
                    temp += token.orth_
                    if temp not in stopword:
                        noun_list.append(temp)
                prefix_flag = False
                noun_flag = False
            else:
                if noun_flag and temp not in stopword:
                    noun_list.append(temp)
                    temp = ''
                noun_flag = False
                prefix_flag = False
        if noun_flag and temp not in stopword:
            noun_list.append(temp)

    return noun_list


def get_isekai(doc):
    noun_list = []
    noun_flag = False
    prefix_flag = False
    temp = ''
    for sent in doc.sents:
        for token in sent:
            tag = token.tag_.split('-')[0]
            if tag == '接頭辞':
                if noun_flag and temp not in stopword:
                    noun_list.append(temp)
                noun_flag = False
                prefix_flag = True
                temp = token.orth_
            elif tag == '名詞':
                if prefix_flag:
                    temp += token.orth_
                    prefix_flag = False
                    noun_flag = True
                    continue
                elif noun_flag:
                    noun_list.append(temp)
                temp = token.orth_
                prefix_flag = False
                noun_flag = True
            elif tag == '接尾辞':
                if noun_flag:
                    temp += token.orth_
                    if temp not in stopword:
                        noun_list.append(temp)
                prefix_flag = False
                noun_flag = False
            else:
                if noun_flag and temp not in stopword:
                    noun_list.append(temp)
                    temp = ''
                noun_flag = False
                prefix_flag = False
        if noun_flag and temp not in stopword:
            noun_list.append(temp)

    return noun_list


word_list = []
for row in cursor.execute('select content from book_info'):
    doc = nlp(row[0])
    word_list.extend(get_isekai_fantasy(doc))


counter = Counter(word_list)
df = pd.DataFrame.from_dict(counter, orient='index', columns=['frequent'])
df = df.sort_values('frequent', ascending=False)
df.to_csv('word_2020_noun_isekai_fantasy.csv')

for data in df.head(20).itertuples():
    plt.bar(data.Index, data.frequent)

plt.grid(axis='y')
plt.xlabel('単語')
plt.xticks(rotation=90)
plt.ylabel('出現回数')
plt.savefig('word_2020_noun_isekai_fantasy.png',
            bbox_inches='tight', pad_inches=0, dpi=300)
