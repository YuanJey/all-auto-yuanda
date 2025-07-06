from selenium import webdriver
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from order.order import Order
from verification.verification import Verification

hx_driver = webdriver.Chrome()


def check_login_status(account, password):
    hx_driver.get("https://hx.yuanda.biz")  # 访问目标网址
    login_button = WebDriverWait(hx_driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "btn_login.loginbox"))
    )
    login_button.click()
    iframe = WebDriverWait(hx_driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
    )

    # 切换到 iframe 上下文
    hx_driver.switch_to.frame(iframe)

    phone_input = WebDriverWait(hx_driver, 60).until(
        EC.presence_of_element_located((By.ID, "phone"))
    )
    phone_input.send_keys(account)
    password_input = WebDriverWait(hx_driver, 60).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_input.send_keys(password)
    login_button = WebDriverWait(hx_driver, 60).until(
        EC.element_to_be_clickable((By.ID, "login"))
    )
    login_button.click()

    hx_driver.switch_to.default_content()
    while True:
        try:
            # 等待用户信息区域出现，表示已登录
            user_info = WebDriverWait(hx_driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-right-name.fl.cf"))
            )
            print("当前已登录")
            return True
        except:
            print("未登录，请尝试重新登录")
            continue
def hx_login2():
    hx_driver.get("https://hx.yuanda.biz/Home/Public/loginbox/type/2")
    #
    # 等待输入框出现并输入手机号,password
    phone_input = WebDriverWait(hx_driver, 120).until(
        EC.presence_of_element_located((By.ID, "phone"))
    )
    phone_input.send_keys("19155789001")
    password_input = WebDriverWait(hx_driver, 120).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_input.send_keys("Yuan970901")
    login_button = WebDriverWait(hx_driver, 120).until(
        EC.element_to_be_clickable((By.ID, "login"))
    )
    login_button.click()
    input("完成登陆后输入按回车键：")
    hx_driver.get("https://hx.yuanda.biz")

if __name__ == '__main__':
    check_login_status("19155789001","Yuan970901")