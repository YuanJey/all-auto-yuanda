import threading
import time

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database.database import Database
from selenium.webdriver.chrome.options import Options
from buy.buy import Buy
from order.order import Order
from user.user import User
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from verification.verification import Verification
from admin.log import Log
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

KEY = b'YourKey123456789'  # 必须是 16、24 或 32 字节长度
BLOCK_SIZE = 16  # AES block size
db_file = 'accounts.db'  # 提前准备好数据库文件路径
hx_driver = webdriver.Chrome()
db = Database(db_file)
last_sc_account=db.get_last_sc_account()
fail_money_map = {}
sc_accounts_state = {}
def aes_encrypt(plaintext: str) -> str:
    cipher = AES.new(KEY, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(plaintext.encode('utf-8'), BLOCK_SIZE))
    return base64.b64encode(ciphertext).decode('utf-8')

class Transfer:
    def __init__(self, driver,password):
        self.driver = driver
        self.password=password
        self.url="https://hx.yuanda.biz/Home/User/tomall"

    def transfer2(self, account, money):
        url = "https://hx.yuanda.biz/Home/User/tomall_apply"

        # 构造表单数据
        data = {
            'money': str(money),
            'account': account,
            'passwd': self.password
        }
        cookies = self.driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        try:
            response = requests.post(url, data=data,cookies=cookie_dict)
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None
    def get_available_transfer_money(self):
        self.driver.get(self.url)
        wait = WebDriverWait(self.driver, 60)
        # 定位到包含可转账金额的 span
        available_money_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//span[text()="可转账金额："]/following-sibling::span[1]'))
        )
        money_text = available_money_element.text.strip()
        try:
            return float(money_text)
        except ValueError:
            print(f"无法解析可转账金额: {money_text}")
            return 0.0
def process_account(sc_account, date):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 开启无头模式
    driver = webdriver.Chrome(options=chrome_options)
    try:
        user = User(driver, sc_account.account, sc_account.password)
        if user.login():
            user.download_order(date)
            hx(date, sc_account.account)
            balance = user.get_balance()
            fail_money_map[sc_account.account]= balance
            to_money2(sc_account, balance)
            buy = Buy(driver)
            balance = user.get_balance()
            buy.start2(int(balance))
            sc_accounts_state[sc_account.account]=buy.state
    finally:
        driver.quit()
def hx_login(account, password):
    hx_driver.get("https://hx.yuanda.biz")  # 访问目标网址

    login_button = WebDriverWait(hx_driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "btn_login.loginbox"))
    )
    login_button.click()

    # 等待遮罩层消失（假设类名为 .layui-layer-shade）
    try:
        WebDriverWait(hx_driver, 60).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "layui-layer-shade"))
        )
    except:
        print("遮罩层未消失，可能影响后续操作")

    iframe = WebDriverWait(hx_driver, 60).until(
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
            WebDriverWait(hx_driver, 10).until(
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
    order_files = path + "/" + file + ".txt"
    orders = order.get_orders_from_file(order_files)
    print(file+"核销订单数量：", len(orders))
    for jd_account, jd_password in orders.items():
        # print("开始核销jd卡号：", jd_account, "卡密：", jd_password)
        verification.verification(jd_account, jd_password)
    verification.save_fail_summary(file)

lock = threading.Lock()
def to_money2(sc_account, balance):
    transfer = Transfer(hx_driver, hx_account.password)
    print("商城账户：", sc_account.account, "余额：", balance)
    wait_timeout = 60 * 3  # 最大等待时间（秒）
    wait_interval = 5  # 检查间隔（秒）
    start_time = time.time()
    with lock:
        while True:
            all_money = transfer.get_available_transfer_money()
            to_sc_account_money = 30000 - balance
            if all_money > to_sc_account_money:
                transfer.transfer2(sc_account.account, to_sc_account_money)
                break
            elif last_sc_account.account == sc_account.account:
                rounded_money = (all_money // 100) * 100
                if rounded_money >= 100:
                    transfer.transfer2(sc_account.account, rounded_money)
                break
            else:
                print(
                    f"账户余额不足 可转账金额 {all_money} 小于配置金额 {30000 - balance}，等待核销充值...")
                if time.time() - start_time > wait_timeout:
                    rounded_money = (all_money // 100) * 100
                    if rounded_money >= 100:
                        transfer.transfer2(sc_account.account, rounded_money)
                        break
                    else:
                        print(f"等待超时，未满足转账条件: {sc_account.account}")
                        break
                time.sleep(wait_interval)

if __name__ == '__main__':
    # enc = input("请输入授权码：")
    hx_account=db.get_hx_account()
    dec = aes_encrypt(hx_account.account)
    if dec != hx_account.key:
        print("授权码错误")
        exit()
    max_work_input = input("请输入同时处理账号数量(根据自己电脑配置和网络选择1-6)：")
    try:
        max_work = int(max_work_input)
        if not (1 <= max_work <= 6):  # 限制范围
            print("输入超出范围，默认使用 2")
            max_work = 2
    except ValueError:
        print("输入无效，默认使用 2")
        max_work = 2
    # max_work = 1
    date = input("请输入核销的订单日期(例如:2025-06-18),回车默认为前一天：")
    if not date:
        current_date = datetime.now()
        # 计算前一天的日期
        previous_day = current_date - timedelta(days=1)
        # 格式化输出为字符串（格式为YYYY-MM-DD）
        date = previous_day.strftime("%Y-%m-%d")

    db.init_sc_accounts_state()
    accounts = db.get_all_sc_account()
    hx_account=db.get_hx_account()
    count=len(accounts)
    hx_login(hx_account.account, hx_account.password)

    with ThreadPoolExecutor(max_workers=max_work) as executor:
        futures = [
            executor.submit(process_account, account, date)
            for account in accounts
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"发生异常: {e}")

    log = Log()
    for account, fild_money in fail_money_map.items():
        db.insert_fail_summary(account, fild_money)
    for account, state in sc_accounts_state.items():
        try:
            if state <= 1:
                log.add(hx_account.account, account)
            db.insert_sc_account_state(account, state)
        except Exception as e:
            print(f"发生异常: {e}")

