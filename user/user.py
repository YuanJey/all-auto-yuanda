import os

import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from captcha.captcha import Captcha
from datetime import datetime, timedelta
from pathlib import Path


class  User:
    def __init__(self, driver,account, password):
        self.account = account
        self.password = password
        self.driver = driver
        self.cookie=  self
        pass

    def get_cookie(self):
        """获取cookie"""
        cookies = self.driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        self.cookie = cookie_dict
        return cookie_dict
    def login(self):
        self.driver.get('https://sc.yuanda.biz/')

        try:
            # 点击登录按钮
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div//ul//li//a[text()="登录"]'))
            )
            login_btn.click()
            # 循环处理验证码
            retry_count = 0
            while True:
                print(f"尝试登录第 {retry_count + 1} 次...")
                try:
                    # 等待验证码图片出现
                    code=Captcha(self.driver,self.account,"4f7fe23e7cd68680a6b320982be0a1c9")
                    base64_img=code.get_captcha_base64()
                    captcha_code = code.get_code_from_base64(base64_img)
                    if captcha_code:
                        print('识别到验证码:', captcha_code)
                        # 输入验证码
                        veri_input = self.driver.find_element(By.ID, 'veri')
                        veri_input.send_keys(captcha_code)
                        # 输入账号
                        account_input = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.ID, 'account'))
                        )
                        account_input.send_keys(self.account)
                        #  输入密码
                        password_input = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.ID, 'password'))
                        )
                        password_input.send_keys(self.password)
                        login_button = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.ID, 'loginbtn'))
                        )
                        login_button.click()
                        if WebDriverWait(self.driver, 10).until(
                                lambda d: d.current_url == 'https://sc.yuanda.biz/jingdian/user/uscenter.html'
                        ):
                            self.get_cookie()
                            return True
                        else:
                            print('登录失败，页面未跳转。刷新重试...')
                            self.driver.refresh()
                    else:
                        print('验证码识别失败，刷新页面重试...')
                        self.driver.refresh()
                        retry_count += 1
                except Exception as e:
                    print(f"验证码处理异常: {e}")
                    self.driver.refresh()
                    retry_count += 1
        except Exception as e:
            print(f"登录过程发生严重错误: {e}")
            return False

    def download_order(self,date):
        """下载文件"""
        # current_date = datetime.now()
        # 计算前一天的日期
        # previous_day = current_date - timedelta(days=1)
        # 格式化输出为字符串（格式为YYYY-MM-DD）
        # previous_day_str = previous_day.strftime("%Y-%m-%d")
        previous_day_str = date
        directory = Path(previous_day_str)
        # 创建目录（包括所有必要的父目录）
        directory.mkdir(parents=True, exist_ok=True)
        save_path = previous_day_str + "/" + self.account + ".txt"
        url = f"https://sc.yuanda.biz/jingdian/index/export.html?start={previous_day_str}&end="
        # https://sc.yuanda.biz/jingdian/index/export.html?start=2025-06-02&end=
        cookie=self.get_cookie()
        try:
            response = requests.get(url, cookies=cookie, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                print(f"订单文件已下载到: {save_path}")
            else:
                print(f"下载失败，状态码: {response.status_code}")
        except requests.RequestException as e:
            print(f"下载错误: {e}")

    # 获取余额 <span class="corg">0.00 元</span>
    def get_balance1(self):
        """获取账户余额"""
        url = 'https://sc.yuanda.biz/jingdian/User/usCenter.html'
        self.driver.get(url)
        # 等待元素出现（最多等待10秒）
        wait = WebDriverWait(self.driver, 60)
        balance_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'corg'))
        )
        # 获取余额文本 '0.00 元'
        balance_text = balance_element.text
        balance_text = balance_text.replace('元', '').strip()
        balance_text = balance_text.replace(',', '')
        balance_text = float(balance_text)
        return balance_text

    def get_balance(self):
        """获取账户余额，定位到 span.corg，并在失败时刷新页面重试"""
        url = 'https://sc.yuanda.biz/jingdian/User/usCenter.html'
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            try:
                self.driver.get(url)
                wait = WebDriverWait(self.driver, 60)

                # 使用更明确的 CSS_SELECTOR 定位 span.corg
                balance_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span.corg'))
                )

                balance_text = balance_element.text.replace('元', '').strip().replace(',', '')
                return float(balance_text)

            except Exception as e:
                print(f"获取余额失败（第 {retry_count + 1} 次重试）: {e}")
                retry_count += 1
                self.driver.refresh()

        print("无法获取账户余额，请检查网络或页面结构是否发生变化。")
        return 0.0

    def init_balance_file(self,ctx):
        date = datetime.now() - timedelta(days=1)
        current_date = date.strftime("%Y-%m-%d")
        filename = f"{current_date}_{ctx}_balance.txt"
        if not os.path.exists(filename):
            try:
                with open(filename, 'w') as f:
                    pass  # 创建空文件
            except Exception as e:
                print(f"创建文件失败: {e}")
    def save_balance_to_file(self,ctx):
        self.init_balance_file(ctx)
        k = self.account
        v = self.get_balance()
        date = datetime.now() - timedelta(days=1)
        current_date = date.strftime("%Y-%m-%d")
        filename = f"{current_date}_{ctx}_balance.txt"
        try:
            with open(filename, 'a') as f:  # a 表示追加模式
                f.write(f"{k}\t{v}\n")
        except Exception as e:
            print(f"写入文件失败: {e}")

