import requests
from pyquery import PyQuery as pq

CATALOG_URL = 'https://www.bqg616.cc/#/book/3153/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
}

# 请求
resp = requests.get(CATALOG_URL, headers=headers)
resp.encoding = resp.apparent_encoding      # 解决乱码

print('状态码：', resp.status_code)          # 200=成功
print('实际请求的URL：', resp.url)           # 看 # 后面是不是被丢掉了
print('页面HTML长度：', len(resp.text))       # 太短可能就是没拿到内容

# 用简化后的选择器试试
doc = pq(resp.text)
links = doc('#list > dd > a')
print('抓到章节数：', len(links))

# 打印前5个看看长啥样
print('--- 前5个章节 ---')
for i, link in enumerate(links.items()):
    if i >= 5:
        break
    print(f'{i+1}. 文本={link.text()}   href={link.attr.href}')