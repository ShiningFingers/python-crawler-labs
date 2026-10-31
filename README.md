# 网络爬虫 / Python 课程实验合集

本仓库汇总《互联网数据获取技术》及《Python 程序设计》课程的 5 次实验代码与必要说明。每个实验目录独立，包含可运行的最终版代码、实验报告（如有）和运行截图。

## 环境依赖

- Python 3.8+
- 各实验所需的第三方库在对应目录的 README 中说明（主要涉及 `requests`、`pyquery`、`selenium`、`flask`、`tkinter` 内置）

## 实验索引

| 编号 | 实验名 | 主要内容 | 代码入口 | 报告 | 截图 |
|---|---|---|---|---|---|
| 01 | selenium 爬取动态网页 | 用 selenium 模拟登录、筛选、翻页爬取动态网站（集信达服务日志） | [my_spider.py](experiments/01_selenium/my_spider.py) | — | [scraped_page.png](experiments/01_selenium/screenshots/scraped_page.png) |
| 02 | 蜗牛笔记爬虫 | 用 requests + PyQuery 爬取蜗牛学苑(woniuxy)文章列表与详情 | [test.py](experiments/02_woniuxy/test.py) | — | 待补 |
| 03 | 自选网站爬小说 | 用 requests + PyQuery 爬取《剑来》《极品家丁》10+ 章，含 JS 动态渲染分析与 URL 规律优化 | [剑来十章爬取.py](experiments/03_novel/剑来十章爬取.py) | [刘浩宇小说爬取实验报告定稿.docx](experiments/03_novel/report/刘浩宇小说爬取实验报告定稿.docx) | [豆瓣小说数据采集.bmp](experiments/03_novel/screenshots/豆瓣小说数据采集.bmp)、[小说排行榜数据采集.bmp](experiments/03_novel/screenshots/小说排行榜数据采集.bmp) |
| 04 | Python 程序设计基础 | tkinter 实现学生成绩管理系统（增删改查、排序、CSV 导入导出） | [student_system.py](experiments/04_python_basics/student_system.py) | [刘浩宇python实验报告.docx](experiments/04_python_basics/report/刘浩宇python实验报告.docx) | — |
| 05 | turtle 小试牛刀 | 用 turtle 绘制奥运五环 | [乌龟.py](experiments/05_turtle/乌龟.py) | — | [ring.png](experiments/05_turtle/ring.png)（待确认） |

> 实验 01、02、05 平台未要求提交实验报告，故仓库中仅放代码与说明。

## 如何新增实验（第 6 次及以后）

1. 在 `experiments/` 下新建目录 `06_<短名>/`，例如 `06_scrapy/`。
2. 放入最终版代码、`report/`（若有报告）、`screenshots/`（运行截图）。
3. 复制 `templates/实验报告模板.md` 到该目录按需改写，或直接写一个 `README.md` 说明：实验题目、爬取目标、运行方式、结果。
4. 更新本 README 的「实验索引」表格，新增一行。
5. 提交一次 commit：

```bash
git add experiments/06_xxx/ README.md
git commit -m "add experiment 06: <实验名>"
```

## 目录结构

```
.
├── experiments/
│   ├── 01_selenium/        # selenium 动态网页爬取
│   ├── 02_woniuxy/         # 蜗牛笔记爬虫
│   ├── 03_novel/           # 小说爬取
│   ├── 04_python_basics/   # Python 基础（学生成绩管理系统）
│   └── 05_turtle/          # turtle 绘图
├── templates/              # 实验报告模板
└── README.md
```
