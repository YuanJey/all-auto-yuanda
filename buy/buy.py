from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class  Buy:
    def __init__(self,driver):
        self.driver = driver
        self.num100 = 20
        self.num200 = 10
        self.num500 = 12
        self.num1000 = 12
        self.num2000 = 4
        # self.num100 = 20
        # self.num200 = 10
        # self.num500 = 16
        # self.num1000 = 16
        # self.num2000 = 1
        self.amount=  self.num100*100+self.num200*200+self.num500*500+self.num1000*1000+self.num2000*2000
        self.m_100 = 'https://sc.yuanda.biz/pg/234.html'
        self.m_200 = 'https://sc.yuanda.biz/pg/235.html'
        self.m_500 = 'https://sc.yuanda.biz/pg/237.html'
        self.m_1000 = 'https://sc.yuanda.biz/pg/240.html'
        self.m_2000 = 'https://sc.yuanda.biz/pg/241.html'
        self.state= 0
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
        """
        根据指定金额尝试下单，优先使用大面额，支持向下取整至最近的 100 整数倍。

        :param money: 目标金额（可为任意整数）
        :return: None
        """
        if money < 100:
            print("金额太小，无法下单")
            return

        # 自动向下取整到最近的 100 的整数倍
        rounded_money = (money // 100) * 100
        if rounded_money != money:
            print(f"⚠️ 输入金额 {money} 非 100 的整数倍，已自动调整为：{rounded_money}")

        # 定义面额和对应的数量限制
        # denominations = [
        #     (2000, 1),
        #     (1000, 16),
        #     (500, 16),
        #     (200, 10),
        #     (100, 20)
        # ]
        denominations = [
            (2000, 4),
            (1000, 12),
            (500, 12),
            (200, 10),
            (100, 20)
        ]

        # 如果金额正好是 30000，使用固定策略
        if rounded_money == 30000:
            self.start()
            self.state = 1
            return

        remaining = rounded_money

        for amount, limit in denominations:
            count = min(remaining // amount, limit)
            for _ in range(count):
                state=self.handle2(amount)
                if state==-1:
                    self.state = -1
                    return
                elif state==1:
                    self.state = 1
                    return
                elif state == -2:
                    self.state = -2
            remaining -= count * amount
            if remaining == 0:
                break

        if remaining != 0:
            print(f"无法完全消费金额，剩余: {remaining}")


    def handle(self, number):
        url = None
        if number == 100:
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
            buy_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cart-buy > a.buy-btn'))
            )
            # 使用JavaScript点击
            self.driver.execute_script("arguments[0].click();", buy_button)

            # 找“找人代付”并点击
            pay_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, 'alipay'))
            )
            self.driver.execute_script("arguments[0].click();", pay_button)

            # 点击结算按钮
            submit_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, 'jiesuan'))
            )
            # 使用JavaScript点击
            self.driver.execute_script("arguments[0].click();", submit_btn)

            success_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, 'zhengwen'))
            )
            message_text = success_message.text
            print("成功信息：", message_text, number, "面额购买成功+1")
        except Exception as e:
            print(f"操作失败：{e}", "金额:", number)

    def handle2(self, number):
        url = None
        if number == 100:
            url = self.m_100
        elif number == 200:
            url = self.m_200
        elif number == 500:
            url = self.m_500
        elif number == 1000:
            url = self.m_1000
        elif number == 2000:
            url = self.m_2000
        else:
            print(f"不支持的面额: {number}")
            return None

        try:
            self.driver.get(url)
            # 等待购买按钮并点击
            buy_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cart-buy > a.buy-btn'))
            )
            self.driver.execute_script("arguments[0].click();", buy_button)

            # 等待支付按钮并点击
            pay_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, 'alipay'))
            )
            self.driver.execute_script("arguments[0].click();", pay_button)

            # 等待结算按钮并点击
            submit_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, 'jiesuan'))
            )
            self.driver.execute_script("arguments[0].click();", submit_btn)

            # 检查是否进入成功页面
            success_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, 'zhengwen'))
            )
            success_text = success_message.text
            print("成功信息：", success_text, number, "面额购买成功+1")
            return  0
        except Exception as e:
            try:
                layer = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'layui-layer-content')),
                )
                if layer and "余额不足" in layer.text:
                    print(f"弹窗提示：{layer.text}")
                    return -1
                if "您今天的下单金额已超过三万" in layer.text:
                    print(f"{number} 超过3w")
                    return 1
            except Exception as e:
                print(f"操作失败：{e},金额: {number}")
                return None
            return -2

