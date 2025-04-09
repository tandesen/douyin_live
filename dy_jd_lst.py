#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
from lxml import etree
from selenium.common.exceptions import InvalidSessionIdException, NoSuchElementException
from sqlalchemy import create_engine, NVARCHAR, text
import pyodbc
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException
)
from selenium.webdriver.chrome.options import Options
import random
import time
from tqdm import tqdm  # 进度条显示

# 目标URL
cur_page = 1

#  研发
url_yf = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6704215862603155720%2C6704215862557018372%2C6704215886108035339%2C6704215888985327886%2C6704215897130666254%2C6704215956018694411%2C6704215957146962184%2C6704215958816295181%2C6704215963966900491%2C6704216109274368264%2C6704216296701036811%2C6704216635923761412%2C6704217321877014787%2C6704219452277262596%2C6704219534724696331%2C6938376045242353957&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=10&functionCategory=&tag="

#  运营
url_yy = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6704215882479962371%2C6704215882438019342%2C6704215908782442766%2C6704215955154667787%2C6704215961064442123%2C6704216001937934599%2C6704216057269192973%2C6704216853931100430%2C6704217437631416580%2C6704219199050352903%2C6709824273306880267%2C6850051246221429006%2C6863074795655792910&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=100&functionCategory=&tag="

#  产品
url_cp = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6704215864629004552%2C6704215864591255820%2C6704215924712409352%2C6704216224387041544&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=100&functionCategory=&tag="

#  销售
url_xs = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6709824272505768200%2C6704215938645887239%2C6704215966085024003%2C6709824272459630861%2C6709824273038444807&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=100&functionCategory=&tag="

#  职能/支持
url_zn = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6704215913488451847%2C6704215913454897421%2C6704216232129726734%2C6704216386916321540%2C6704216480889702664%2C6704216727414114564%2C6704217005358057732%2C6704219468463081735%2C6704219470161774852%2C6850051245856524558&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=100&functionCategory=&tag="

#  设计
url_sj = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6709824272514156812%2C6704216194292910348%2C6704216380595505421%2C6704216925762750724%2C6709824272627403020%2C6709824272996501772%2C6709824273332046088%2C6709824273608870155%2C6850051246036879630&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=100&functionCategory=&tag="

#  市场
url_sc = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6704215901438216462%2C6704215901392079117%2C6704216021651163395%2C6704216386178124040%2C6704216430973290760%2C6704216870330829070%2C6704216950135851275%2C6704217388763580683&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=100&functionCategory=&tag="

#  游戏策划
url_yych = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6850051244971526414%2C6850051245139298567%2C6850051245315459342%2C6850051245500008718%2C6850051245680363783&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=100&functionCategory=&tag="

#  教学教研
url_jxjy = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6794746007419619592%2C6794746007788718350%2C6794746008191371528%2C6794746008547887367%2C6794746008740825352&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=100&functionCategory=&tag="


















df_rlt = pd.DataFrame(columns=['职位名称', '地点', '合同类型', '职位类别', '职位ID', '职位描述', '职位要求'])

# 配置浏览器选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")



# 智能等待函数（带重试）
def smart_wait(driver, locator, timeout=15, retries=3, check_interval=2):
    for _ in range(retries):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            # 模拟人类随机停留
            time.sleep(random.uniform(0.5, 1.5))
            return element
        except (TimeoutException, StaleElementReferenceException):
            driver.refresh()
            time.sleep(check_interval)
    raise TimeoutException(f"元素 {locator} 未找到，已达最大重试次数 {retries}")




try:
    # 单例模式使用driver（重要修改！）
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)  # 隐性等待

    # 获取总页数
    driver.get(url_yf)
    # 显式等待关键元素加载完成。这里的关键元素会显示下一页信息。
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "li.atsx-pagination-next:not([aria-disabled='true']) > a"))
    )
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(1.0, 2.5))  # 模拟阅读时间

    tree = etree.HTML(driver.page_source)
    max_page = int(tree.xpath("//li[@title='下一页']/preceding-sibling::li[1]/a/text()")[0])

    # 分页爬取
    for cur_page in tqdm(range(1, max_page + 1), desc="爬取进度"):
        # 使用JavaScript直接跳转页码（比点击更稳定）
        if cur_page > 1:
            url_yf = F"https://jobs.bytedance.com/experienced/position?keywords=&category=6704215862603155720%2C6704215862557018372%2C6704215886108035339%2C6704215888985327886%2C6704215897130666254%2C6704215956018694411%2C6704215957146962184%2C6704215958816295181%2C6704215963966900491%2C6704216109274368264%2C6704216296701036811%2C6704216635923761412%2C6704217321877014787%2C6704219452277262596%2C6704219534724696331%2C6938376045242353957&location=&project=&type=&job_hot_flag=&current={cur_page}&limit=10&functionCategory=&tag="
            driver.execute_script(f"window.location.href = '{url_yf}';")
            smart_wait(driver, (By.CSS_SELECTOR, "div.listItems__1q9i5"), timeout=20)
            # 读取每个职位的详情链接。
            tree = etree.HTML(driver.page_source)

        # 处理每个职位
        for href in tree.xpath("""//div[@class="listItems__1q9i5"]//a[@data-id]/@href"""):
            # 拼接完整的URL
            detail_url = f"https://jobs.bytedance.com{href}"
            try:
                # 新标签页打开详情（保持主session）
                # driver.execute_script(f"window.location.href = '{detail_url}';")
                driver.get(detail_url)
                smart_wait(driver, (By.XPATH, "//span[@class='job-title']"), timeout=20)

                # 解析数据（优化XPath）
                tree2 = etree.HTML(driver.page_source)
                job_info = {
                    '职位名称': tree2.xpath("//span[@class='job-title']/text()")[0].strip(),
                    '地点': tree2.xpath("//div[contains(@class,'job-info')]/span[1]//text()")[0].strip(),
                    '合同类型': tree2.xpath("//div[contains(@class,'job-info')]/span[2]/text()")[0].strip(),
                    '职位类别': tree2.xpath("//div[contains(@class,'job-info')]/span[3]/text()")[0].strip(),
                    '职位ID': tree2.xpath("//div[contains(@class,'job-info')]/span[4]/text()")[0].strip(),
                    '职位描述': '\n'.join(
                        tree2.xpath("//div[contains(@class,'block-content')][1]//text()")).strip(),
                    '职位要求': '\n'.join(tree2.xpath("//div[contains(@class,'block-content')][2]//text()")).strip()
                }
                # print(job_info)
                df_rlt = pd.concat([df_rlt, pd.DataFrame([job_info])], ignore_index=True)
                # print(df_rlt)

                # # 关闭当前标签页
                # driver.close()
                # driver.switch_to.window(driver.window_handles[0])

                # 随机间隔防止过快请求
                time.sleep(random.uniform(1.5, 3.5))

            except Exception as e:
                print(f"第{cur_page}页处理失败: {str(e)[:50]}...")
                # 异常恢复机制
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

        df_rlt.to_excel('jd_yf.xlsx', index=False)

except Exception as e:
    print(f"主流程异常: {e}")
finally:
    if 'driver' in locals():
        driver.quit()















# deepseek 写的



# 配置浏览器选项（增强反检测）
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # 随机User-Agent池
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        # 添加更多常用UA
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    return chrome_options




# 安全点击函数
def safe_click(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(random.uniform(0.3, 0.7))
        element.click()
    except WebDriverException:
        driver.execute_script("arguments[0].click();", element)



# 主爬虫逻辑
def main_scraper(url_yf):
    df_rlt = pd.DataFrame(columns=['职位名称', '地点', '合同类型', '职位类别', '职位ID', '职位描述', '职位要求'])

    try:
        # 单例模式使用driver（重要修改！）
        driver = webdriver.Chrome(options=get_chrome_options())
        driver.implicitly_wait(10)  # 隐性等待

        # 获取总页数
        driver.get(url_yf)
        # 显式等待关键元素加载完成。这里的关键元素会显示下一页信息。
        smart_wait(driver, (By.CSS_SELECTOR, "li.atsx-pagination-next:not([aria-disabled='true']) > a"))
        # WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable(
        #         (By.CSS_SELECTOR, "li.atsx-pagination-next:not([aria-disabled='true']) > a"))
        # )
        # smart_wait(driver, (By.CSS_SELECTOR, "div.pager__3IM2I"), timeout=20)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1.0, 2.5))  # 模拟阅读时间

        tree = etree.HTML(driver.page_source)
        max_page = int(tree.xpath("//li[@title='下一页']/preceding-sibling::li[1]/a/text()")[0])

        # 分页爬取
        for cur_page in tqdm(range(1, max_page + 1), desc="爬取进度"):
            # 使用JavaScript直接跳转页码（比点击更稳定）
            if cur_page > 1:
                driver.execute_script(f"window.location.href = '{url_yf}';")
                smart_wait(driver, (By.CSS_SELECTOR, "div.listItems__1q9i5"), timeout=20)

            # # 动态滚动加载
            # last_height = driver.execute_script("return document.body.scrollHeight")
            # while True:
            #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #     time.sleep(random.uniform(1.0, 2.0))
            #     new_height = driver.execute_script("return document.body.scrollHeight")
            #     if new_height == last_height:
            #         break
            #     last_height = new_height

            # 读取每个职位的详情链接。
            tree = etree.HTML(driver.page_source)

            # 处理每个职位
            for href in tree.xpath("""//div[@class="listItems__1q9i5"]//a[@data-id]/@href"""):
                # 拼接完整的URL
                detail_url = f"https://jobs.bytedance.com{href}"
                try:
                    # 新标签页打开详情（保持主session）
                    # driver.execute_script(f"window.location.href = '{detail_url}';")
                    driver.get(detail_url)
                    smart_wait(driver, (By.XPATH, "//span[@class='job-title']"), timeout=20)

                    # 解析数据（优化XPath）
                    tree2 = etree.HTML(driver.page_source)
                    job_info = {
                        '职位名称': tree2.xpath("//span[@class='job-title']/text()")[0].strip(),
                        '地点': tree2.xpath("//div[contains(@class,'job-info')]/span[1]//text()")[0].strip(),
                        '合同类型': tree2.xpath("//div[contains(@class,'job-info')]/span[2]/text()")[0].strip(),
                        '职位类别': tree2.xpath("//div[contains(@class,'job-info')]/span[3]/text()")[0].strip(),
                        '职位ID': tree2.xpath("//div[contains(@class,'job-info')]/span[4]/text()")[0].strip(),
                        '职位描述': '\n'.join(
                            tree2.xpath("//div[contains(@class,'block-content')][1]//text()")).strip(),
                        '职位要求': '\n'.join(tree2.xpath("//div[contains(@class,'block-content')][2]//text()")).strip()
                    }
                    df_rlt = pd.concat([df_rlt, pd.DataFrame([job_info])], ignore_index=True)
                    print(df_rlt)

                    # 关闭当前标签页
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    # 随机间隔防止过快请求
                    time.sleep(random.uniform(1.5, 3.5))

                except Exception as e:
                    print(f"第{cur_page}页处理失败: {str(e)[:50]}...")
                    # 异常恢复机制
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    continue

    except Exception as e:
        print(f"主流程异常: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
    return df_rlt


df_result = main_scraper(url_yf)

# 执行示例
if __name__ == "__main__":
    url = "https://jobs.bytedance.com/position"
    df_result = main_scraper(url_yf)
    df_result.to_csv('jobs_data.csv', index=False, encoding='utf_8_sig')

















# 设置请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
}


# 配置浏览器选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

df_rlt = pd.DataFrame(columns=['职位名称', '地点', '合同类型', '职位类别', '职位ID', '职位描述', '职位要求'])


# game start.
try:
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url_yf)
    # 显式等待关键元素加载完成。这里的关键元素会显示下一页信息。
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "li.atsx-pagination-next:not([aria-disabled='true']) > a"))
    )

    # 可选：滚动到页面底部触发懒加载
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # 获取完整DOM
    full_html = driver.page_source

    # 读取每个职位的详情链接。
    tree = etree.HTML(full_html)

    max_page = int(tree.xpath("""//div[@class='pager__3IM2I']//li[@title='下一页']/preceding-sibling::li[1]/a/text()""")[0])
    driver.quit()

    for cur_page in range(1, max_page + 1):
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url_yf)

        # 显式等待关键元素加载完成。这里的关键元素会显示岗位信息。
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-id]"))
        )

        # 可选：滚动到页面底部触发懒加载
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 获取完整DOM
        full_html = driver.page_source

        # 读取每个职位的详情链接。
        tree = etree.HTML(full_html)

        for href in tree.xpath("""//div[@class="listItems__1q9i5"]//a[@data-id]/@href"""):
            # 拼接完整的URL
            detail_url = f"https://jobs.bytedance.com{href}"

            try:
                driver_detail = webdriver.Chrome(options=chrome_options)

                driver_detail.get(detail_url)

                # 显式等待关键元素加载完成。这里的关键元素会显示岗位信息。
                WebDriverWait(driver_detail, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@class='job-title']"))
                )

                # 可选：滚动到页面底部触发懒加载
                driver_detail.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # 获取完整DOM
                full_html2 = driver_detail.page_source

                # 解析职位详情
                tree2 = etree.HTML(full_html2)
                job_info = {
                    '职位名称': tree2.xpath("//span[@class='job-title']/text()")[0],
                    '地点': tree2.xpath("//div[@class='job-info']/span[1]//text()")[0],
                    '合同类型': tree2.xpath("//div[@class='job-info']/span[2]/text()")[0],
                    '职位类别': tree2.xpath("//div[@class='job-info']/span[3]/text()")[0],
                    '职位ID': tree2.xpath("//div[@class='job-info']/span[4]/text()")[0],
                    '职位描述': tree2.xpath("//div[@class='block-content'][1]/text()")[0],
                    '职位要求': tree2.xpath("//div[@class='block-content'][2]/text()")[0]
                }
                # 将职位信息添加到 DataFrame 中. pd.append or pd._append is deprecated.
                df_rlt = pd.concat([df_rlt, pd.DataFrame([job_info])], ignore_index=True)

                # 关闭详情页面的浏览器实例
                driver_detail.quit()

            except Exception as e:
                print(f"获取职位详情失败: {e}")
                continue

except InvalidSessionIdException as e:
    print(f"Session ID 无效: {e}")
finally:
    driver.quit()


# df_rlt.to_excel("dy_jd_lst.xlsx", index=False)


# ================= 配置数据库连接信息 =================
server = "localhost"          # 数据库服务器地址
database = "jobSeaker"        # 数据库名称
driver_db = "ODBC Driver 17 for SQL Server"  # 根据实际安装的驱动版本修改

# ================= 创建数据库连接 =================
connection_string = f"DRIVER={{{driver_db}}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# ================= 数据库写入配置 =================
table_name = "JobPositionsDY"  # 数据库表名（建议使用英文）

# ================= 自动建表（如果表不存在） =================
try:
    # 检查表是否存在
    cursor.execute(f"""
    IF OBJECT_ID('{table_name}', 'U') IS NULL
    BEGIN
        CREATE TABLE {table_name} (
            [职位名称] NVARCHAR(255),
            [地点] NVARCHAR(255),
            [合同类型] NVARCHAR(255),
            [职位类别] NVARCHAR(255),
            [职位ID] NVARCHAR(255) PRIMARY KEY,
            [职位描述] NVARCHAR(1000),
            [职位要求] NVARCHAR(1000)
        )
    END
    """)
    conn.commit()
    print(f"已创建新表: {table_name}")
except Exception as e:
    print(f"创建表失败: {e}")

# ================= 写入数据到数据库 =================
try:
    for _, row in df_rlt.iterrows():
        try:
            cursor.execute(f"""
            INSERT INTO {table_name} ([职位名称], [地点], [合同类型], [职位类别], [职位ID], [职位描述], [职位要求])
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, row['职位名称'], row['地点'], row['合同类型'], row['职位类别'], row['职位ID'], row['职位描述'], row['职位要求'])
        except pyodbc.IntegrityError:
            print(f"职位ID {row['职位ID']} 已存在，跳过插入。")
    conn.commit()
    print("数据写入成功！")
except Exception as e:
    print(f"写入失败，错误信息：{str(e)}")
finally:
    cursor.close()
    conn.close()



response = requests.get('https://jobs.bytedance.com/experienced/position/7468657052731590919/detail')
html_content = response.text
print(html_content)

tree = etree.HTML(html_content)

tree.xpath("//span[@class='job-title']/text()")[0]
tree.xpath('//div[@class="job-info"]/span[1]//text()')





from requests_html import HTMLSession

def get_rendered_html(url):
    session = HTMLSession()
    r = session.get(url)
    # Execute JavaScript on the page
    r.html.render(timeout=20, sleep=2)
    return r.html.html

url = 'https://jobs.bytedance.com/experienced/position/7468657052731590919/detail'
html_content = get_rendered_html(url)
tree = etree.HTML(html_content)

# Now you can use xpath on the fully rendered page
job_title = tree.xpath("//span[@class='job-title']/text()")
print(job_title)
