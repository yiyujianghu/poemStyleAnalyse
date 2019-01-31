#！/user/bin/env python
# encoding:utf-8
"""
@author:  Dong Jun
@file:    spider.py
@time:    2019/1/29 19:50
"""

from bs4 import BeautifulSoup
import requests
import json
import os
import re

BASE_DIR = os.path.realpath(os.path.dirname(__file__)) + '/poem/'
log_path = BASE_DIR + 'log.txt'
author_dict_path = BASE_DIR + 'authorDict.txt'
BASE_URL = 'http://www.shicimingju.com'

def textRmSpace(text):
    '''替换文本中的转义字符和空格'''
    return text.replace('\n', '').replace('\t', '').replace('\r', '').replace('\v', '').replace('\u3000', '').replace(' ', '')

def textRmBrackets(text):
    '''利用正则表达式去掉文本中括号和特殊字符之间的文字'''
    result_en = re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", text)
    result = re.sub(u"\\（.*?）|\\{.*?}|\\[.*?]|\\【.*?】|\\·.*?·", "", result_en)
    if '分类标签' in result:
        result = result[:result.find('分类标签')]
    return result
    
def urlParse(url):
    '''相应url请求并解析成html代码'''
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    return soup

def url2dictORlist(URL, type):
    '''
    1、传递作者分类页面的URL，然后返回该页面的作者名字和相应的URL链接
    2、传递作者单独页面的URL，然后返回该页面所有诗词的URL链接
    '''
    soup = urlParse(URL)
    urlList = soup.find_all('h3')
    judgeWord = '/chaxun/'
    if type == 'author':
        authorAndURL = {}
        judgeWord += "zuozhe/"
        for content in urlList:
            tag_a = list(content)[1]
            if judgeWord in tag_a.attrs['href']:
                author = tag_a.text
                url = tag_a.attrs['href']
                authorAndURL[author] = BASE_URL + url
        return authorAndURL
    elif type == 'poem':
        poemURLList = []
        judgeWord += "list/"
        for content in urlList:
            tag_a = list(content)[1]
            if judgeWord in tag_a.attrs['href']:
                url = tag_a.attrs['href']
                poemURLList.append(BASE_URL + url)
        return poemURLList

def nextPageExist(pageURL):
    '''用于判断页面是否有<下一页>的点击按钮，以确定是否遍历结束，用于遍历所有作者信息和所有诗词信息'''
    soup = urlParse(pageURL)
    try:
        pageList = soup.find_all('span')
        identify = False
        for page in pageList:
            if page.text == "下一页":
                identify = True
                break
    except:
        return False
    return identify

def findAuthorDict():
    '''用于从初始的作者信息页面，返回所有的作者信息，并保存为就是json结构的数据存入txt文件中'''
    authorFirstURL = 'http://www.shicimingju.com/category/all'
    authorDictAll = url2dictORlist(authorFirstURL, 'author')
    pageCount = 2
    nextPageIdentify = True
    while nextPageIdentify:
        authorURLNow = authorFirstURL + '__' + str(pageCount)
        nextPageIdentify = nextPageExist(authorURLNow)
        authorDictNow = url2dictORlist(authorURLNow, 'author')
        authorDictAll = {**authorDictAll, **authorDictNow}
        pageCount += 1
    with open(author_dict_path, 'w', encoding='utf-8') as f_author:
        authorJsonAll = json.dumps(authorDictAll, ensure_ascii=False)
        f_author.write(authorJsonAll)


def findPoem(url):
    '''通过URL将该页面上的诗句解析出来，然后保存为<作者+内容>的数据存为txt，相关数据可用于神经网络直接训练'''
    soup = urlParse(url)
    author = ''
    authorList = soup.find_all('div', {'class':'shici-info'})[0].children
    for i in authorList:
        try:
            if "/chaxun/zuozhe/" in i.attrs['href']:
                author = i.text
        except:
            continue
    content = soup.find_all('div', {'class':'shici-content'})[0].text
    author = textRmSpace(author)   
    content = textRmSpace(content)
    contentFinal = textRmBrackets(content)
    result = author + '\t' + contentFinal + '\n'
    return result
    
def poemer2URL(poemerURL):
    '''输入一位作者的主URL，然后返回一个其全部诗词的URL列表，结果将传递给下一步遍历提取所有诗词'''
    poemFirstUrl = poemerURL
    poemURLList = url2dictORlist(poemFirstUrl, 'poem')
    pageCount = 2
    nextPageIdentify = True
    while nextPageIdentify:
        poemURLNow = poemFirstUrl[:-5] + '_' + str(pageCount) + '.html'
        nextPageIdentify = nextPageExist(poemURLNow)
        poemURLListNow = url2dictORlist(poemURLNow, 'poem')
        poemURLList.extend(poemURLListNow)
        pageCount += 1
    return poemURLList

def fileSave(authorName, urlList):
    '''传入某个作者的名字与其诗句的URL列表信息，然后将其所有诗句存在一个txt文件中'''
    filename = BASE_DIR + authorName + '.txt'
    f_data = open(filename, 'w', encoding='utf-8')
    count = 0
    for url in urlList:
        try:
            result = findPoem(url)
            authorNow = result.split('\t')[0]
            if authorNow == authorName:
                f_data.write(result)
                count += 1
            if count >= 1000:
                break
        except:
            continue
    f_data.close()


def authorListSave(authors):
    '''传入一个作者列表，然后遍历其中每一位作者的名字，然后将每一位作者的诗词存在一个txt文件中'''
    authorPoemCount = ""
    if not os.path.exists(author_dict_path):
        findAuthorDict()
    with open(author_dict_path, 'r', encoding='utf-8') as f_authorDict:
        data = f_authorDict.read()
        author_dict = json.loads(data)
    for name in authors:
        poemerURL = author_dict[name]
        poemURLList = poemer2URL(poemerURL)
        count = len(poemURLList)
        fileSave(name, poemURLList)
        poemCount = name + ":" + str(count) + "\n"
        authorPoemCount += poemCount
    with open(log_path, 'w', encoding='utf-8') as f_log:
        f_log.write(authorPoemCount)

if __name__ == '__main__':
    authors = [
               # '李白',                                                                           # 李白
               # '杜甫',                                                                           # 杜甫
               # '诗经', '先秦无名','屈原',                                                          # 先秦
               # '陶渊明',
               # '谢灵运', '谢朓', '鲍照', '庾信', '沈约', '陆机',                                    # 六朝诗风
               # '辛弃疾', '陈亮',                                                                  # 稼轩
               # '曹操', '曹植', '曹丕', '汉无名氏', '嵇康', '刘桢', '王粲', '两汉乐府',                # 汉魏诗风
               # '梁启超', '陈三立', '黄遵宪', '谭嗣同', '鲁迅', '汪精卫', '柳亚子', '郁达夫', '陈寅恪', '陈独秀',     # 晚清民国
               # '黄庭坚', '陆游', '苏轼', '杨万里',                                                  # 宋诗
               # '李商隐', '韩偓', '杜牧',                                                            # 晚唐
               # '皇甫松', '韦庄', '欧阳炯', '牛希济', '李珣', '温庭筠'                                 # 花间词
               # '张元干', '张孝祥', '刘琨', '阮籍', '阮瑀', '应璩', '陆云'
               # '秋瑾', '林则徐', '康有为', '瞿秋白', '丘逢甲'
               '李煜', '冯延巳'
                ]
    authorListSave(authors)

