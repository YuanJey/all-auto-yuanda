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
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64

KEY = b'YourKey123456789'  # 必须是 16、24 或 32 字节长度
BLOCK_SIZE = 16  # AES block size
db_file = 'accounts.db'  # 提前准备好数据库文件路径
hx_driver = webdriver.Chrome()
db = Database(db_file)
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
        account_input = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, 'account'))
        )
        account_input.clear()
        account_input.send_keys(account)
        money_input = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, 'money'))
        )
        money_input.clear()
        money_input.send_keys(str(money))

        passwd_input = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, 'passwd'))
        )
        passwd_input.clear()
        passwd_input.send_keys(str(money))
        wait = WebDriverWait(self.driver, 60)
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
            # db.insert_fail_summary(sc_account.account, balance)
            to_money(sc_account, balance)
            buy = Buy(driver)
            balance = user.get_balance()
            if balance >= 30000:
                print("余额大于等于配置金额,即将开始执行。")
                buy.start()
            else:
                print("余额小于配置金额,请手动充值。")
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
    input("完成后输入回车键：")
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
    to_money = 30000 - balance
    if all_money > to_money:
        transfer.transfer2(sc_account.account, to_money)
    else:
        print(
            f"账户余额不足 可转账金额 {all_money} 小于配置金额 {30000 - balance}，请手动充值。")
if __name__ == '__main__':
    enc = input("请输入授权码：")
    hx_account=db.get_hx_account()
    dec = aes_encrypt(hx_account.account)
    if dec != enc:
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
    date = input("请输入核销的订单日期(例如:2025-06-18),回车默认为前一天：")
    if not date:
        current_date = datetime.now()
        # 计算前一天的日期
        previous_day = current_date - timedelta(days=1)
        # 格式化输出为字符串（格式为YYYY-MM-DD）
        date = previous_day.strftime("%Y-%m-%d")

    accounts = db.get_all_sc_account()
    hx_account=db.get_hx_account()
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
