from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class  Buy:
    def __init__(self, driver):
        self.driver = driver
        self.num100 = 20
        self.num200 = 10
        self.num500 = 12
        self.num1000 = 12
        self.num2000 = 4
        self.amount=  self.num100*100+self.num200*200+self.num500*500+self.num1000*1000+self.num2000*2000
        self.m_100 = 'https://sc.yuanda.biz/pg/234.html'
        self.m_200 = 'https://sc.yuanda.biz/pg/235.html'
        self.m_500 = 'https://sc.yuanda.biz/pg/237.html'
        self.m_1000 = 'https://sc.yuanda.biz/pg/240.html'
        self.m_2000 = 'https://sc.yuanda.biz/pg/241.html'
        pass

    def check_balance(self,balance):
        if balance >= self.amount:
            print(f"余额: {balance} 配置金额为: {self.amount}, 可以开始购买。")
            return True
        else:
            print(f"余额: {balance} 配置金额为: {self.amount}, 不足，请充值。")
            return False
    def start(self):
        for i in range(self.num100):
            self.handle(100)
        for i in range(self.num200):
            self.handle(200)
        for i in range(self.num500):
            self.handle(500)
        for i in range(self.num1000):
            self.handle(1000)
        for i in range(self.num2000):
            self.handle(2000)

    def start2(self, money):
        if money % 100 != 0:
            print("金额必须是 100 的倍数")
            return

        # 定义面额和对应的数量限制
        denominations = [
            (2000, 4),
            (1000, 12),
            (500, 12),
            (200, 10),
            (100, 20)
        ]

        # 如果金额正好是 30000，使用固定策略
        if money == 30000:
            self.start()
            return
        remaining = money

        for amount, limit in denominations:
            count = min(remaining // amount, limit)
            for _ in range(count):
                self.handle(amount)
            remaining -= count * amount
            if remaining == 0:
                break

        if remaining != 0:
            print(f"无法完全消费金额，剩余: {remaining}")

    def handle(self,number):
        url= None
        if  number == 100:
            url = self.m_100
        elif number == 200:
            url = self.m_200
        elif number == 500:
            url = self.m_500
        elif number == 1000:
            url = self.m_1000
        elif number == 2000:
            url = self.m_2000
        try:
            self.driver.get(url)
            buy_button = WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cart-buy > a.buy-btn'))
            )
            # 使用JavaScript点击
            self.driver.execute_script("arguments[0].click();", buy_button)

            # 找“找人代付”并点击
            pay_button = WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.ID, 'alipay'))
            )
            self.driver.execute_script("arguments[0].click();", pay_button)

            # 点击结算按钮
            submit_btn = WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.ID, 'jiesuan'))
            )
            # 使用JavaScript点击
            self.driver.execute_script("arguments[0].click();", submit_btn)

            success_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, 'zhengwen'))
            )
            message_text = success_message.text
            print("成功信息：", message_text,number, "面额购买成功+1")
        except Exception as e:
            print(f"操作失败：{e}", "金额:", number)