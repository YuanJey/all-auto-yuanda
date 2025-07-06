import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta


class Verification:
    def __init__(self, driver):
        self.driver = driver
        self.url = 'https://hx.yuanda.biz/Home/Card/writeOffCard'
        self.cookie = None
        # 新增：记录卡密核销成功次数
        self.fail_count = {}

    def set_cookie(self):
        """获取cookie"""
        cookies = self.driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        self.cookie = cookie_dict

    def verification_lod(self, jd_account, jd_password):
        # 自定义请求头
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # 要发送的数据
        data = {
            'cardkey': jd_account,
            'cardpwd': jd_password,
            'cardid': '351',
            'priceid': '2846',
            'typeid': '109',
        }

        try:
            response = requests.post(self.url, headers=headers, cookies=self.cookie, data=data)
            if response.status_code == 200:
                resp = response.json()
                status = resp.get('status')
                info = resp.get('info')
                if status != 1:
                    print(f"[失败] 核销失败: {info} - {jd_account}")
                    self.fail_count[jd_account] = jd_password
            else:
                print(f"[错误] 请求失败，状态码: {response.status_code} - {jd_account}")
                self.fail_count[jd_account] = jd_password
        except Exception as e:
            print(f"[异常] 核销出错: {e} - {jd_account}")
            self.fail_count[jd_account] = jd_password

    def verification(self, jd_account, jd_password):
        # 自定义请求头
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # 要发送的数据
        data = {
            'cardkey': jd_account,
            'cardpwd': jd_password,
            'cardid': '351',
            'priceid': '2846',
            'typeid': '109',
        }

        max_retries = 10
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = requests.post(self.url, headers=headers, cookies=self.cookie, data=data)
                if response.status_code == 200:
                    resp = response.json()
                    status = resp.get('status')
                    info = resp.get('info')
                    if status != 1:
                        print(f"[失败] 核销失败: {info} - {jd_account}")
                    else:
                        # print(f"[成功] 核销成功 - {jd_account}")
                        return True  # 成功直接返回
                else:
                    print(f"[错误] 请求失败，状态码: {response.status_code} - {jd_account}")
            except (requests.ConnectionError, requests.Timeout) as e:
                print(f"[网络异常] 第 {retry_count + 1} 次重试: {e} - {jd_account}")
                time.sleep(2)  # 延迟重试
                continue
            except Exception as e:
                print(f"[不可恢复异常] 核销出错: {e} - {jd_account}")
                break
            finally:
                retry_count += 1

        # 所有重试都失败后，保存失败订单
        print(f"[最终失败] 已达最大重试次数，仍失败 - {jd_account}")
        self.fail_count[jd_account] = jd_password
        return False


    def run_verification_for_pair(self, jd_account, jd_password, repeat=1):
        """对一组卡密并发执行核销多次"""
        key = (jd_account, jd_password)
        print(f"开始并发核销卡密: {key}，共 {repeat} 次")
        with ThreadPoolExecutor(max_workers=5) as executor:
            for i in range(repeat):
                executor.submit(self.verification, jd_account, jd_password)

    def save_fail_summary(self,acc):
        """将卡密核销成功次数保存到文件"""
        # 获取前一天日期作为文件名
        previous_day = datetime.now().date() - timedelta(days=1)
        filename = f"{previous_day}_fail_order.txt"
        # 自动创建目录（例如 logs/）
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)  # 递归创建目录
        file_path = os.path.join(log_dir, filename)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"===商城号:{acc} 核销统计时间: {timestamp} ===\n")
            for account, password in self.fail_count.items():
                line = f"{account} {password}\n"
                # print(line.strip())  # 控制台输出
                f.write(line)
            f.write("========================\n\n")


