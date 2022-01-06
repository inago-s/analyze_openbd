import spacy


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


nlp = spacy.load('ja_ginza_electra')
text = '『趣味の合間に人生』を座右の銘としている南雲ハジメは、突然クラスメイトと共に異世界に召喚されてしまう。異世界の住人達とは比べ物にならない能力をクラスメイトの皆が発現させる中、ハジメが発現させたのは、ごくありふれた能力である""錬成師""だった。奈落に突き落とされた彼は、その""ありふれた能力""を活用し、迷宮からの脱出を目指すが……。WEB上で絶大な人気を誇る""最強""異世界ファンタジー、開幕!!'

print(get_isekai_fantasy(nlp(text)))
