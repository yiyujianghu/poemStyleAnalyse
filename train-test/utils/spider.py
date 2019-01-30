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

def textRmSpace(text):
    return text.replace('\n', '').replace('\t', '').replace('\r', '').replace('\v', '').replace('\u3000', '').replace(' ', '')
    
def urlParse(url):
    r = requests.get(url)
    html = r.text  # 服务器返回响应
    return html

def findPoem(html):
    # html = urlParse(url)
    soup = BeautifulSoup(html, "html.parser")
    author = ''
    authorList = soup.find_all('div',{'class':'shici-info'})[0].children
    for i in authorList:
        try:
            if "/chaxun/zuozhe/" in i.attrs['href']:
                author = i.text
        except:
            continue
    content = soup.find_all('div',{'class':'shici-content'})[0].text
    author = textRmSpace(author)   
    content = textRmSpace(content)
    result = author + '\t' + content + '\n'
    return result
    
def poemer2URL(html):
    urlList = []
    soup = BeautifulSoup(html, "html.parser")
    poemUrlList = soup.find_all('h3')[0].children
    for i in poemUrlList:
        try:
            for j in i[0].children:
                if '/chaxun/list/' in j.attrs['href']:
                    urlList.append(j.attrs['href'])
        except:
            continue
    return urlList

def fileSave(authorInfo):
    urlList = authorInfo['urls']
    filename = authorInfo['name'] + '.txt'
    f_data = open(filename, 'w', encoding='utf-8')
    count = 0
    for url in urlList:
        try:
            html = urlParse(url)
            result = findPoem(html)
            authorNow = result.split('\t')[0]
            if authorNow == authorInfo['name']:
                f_data.write(result)
                count += 1
        except:
            continue
    f_data.close()
    return count

if __name__ == '__main__':
    # url = 'http://www.shicimingju.com/chaxun/list/26669.html'
    # data = findPoem(url)
    # print(data)
    # print(data.split('\t')[0]=='xx')

    authorList = ['李白', '杜甫']
    url_lb = ['http://www.shicimingju.com/chaxun/list/26669.html', 'http://www.shicimingju.com/chaxun/list/25739.html']
    url_df = ['http://www.shicimingju.com/chaxun/list/22412.html', 'http://www.shicimingju.com/chaxun/list/3075402.html']
    authorInfoAll = [{'name':'李白', 'urls':url_lb}, {'name':'杜甫', 'urls':url_df}]
    authorPoemCount = ""
    for i in range(len(authorInfoAll)):
        authorInfo = authorInfoAll[i]
        count = fileSave(authorInfo)
        poemCount = authorInfo['name'] + ":" + str(count) + "\n"
        authorPoemCount += poemCount

    with open("log.txt", 'w', encoding='utf-8') as f_log:
        f_log.write(authorPoemCount)

