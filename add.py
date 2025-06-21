from database.database import Database

if __name__ == '__main__':
    db_file = 'accounts.db'  # 提前准备好数据库文件路径
    db = Database(db_file)

    accounts = []  # ✅ 改成 list 而不是 tuple

    with open('accounts.txt', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  # 跳过空行
            parts = line.split()
            if len(parts) >= 2:
                sc_account = parts[0]
                sc_password = parts[1]
                accounts.append((sc_account, sc_password))  # ✅ 使用 append 添加元素

    db.batch_insert_account(accounts)