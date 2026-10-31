import requests
from pyquery import PyQuery as pq
import time

BASE = 'http://www.woniuxy.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
}


def get_doc(url):
    """请求页面并返回 PyQuery 对象"""
    resp = requests.get(url, headers=HEADERS)
    resp.encoding = 'utf-8'          # 蜗牛笔记用 utf-8，防止乱码
    return pq(resp.text)


def parse_list(doc):
    """列表页：提取文章链接、标题、类型、日期、封面图"""
    articles = []
    seen = set()
    # .active-one 信息最全（完整日期+类型+封面图）
    # .content-one 与它指向同一批文章且缺类型/年份，故不重复爬取
    for item in doc('.active-one').items():
        href = item.parent().attr('href')      # 如 /note/1159
        if not href or href in seen:           # 去重
            continue
        seen.add(href)
        articles.append({
            'title': item('.active-title').text().strip(),
            'type' : item('.active-detail').text().strip(),
            'date' : item('.active-time').text().strip(),
            'cover': item('img').attr('src') or '',
            'url'  : BASE + href               # 相对路径拼接成完整 URL
        })
    return articles


def parse_detail(url):
    """详情页：提取阅读数、正文、正文图片"""
    doc = get_doc(url)

    # 阅读数：.num-box 下有多个 .reading-times，取纯数字的那个
    read_num = ''
    for p in doc('.num-box .reading-times').items():
        t = p.text().strip()
        if t.isdigit():
            read_num = t
            break

    # 正文
    content = doc('.content-area').text().strip()

    # 正文图片（限定在 content-area 内，避开站点图标/验证码图）
    imgs = [img.attr('src') for img in doc('.content-area img').items() if img.attr('src')]

    return read_num, content, imgs


def main():
    all_data = []

    for page in range(1, 3):                   # 爬第 1、2 页（至少 2 页）
        url = f'{BASE}/note/page-{page}'       # 分页规律：/note/page-N
        print(f'\n===== 正在爬取第 {page} 页：{url} =====')
        doc = get_doc(url)
        articles = parse_list(doc)
        print(f'  本页获取到 {len(articles)} 篇文章')

        for i, art in enumerate(articles, 1):
            try:
                read_num, content, imgs = parse_detail(art['url'])
            except Exception as e:
                print(f'  [{i}] 详情页请求失败：{art["url"]} -> {e}')
                continue

            art['read_num'] = read_num
            art['content'] = content
            art['imgs'] = imgs
            all_data.append(art)

            print(f'\n  [{i}] 标题：{art["title"]}')
            print(f'      文章类型：{art["type"]} | 日期：{art["date"]} | 阅读数：{read_num}')
            print(f'      正文前100字：{content[:100]}')
            print(f'      图片 {len(imgs)} 张，第一张：{imgs[0] if imgs else "无"}')

            time.sleep(1)                      # 控制请求频率，防止被反爬

    # 保存到文件
    with open('woniunote.txt', 'w+', encoding='utf-8') as f:
        for art in all_data:
            f.write(f'标题：{art["title"]}\n')
            f.write(f'文章类型：{art["type"]}\n')
            f.write(f'日期：{art["date"]}\n')
            f.write(f'阅读数：{art["read_num"]}\n')
            f.write(f'文章内容：{art["content"]}\n')
            f.write(f'图片链接：{"，".join(art["imgs"]) if art["imgs"] else "无"}\n')
            f.write('-' * 60 + '\n')

    print(f'\n全部完成！共爬取 {len(all_data)} 篇文章，已保存到 woniunote.txt')


if __name__ == '__main__':
    main()