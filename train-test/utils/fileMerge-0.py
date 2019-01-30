#！/user/bin/env python
# encoding:utf-8
"""
@author:  Dong Jun
@file:    fileMerge.py
@time:    2018/8/27 15:50
"""

import os
import random

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read().replace('\n', '').replace('\t', '').replace('\r\n', '').replace('\r', '').\
            replace('\v', '').replace('\u3000', '').replace(' ', '')

def save_file(dirname):
    f_vocab = open('data/vocab_all.txt', 'w', encoding='utf-8')
    for category in os.listdir(dirname):
        catpath = os.path.join(dirname, category)
        if not os.path.isdir(catpath):
            continue
        files = os.listdir(catpath)
        count = 0
        for cur_file in files:
            filename = os.path.join(catpath, cur_file)
            content = read_file(filename)
            f_vocab.write(content + '\n')
            count += 1
            if count % 10000 == 0:
                print("{} has been finished!".format(count))

        print('Finished:', category)

    f_vocab.close()

if __name__ == "__main__":
    save_file("./data")
