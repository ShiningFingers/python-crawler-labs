# 小组+姓名
# 小说章节爬虫：requests + PyQuery（爬取10章 + 2秒间隔 + 上限控制）

import requests
from pyquery import PyQuery as pq
import time

# ==================== 配置区 ====================
CATALOG_URL = 'https://www.biquwx.la/1_1245/'   # 目录页（换成你的小说）
CHAPTER_LINK_SELECTOR = '#list > dl > dd > a'    # 章节链接选择器
TITLE_SELECTOR = '.bookname > h1'                # 标题选择器
CONTENT_SELECTOR = '#content'                    # 正文选择器
MAX_CHAPTERS = 10        # 老师要求：爬10章
DELAY = 2                # 老师要求：2秒间隔
OUTPUT_FILE = '剑来.txt'

# 请求头：伪装浏览器防反爬 [1](@index-ref?id=5)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}
# ================================================

# ① 先清空/创建文件（w+ 覆盖写入）
with open(OUTPUT_FILE, mode='w+', encoding='utf-8') as f:
    f.write('')   # 首次创建，清空旧内容

# ② 获取目录页，拿所有章节链接
response = requests.get(CATALOG_URL, headers=headers)
response.encoding = response.apparent_encoding     # 解决乱码 [1](@index-ref?id=6)
doc = pq(response.text)
links = doc(CHAPTER_LINK_SELECTOR)
print(f'目录页获取成功，发现章节链接')

# ③ 遍历章节，只爬前10章
count = 0
for link in links.items():
    if count >= MAX_CHAPTERS:      # 达到10章就停
        break
    # 拼接完整URL（目录页href是相对路径，需补域名）[1](@index-ref?id=7)
    chapter_url = CATALOG_URL + link.attr.href
    count += 1
    print(f'正在爬取第 {count} 章：{link.text()}')

    try:
        resp = requests.get(chapter_url, headers=headers)
        resp.encoding = resp.apparent_encoding
        doc_ch = pq(resp.text)
        title = doc_ch(TITLE_SELECTOR).text()
        content = doc_ch(CONTENT_SELECTOR).text()

        # a+ 追加写入
        with open(OUTPUT_FILE, mode='a+', encoding='utf-8') as f:
            f.write(title); f.write('\n'); f.write(content); f.write('\n')
    except Exception as e:
        print(f'  第{count}章失败：{e}')
        continue

    # 每章间隔2秒，防止被封
    time.sleep(DELAY)

print(f'\n完成！共爬取 {count} 章，保存到 {OUTPUT_FILE}')