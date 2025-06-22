from database.accounts import SCAccount
from database.database import Database
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64

KEY = b'YourKey123456789'  # 必须是 16、24 或 32 字节长度
BLOCK_SIZE = 16  # AES block size

def aes_encrypt(plaintext: str) -> str:
    cipher = AES.new(KEY, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(plaintext.encode('utf-8'), BLOCK_SIZE))
    return base64.b64encode(ciphertext).decode('utf-8')

database = Database("accounts.db")
def init_account():
    hx_account = input("请输入核销账号：")
    hx_password = input("请输入核销密码：")
    database.insert_hx_account(hx_account, hx_password)

if __name__ == '__main__':
    while True:
        print("===============================================")
        # 提示用户选择操作
        choice = input(
            "0.导入商城账号\n"
            "1.设置核销账号\n"
            "2.获取核销账号信息\n"
            "3.新增商城账号\n"
            "4.删除商城账号\n"
            "5.查看商城账号\n"
            "其他任意键退出..."
            "\n"
        )
        if choice == "0":
            accounts = []
            with open('accounts.txt', 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        accounts.append((parts[0], parts[1]))

            print(f"共读取了{len(accounts)}行账号信息")

            database.batch_insert_account(accounts)
            continue
        if choice == "1":
            init_account()
            continue
        if choice == "2":
            account = database.get_hx_account()
            print("当前核销账号信息：", account.account, account.password)
            continue
        if choice == "3":
            account = input("请输入商城账号：")
            password = input("请输入商城密码：")
            accounts= [(account, password)]
            database.batch_insert_account(accounts)
            continue
        if choice == "4":
            account = input("请输入要删除的商城账号：")
            database.del_account(account)
            continue
        if choice == "5":
            accounts = database.get_all_sc_account()
            if not accounts:
                print("没有商城账号信息。")
            else:
                for account in accounts:
                    print("账号：", account.account, "密码：", account.password)
            continue
        if choice == "6":
            day = input("请输入日期：")
            fild_money=database.get_fail_summary( day)
            all_money=0
            if not fild_money:
                print("没有失败的核销记录。")
            else:
                for account in fild_money:
                    print("账号：", account.account, "失败金额：", account.fail_money)
                    all_money+=account.fail_money
            print("总失败金额：", all_money)
            continue
        else:
            print("程序已退出。")
            break
