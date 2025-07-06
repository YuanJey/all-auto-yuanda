import json

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha.code import Code


class Yescaptcha(Code):
    def __init__(self, driver, api_key):
        self.driver = driver
        self.api_key = api_key
    def get_captcha_base64(self):
        try:
            # 等待验证码图片可见
            veriimg = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'veriimg'))
            )
            # 直接获取图片的 base64 编码
            base64_image = veriimg.screenshot_as_base64
            return base64_image
        except Exception as e:
            print('获取验证码 base64 失败:', e)
            return None

    def get_captcha_result(self, base64_image):
        """
               使用 https://cn.yescaptcha.com 同步识别验证码（base64 输入）
               :param base64_image: 验证码图片的 base64 编码
               :return: 识别结果字符串或 None
               """
        url = "https://cn.yescaptcha.com/createTask"
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "ImageToTextTaskMuggle",
                "body": f"data:image/png;base64,{base64_image}"
            }
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()

            if result.get("errorId") == 0 and result.get("status") == "ready":
                solution = result.get("solution", {})
                captcha_text = solution.get("text")
                print('识别结果:', captcha_text)
                return captcha_text
            else:
                error_desc = result.get("errorDescription", "未知错误")
                print("识别失败:", error_desc)
                return None
        except requests.RequestException as e:
            print("请求失败:", e)
            return None