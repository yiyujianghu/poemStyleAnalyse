#!/usr/bin/env python
# encoding:utf-8
'''
@author: Dong Jun
@file:   fileMerge.py
@time:   19-2-1 20:23
'''

import os
import random

BASE_DIR = os.path.realpath(os.path.dirname(__file__)) + '/poem/'

def fileBuild(poemersList):
    train_path = data_path + 'cnews.train.txt'
    val_path = data_path + 'cnews.val.txt'
    vocab_path = data_path + 'cnews.vocab.txt'
    f_train = open(train_path, 'w', encoding='utf-8')
    f_val = open(val_path, 'w', encoding='utf-8')
    f_vocab = open(vocab_path, 'w', encoding='utf-8')
    f_vocab.write('<PAD>\n')
    vocabSet = set({})

    for poemer in poemersList:
        poemPath = poemers10_path + poemer + '.txt'
        lineCount = 0
        with open(poemPath, 'r', encoding='utf-8') as f_poem:
            data = f_poem.readlines()
            random.shuffle(data)
            random.shuffle(data)
            for content in data:
                if lineCount < 800:
                    f_train.write(content)
                else:
                    f_val.write(content)
                lineCount += 1
                poemOnly = content[3:]
                charSet = set(poemOnly)
                vocabSet |= charSet
    vocabSet -= {'\n', '\t'}

    for char in vocabSet:
        f_vocab.write(char + '\n')

    f_train.close()
    f_val.close()
    f_val.close()


if __name__ == '__main__':
    poemers10_path = BASE_DIR + 'poemers10/'
    data_path = BASE_DIR + 'data4train/'
    poemersList = ['先秦', '汉魏', '六朝', '李白', '杜甫', '晚唐', '花间', '宋诗', '稼轩', '晚清']
    fileBuild(poemersList)


