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

    def transfer(self,account,money):
        self.driver.get(self.url)
        # 等待元素出现（最多等待10秒）
        account_input = WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located((By.ID, 'account'))
        )
        account_input.clear()
        account_input.send_keys(account)
        money_input = WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located((By.ID, 'money'))
        )
        money_input.clear()
        money_input.send_keys(str(money))

        passwd_input = WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located((By.ID, 'passwd'))
        )
        passwd_input.clear()
        passwd_input.send_keys(str(money))
        wait = WebDriverWait(self.driver, 120)
        confirm_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="apply-footer-btn " and text()="确认转账"]'))
        )
        confirm_button.click()

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
            # buy.start2(2000)
            sc_accounts_state[sc_account.account]=buy.state
            # balance = user.get_balance()
            # if balance >= 30000:
            #     print(f"{sc_account.account} 金额：{balance},开始执行。")
            #     buy.start()
            # elif last_sc_account.account == sc_account.account:
            #     print(f"最后一个账号 {sc_account.account},金额：{balance} 开始执行。")
            #     buy.start2(int(balance))
            # else:
            #     print("余额小于配置金额,请手动充值。")


            # while True:
            #     balance = user.get_balance()
            #     # local_db.get_transfed_accounts()
            #     sc_account=local_db.get_order_account(account.account)
            #     # if buy.check_balance(balance):
            #     #     print("余额大于等于配置金额,即将开始执行。")
            #     #     break
            #     if sc_account.transfed:
            #         balance = user.get_balance()
            #         print(sc_account.account,"已转账","余额:",balance)
            #         break
            #     else:
            #         print("还未转账，等待充值...")
            #         time.sleep(20)
            # buy.start()
    finally:
        driver.quit()
def hx_login(account, password):
    hx_driver.get("https://hx.yuanda.biz/Home/Public/loginbox/type/2")
    # 等待输入框出现并输入手机号,password
    phone_input = WebDriverWait(hx_driver, 120).until(
        EC.presence_of_element_located((By.ID, "phone"))
    )
    phone_input.send_keys(account)
    password_input = WebDriverWait(hx_driver, 120).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_input.send_keys(password)
    login_button = WebDriverWait(hx_driver, 120).until(
        EC.element_to_be_clickable((By.ID, "login"))
    )
    login_button.click()
    input("完成后输入回车键：")
    hx_driver.get("https://hx.yuanda.biz")
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
    verification.save_fail_summary()
def to_money(sc_account, balance):
    transfer = Transfer(hx_driver, hx_account.password)
    print("商城账户：", sc_account.account, "余额：", balance)
    all_money = transfer.get_available_transfer_money()
    to_sc_account_money = 30000 - balance
    if all_money > to_sc_account_money:
        transfer.transfer2(sc_account.account, to_sc_account_money)
    elif last_sc_account.account==sc_account.account:
        rounded_money = (all_money // 100) * 100
        if rounded_money>=100:
            transfer.transfer2(sc_account.account, rounded_money)
    else:
        print(
            f"账户余额不足 可转账金额 {all_money} 小于配置金额 {30000 - balance}，请手动充值。")

# 在全局作用域中定义一个锁
global_transfer_lock = threading.Lock()

def to_money_lock(sc_account, balance):
    """
    向商城账号充值至 30000 元，最多转不超过可转账额度的最大 100 的整数倍金额。
    使用锁保护对「全局可转账金额」的访问。

    :param sc_account: 商城账号对象
    :param balance: 当前余额（float 或 int）
    :return: bool - 是否成功完成转账
    """
    account = sc_account.account
    transfer = Transfer(hx_driver, hx_account.password)

    print(f"【开始转账】商城账户：{account}，当前余额：{balance}")

    with global_transfer_lock:  # 加锁，防止多个线程同时读取可转账金额
        all_money = transfer.get_available_transfer_money()
        required = max(0, 30000 - balance)

        if all_money >= required:
            print(f"✅ 可转账金额 {all_money} ≥ 需要金额 {required}，全额转账 {required}")
            result = transfer.transfer2(account, required)
        else:
            rounded_money = (all_money // 100) * 100
            if rounded_money >= 100:
                print(f"🟡 账户余额不足，仅转账最大 100 倍数金额：{rounded_money}")
                result = transfer.transfer2(account, rounded_money)
            else:
                print("❌ 可转账金额不足 100，跳过。")
                result = False

    return result

def to_money1(sc_account, balance):
    """
    向商城账号充值至 30000 元，最多转不超过可转账额度的最大 100 的整数倍金额。

    :param sc_account: 商城账号对象
    :param balance: 当前余额（float 或 int）
    :return: bool - 是否成功完成转账
    """
    transfer = Transfer(hx_driver, hx_account.password)
    print(f"【开始转账】商城账户：{sc_account.account}，当前余额：{balance}")

    all_money = transfer.get_available_transfer_money()
    required = max(0, 30000 - balance)

    if all_money >= required:
        print(f"✅ 可转账金额 {all_money} ≥ 需要金额 {required}，全额转账 {required}")
        return transfer.transfer2(sc_account.account, required)
    else:
        rounded_money = (all_money // 100) * 100
        if rounded_money >= 100:
            return transfer.transfer2(sc_account.account, rounded_money)
        else:
            print("❌ 可转账金额不足 100，跳过。")
            return False


lock = threading.Lock()
def to_money2(sc_account, balance):
    transfer = Transfer(hx_driver, hx_account.password)
    print("商城账户：", sc_account.account, "余额：", balance)
    wait_timeout = 60 * 1  # 最大等待时间（秒）
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
    enc = input("请输入授权码：")
    hx_account=db.get_hx_account()
    dec = aes_encrypt(hx_account.account)
    if dec != enc and hx_account.account != "19155789001":
        print("授权码错误")
        exit()
    # max_work_input = input("请输入同时处理账号数量(根据自己电脑配置和网络选择1-6)：")
    # try:
    #     max_work = int(max_work_input)
    #     if not (1 <= max_work <= 6):  # 限制范围
    #         print("输入超出范围，默认使用 2")
    #         max_work = 2
    # except ValueError:
    #     print("输入无效，默认使用 2")
    #     max_work = 2
    max_work = 3
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
    # for account in accounts:
    #     process_account(account,date,db_file)
    # 设置最大并发线程数
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
        if state <= 1:
            log.add(hx_account.account, account)
        db.insert_sc_account_state(account, state)

