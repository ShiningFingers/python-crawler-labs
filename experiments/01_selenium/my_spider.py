import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "http://127.0.0.1:5000"          # 作业要提交的URL
OUT_FILE = "jixinda.json"               # 要提交的数据文件


def wait_real_data(wait):
    """等到真正有8列的数据行出现（跳过'数据加载中'占位行）"""
    wait.until(lambda d: any(
        len(r.find_elements(By.TAG_NAME, 'td')) == 8
        for r in d.find_elements(By.CSS_SELECTOR, '#log-table tbody tr')
    ))


def parse_current_page(driver):
    """解析当前页表格，返回本页数据列表"""
    page_data = []
    for row in driver.find_elements(By.CSS_SELECTOR, '#log-table tbody tr'):
        tds = row.find_elements(By.TAG_NAME, 'td')
        if len(tds) != 8:               # 跳过占位行/异常行
            continue
        page_data.append({
            "序号": tds[0].text,
            "创建时间": tds[1].text,
            "通道名称": tds[2].text,
            "签名名称": tds[3].text,
            "模板名称": tds[4].text,
            "应用": tds[5].text,
            "耗时(秒)": tds[6].text,
            "状态": tds[7].text
        })
    return page_data


def main():
    # 无头模式：不弹浏览器窗口，后台跑完自动关
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1400,900')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)    # 最长等15秒
    all_data = []

    try:
        # ===== 1. 打开网站 =====
        driver.get(URL)
        print('已打开：', URL)

        # ===== 2. 模拟登录 =====
        user = wait.until(EC.presence_of_element_located((By.ID, 'username')))
        user.clear(); user.send_keys('admin')          # 先清空再输入，避免变成 adminadmin
        pwd = driver.find_element(By.ID, 'password')
        pwd.clear(); pwd.send_keys('123456')
        driver.find_element(By.ID, 'login-btn').click()
        print('登录成功')

        # ===== 3. 进入服务日志页 =====
        wait.until(EC.element_to_be_clickable((By.ID, 'menu-log'))).click()
        print('已进入 服务日志 页面')

        # ===== 4. 输入筛选条件并搜索 =====
        sign = wait.until(EC.presence_of_element_located((By.ID, 'input-sign')))
        sign.clear(); sign.send_keys('闲云旅游')
        app = driver.find_element(By.ID, 'input-app')
        app.clear(); app.send_keys('TMS')
        driver.find_element(By.ID, 'search-btn').click()
        print('已筛选：签名=闲云旅游，应用=TMS')

        # ===== 5. 循环翻页抓取 =====
        page = 1
        while True:
            wait_real_data(wait)                        # 等真实数据渲染完
            rows = parse_current_page(driver)
            all_data.extend(rows)
            print(f'  第 {page} 页：抓到 {len(rows)} 条，累计 {len(all_data)} 条')

            next_btn = driver.find_element(By.ID, 'next-btn')
            if 'disabled' in (next_btn.get_attribute('class') or ''):
                print('  已到最后一页，停止翻页')
                break
            next_btn.click()
            page += 1
            time.sleep(1)                               # 等下一页加载

        # ===== 6. 存入 JSON =====
        with open(OUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f'\n全部完成！共 {len(all_data)} 条，已保存到 {OUT_FILE}')

    finally:
        driver.quit()                                   # 一定关浏览器


if __name__ == '__main__':
    main()