#！/user/bin/env python
# encoding:utf-8
"""
@author:  Dong Jun
@file:    fileMerge.py
@time:    18-9-10 下午7:29
"""

import os

def fileread(filename):
    count = 1
    fout = open(filename[:-4]+'_new.txt', 'w', encoding='utf-8')
    with open(filename, 'r', encoding='utf-8') as f:
        for i in f.readlines():
            
            if count % 150 == 0:
                fout.write(i)
                print("file", i[:10])
            count += 1

def fileMerge(path):
    fout = open("filevocab.txt", 'w', encoding='utf-8')
    filelist = os.listdir(path)
    for filename in filelist:
        with open(path+filename, 'r', encoding='utf-8') as f:
            for i in f.readlines():
                fout.write(i[3:])
    fout.close()

if __name__ == '__main__':
    path = './goodbad/'
    fileMerge(path)
    


