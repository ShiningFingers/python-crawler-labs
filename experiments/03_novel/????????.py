import requests
from pyquery import PyQuery as pq

# 你的第一章URL
url = "http://www.xbiquwk.com/10_10243/5023899.html"

# 请求头：伪装浏览器防反爬（笔记第八节提醒要加 User-Agent）[1](@index-ref?id=2)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
}

# 步骤1：发送请求获取页面
response = requests.get(url, headers=headers)
print('状态码：', response.status_code)        # 200 表示成功
print('页面HTML长度：', len(response.text))     # 判断是不是"空壳"

# 步骤2：处理编码（笔记：header无charset默认ISO-8859-1，乱码要手动设）
print('header猜测编码：', response.encoding)
print('内容分析编码：', response.apparent_encoding)
response.encoding = response.apparent_encoding

# 步骤3：解析标题和内容（笔记里的选择器）[1](@index-ref?id=3)
doc = pq(response.text)
title = doc('.bookname > h1').text()      # 标题：类选择器+子选择器
content = doc('#content').text()          # 正文：id选择器

print('标题：', title)
print('正文前100字：', content[:100])

# 步骤4：保存到文件（w+ 覆盖写入，第一次创建用）[1](@index-ref?id=4)
with open('极品家丁.txt', mode='w+', encoding='utf-8') as f:
    f.write(title)
    f.write('\n')
    f.write(content)
    f.write('\n')

print('单章爬取完成！')