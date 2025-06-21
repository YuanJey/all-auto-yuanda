import os
from datetime import datetime, timedelta


class Order:
    def __init__(self):
        pass

    def get_order_files(self,date):
        # current_date = datetime.now()
        # # 计算前一天的日期
        # previous_day = current_date - timedelta(days=1)
        # # 格式化输出为字符串（格式为YYYY-MM-DD）
        # file_path = previous_day.strftime("%Y-%m-%d")
        file_path = date
        if not os.path.exists(file_path) or not os.path.isdir(file_path):
            print(f"路径 {file_path} 不存在或不是文件夹")
            return []
        txt_files = [os.path.join(file_path, f) for f in os.listdir(file_path) if f.endswith('.txt')]
        return txt_files
    def get_orders_from_file(self,file_path):
        account_password_map = {}
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue  # 跳过空行
                parts = line.split()
                if len(parts) >= 2:
                    jd_account = parts[0]
                    jd_password = parts[1]
                    account_password_map[jd_account] = jd_password
        return account_password_map