# 实验 02：使用简单爬虫框架蜗牛笔记

## 实验内容

用 `requests` + `PyQuery` 爬取蜗牛学苑（woniuxy.com）的笔记文章列表与详情页，提取标题、类型、日期、阅读数、正文、图片链接。

## 爬取目标

- 列表页：`http://www.woniuxy.com/note/page-{N}`（分页）
- 详情页：每篇文章的 `/note/{id}` 页面

## 文件说明

| 文件 | 作用 |
|---|---|
| `test.py` | 爬虫主程序，爬前 2 页文章列表及详情，保存到 `woniunote.txt` |
| `woniunote.txt` | 爬取结果（文章标题、类型、日期、阅读数、正文、图片链接） |

## 运行方式

```bash
pip install requests pyquery
python test.py
```

程序会依次请求第 1、2 页列表，逐篇请求详情页，最后将结果写入 `woniunote.txt`。每篇请求间隔 1 秒防反爬。

## 说明

- **未找到本次实验的实验报告和运行结果截图**，仓库中仅保留代码与爬取结果文本。如需截图可运行后补充。
- 本实验未使用 scrapy 等框架，而是用 requests + PyQuery 实现，符合"简单爬虫"的要求。
