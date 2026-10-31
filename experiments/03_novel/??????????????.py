import requests
from pyquery import PyQuery as pq
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
}

base_url = 'http://www.xbiquwk.com/10_10243/'
start_num = 5023899          # 第一章的数字

for i in range(10):          # 爬取10章
    num = start_num + i      # 数字+1递增（你发现的规律）
    url = base_url + str(num) + '.html'
    print('正在爬取：', url)

    # 请求 + 编码处理
    resp = requests.get(url, headers=headers)
    resp.encoding = resp.apparent_encoding

    # 解析标题和正文
    doc = pq(resp.text)
    title = doc('.bookname > h1').text()
    content = doc('#content').text()

    # 写入：第一章用 w+ 覆盖，后续用 a+ 追加 [2](@index-ref?id=3)
    mode = 'w+' if i == 0 else 'a+'
    with open('极品家丁.txt', mode=mode, encoding='utf-8') as f:
        f.write(title)
        f.write('\n')
        f.write(content)
        f.write('\n')

    print(f'  第{i+1}章完成：{title}')

    time.sleep(2)            # 每章间隔2秒，防止被封

print('10章全部爬取完成！')