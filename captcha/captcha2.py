import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha.code import Code


class Captcha2(Code):
    def __init__(self,driver,api_key):
        self.driver = driver
        self.api_key = api_key
        pass
    def get_captcha_base64(self):
        try:
            # 等待验证码图片可见
            veriimg = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'veriimg'))
            )
            # 直接获取图片的 base64 编码
            base64_image = veriimg.screenshot_as_base64
            return base64_image
        except Exception as e:
            print('获取验证码 base64 失败:', e)
            return None

    def get_code_from_base64(self, base64_image):
        try:
            # 上传到2Captcha
            data = {
                'numeric':1,#  数字验证码
                'key': self.api_key,
                'method': 'base64',
                'body': base64_image,
                'json': 1,
                'min_length': 4,
                'max_length': 4
            }
            response = requests.post(
                'https://2captcha.com/in.php',
                data=data
            )
            upload_result = response.json()

            if upload_result['status'] != 1:
                print('上传验证码失败:', upload_result['request'])
                return None

            captcha_id = upload_result['request']
            # print('上传成功，任务ID:', captcha_id)
            # return self.get_captcha_result(captcha_id)
            return captcha_id
        except Exception as e:
            print('上传验证码失败:', e)
            return None

    def get_captcha_result(self,base64_image):
        captcha_id=self.get_code_from_base64(base64_image)
        fetch_url = f'https://2captcha.com/res.php?key={self.api_key}&action=get&id={captcha_id}&json=1'
        for i in range(60):
            time.sleep(2)
            try:
                res_response = requests.get(fetch_url)
                res_json = res_response.json()
                if res_json['status'] == 1:
                    print('识别结果:', res_json['request'])
                    return res_json['request']
                elif res_json['request'] == 'CAPCHA_NOT_READY':
                    print('验证码还在识别中，等待中...')
                else:
                    print('识别失败:', res_json['request'])
                    return None
            except requests.RequestException as e:
                print(f'请求错误: {e}')
                return None
        print('超时未获得识别结果')
        return None
