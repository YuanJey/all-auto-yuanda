import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from database.database import Database
from user.user import User
from concurrent.futures import ThreadPoolExecutor, as_completed
# db_file = 'accounts.db'  # 提前准备好数据库文件路径
# db = Database(db_file)


def check(sc_account):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    try:
        user = User(driver, sc_account.account, sc_account.password)
        if user.login():
            balance=user.get_balance()

            current_date = datetime.now()
            # 获取今天的日期
            today = current_date.strftime("%Y-%m-%d")
            log_file = f"check_{today}.txt"
            
            # 格式化输出为字符串（格式为YYYY-MM-DD）
            date = current_date.strftime("%Y-%m-%d")
            driver.get("https://sc.yuanda.biz/jingdian/user/usorder.html?mcard=&start="+date+"&end=&mstatus=999")

            # 等待包含订单数量的元素加载完成
            order_count_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.color_b"))
            )
            order_count = order_count_element.text
            print(f"{sc_account.account} 订单数量：{order_count}")
            
            # 写入文件
            with open(log_file, 'a') as file:
                file.write(f"{sc_account.account} 订单数量：{order_count} 余额：{balance}\n")

    finally:
        driver.quit()

def menu2_check(accounts):
    # accounts = db.get_all_sc_account()
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(check, account)
            for account in accounts
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"发生异常: {e}")
# if __name__ == '__main__':
#     accounts = db.get_all_sc_account()
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         futures = [
#             executor.submit(check, account)
#             for account in accounts
#         ]
#
#         for future in as_completed(futures):
#             try:
#                 future.result()
#             except Exception as e:
#                 print(f"发生异常: {e}")