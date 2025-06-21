from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database.database import Database
from order.order import Order
from selenium import webdriver

from verification.verification import Verification
def login(driver,account, password):
    # login_button = WebDriverWait(driver, 60).until(
    #     EC.element_to_be_clickable((By.XPATH, '//button[@class="btn_login loginbox"]'))
    # )
    # login_button.click()
    driver.get("https://hx.yuanda.biz/Home/Public/loginbox/type/2")
    # 等待输入框出现并输入手机号,password
    phone_input = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "phone"))
    )
    phone_input.send_keys(account)
    password_input = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_input.send_keys(password)
    login_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.ID, "login"))
    )
    login_button.click()
    input("请在浏览器中完成登陆操作后，按Enter继续...")
if __name__ == '__main__':
    date = input("请输入核销的订单日期(例如:2025-06-18)：")
    db = Database('accounts.db')
    db.hx_account = db.get_hx_account()
    # db=ZODatabase('accounts.fs')
    order = Order()
    driver = webdriver.Chrome()
    driver.get("https://hx.yuanda.biz")
    verification = Verification(driver)
    verification.set_cookie()
    order_files = order.get_order_files(date)
    login_accounts=db.get_login_sc_account()
    for lg_account in login_accounts:
        order_files = "data/" + lg_account.account + ".txt"
        orders=order.get_orders_from_file(order_files)
        for jd_account, jd_password in orders:
            verification.verification(jd_account, jd_password)