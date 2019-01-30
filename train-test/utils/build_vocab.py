#！/user/bin/env python
# encoding:utf-8
"""
@author:  Dong Jun
@file:    fileMerge.py
@time:    18-9-10 下午3:29
"""

from gensim.test.utils import get_tmpfile
from gensim.models import Word2Vec
import jieba
import requests
import json

def stanfordCut(text, stopList, lall):
    # 这是用斯坦福分词器的接口做的，url长度受限，再从网上找nltk中相关接口
    text_list = []
    for s in text:
        if s in lall:
            text = text.replace(s, ' ')
    url = "http://172.16.194.116/keyword?content=" + text[:-2]
    response = requests.post(url)
    print("response", type(response), response)
    response.encoding = 'utf-8'
    data = json.loads(response.text)['data']
    for i in data:
        if i['word'] not in stopList:
            text_list.append(i['word'])
    return text_list
    

def wordCut(text, stopList, lall):
    text_list = []
    #for s in text:
    #    if s in lall:
    #        text = text.replace(s, ' ')
    tmp = jieba.cut(text[:-2], cut_all=False)
    for i in tmp:
        if i not in stopList:
            text_list.append(i)
    return text_list

    
def file2texts(filename, stopwordpath, financialDict, coal_dict):
    #jieba.load_userdict(financialDict)
    with open(coal_dict, 'r', encoding='utf-8') as f:
        for word in f.readlines():
            word = word.replace('\n', '')
            jieba.add_word(word)
    stopList = []
    texts = []
    lall = []
    count = 0
    #l1 = [chr(n) for n in range(ord('A'), ord('Z')+1)]
    #l2 = [chr(n) for n in range(ord('a'), ord('z')+1)]
    #l3 = [chr(n) for n in range(ord('0'), ord('9')+1)]
    #lall = l1+l2+l3
    
    with open(stopwordpath, 'r', encoding='utf-8') as f:
        for word in f.readlines():        
            stopList.append(word.replace('\n', '').replace(' ', ''))
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            data = wordCut(line, stopList, lall)        # 用jieba分词得到的结果
            # data = stanfordCut(line, stopList, lall)    # 用stanford分词得到的结果
            texts.append(data)
            count += 1
            if count%10000 == 0:
                print("{} has been finished!".format(count))
    return texts

   
def text2model(text_list, modelpath):
    path = get_tmpfile(modelpath)
    model = Word2Vec(text_list, size=200, window=6, min_count=20, workers=4)
    model.save(modelpath)

def vocabProduce(pathModel, pathout):
    fout = open(pathout, 'w', encoding='utf-8')
    fout.write('<PAD>\n')
    vec_model = Word2Vec.load(pathModel)

    num = 0
    for word in vec_model.wv.vocab:
        num += 1
        fout.write(word + '\n')

    print(num + 1)


if __name__ == '__main__':
    filepath = './data/vocab_all.txt'
    stopwordpath = './data/stopword.txt'
    modelpath = './data/word2vec_zh.model'
    pathout = './data/word.vocab.txt'
    financialDict = './data/financialWords.txt'
    coal_dict = './data/coal_dict.txt'
    texts = file2texts(filepath, stopwordpath, financialDict, coal_dict)
    text2model(texts, modelpath)
    vocabProduce(modelpath, pathout)
    
    # vec_model = Word2Vec.load(modelpath)
    # print("vectors len:{}".format(len(vec_model.wv.vectors)))

    # # find the vectors and vocab in the model
    # modelpath = './data/word2vec_zh.model'
    # vec_model = Word2Vec.load(modelpath)
    # print("vectors:{}, \n len:{}".format(vec_model.wv.vectors[0], len(vec_model.wv.vectors)))
    # num = 0
    # for i in vec_model.wv.vocab:
    #     num += 1
    #     if num<10:
    #         print(i)
    # print(num)



