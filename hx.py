import os

from selenium import webdriver
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from order.order import Order
from verification.verification import Verification

hx_driver = webdriver.Chrome()


def hx_login(account, password):
    hx_driver.get("https://hx.yuanda.biz")  # 访问目标网址

    login_button = WebDriverWait(hx_driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "btn_login.loginbox"))
    )
    login_button.click()

    # 等待遮罩层消失（假设类名为 .layui-layer-shade）
    try:
        WebDriverWait(hx_driver, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "layui-layer-shade"))
        )
    except:
        print("遮罩层未消失，可能影响后续操作")

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
def hx(path,file):
    order = Order()
    verification = Verification(hx_driver)
    verification.set_cookie()
    order_files = path + "/" + file
    orders = order.get_orders_from_file(order_files)
    print(file+"核销订单数量：", len(orders))
    for jd_account, jd_password in orders.items():
        # print("开始核销jd卡号：", jd_account, "卡密：", jd_password)
        verification.verification(jd_account, jd_password)
    verification.save_fail_summary(file)
def get_txt_files(directory):
    """
    获取指定目录下的所有txt文件名，并以数组形式返回。
    :param directory: 要搜索的目录路径。
    :return: 包含所有txt文件名的列表。
    """
    txt_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                # txt_files.append(os.path.join(root, file))
                txt_files.append(file)
    return txt_files
if __name__ == '__main__':
    date = input("请输入核销的订单日期(例如:2025-06-18),回车默认为前一天：")
    if not date:
        current_date = datetime.now()
        # 计算前一天的日期
        previous_day = current_date - timedelta(days=1)
        # 格式化输出为字符串（格式为YYYY-MM-DD）
        date = previous_day.strftime("%Y-%m-%d")
    hx_login("19155789001","Yuan970901")
    orders=get_txt_files(date)
    for order in orders:
        hx(date,order)