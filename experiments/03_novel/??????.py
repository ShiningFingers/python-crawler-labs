import requests
from pyquery import PyQuery as pq

url = "https://www.biquwx.la/1_1245/603316.html"   # 笔记里的示例章节
response = requests.get(url)
print(response.status_code)          # 看是不是200
print(response.encoding)             # 笔记：可能显示 GB2312
print(response.apparent_encoding)    # 笔记：实际是 utf-8

response.encoding = response.apparent_encoding   # 关键！解决乱码

doc = pq(response.text)
title = doc('.bookname > h1').text()
content = doc('#content').text()
print(title)      # 应输出：第一卷 笼中雀 第一章 惊蛰
print(content[:100])  # 看正文前100字

with open('剑来.txt', mode='w+', encoding='utf-8') as f:
    f.write(title); f.write('\n'); f.write(content); f.write('\n')

print('单章爬取完成！')