# 实验 01：利用 selenium 爬取动态网页

## 实验内容

用 selenium 模拟浏览器操作，爬取一个带**登录、筛选、分页**的动态网站（模拟"集信达"短信服务日志后台），将表格数据保存为 JSON。

## 爬取目标

本地 Flask 动态网站 `http://127.0.0.1:5000`，由本目录的 `app.py` 提供。页面包含登录、服务日志表格、按签名/应用筛选、AJAX 分页。

## 文件说明

| 文件 | 作用 |
|---|---|
| `app.py` | Flask 服务端，模拟动态网站（登录、日志列表、筛选、分页 AJAX 接口） |
| `my_spider.py` | selenium 爬虫主程序（最终版，无头模式） |
| `templates/index.html` | 动态网页前端 |
| `jixinda.json` | 爬取结果示例 |
| `screenshots/scraped_page.png` | 运行截图（**注：此截图来自早期简单版项目，最终版项目未单独截图**） |

## 运行方式

### 1. 先启动动态网站

```bash
pip install flask
python app.py
```

服务启动后监听 `http://127.0.0.1:5000`。

### 2. 运行爬虫

```bash
pip install selenium
# 需要本机已安装 Chrome 浏览器和对应版本的 chromedriver
python my_spider.py
```

爬虫会：打开网站 → 登录（admin/123456）→ 进入服务日志 → 输入筛选条件（签名=闲云旅游，应用=TMS）→ 逐页抓取 → 保存到 `jixinda.json`。

## 截图说明

`screenshots/scraped_page.png` 是早期简单版（爬取书店动态网页）的截图，用于说明 selenium 截图功能。最终版（集信达日志）的运行截图待补充。
