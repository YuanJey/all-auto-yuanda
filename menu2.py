import sys

from database.accounts import SCAccount
from database.database import Database
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from prompt_toolkit import prompt
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style

KEY = b'YourKey123456789'
BLOCK_SIZE = 16


def aes_encrypt(plaintext: str) -> str:
    cipher = AES.new(KEY, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(plaintext.encode('utf-8'), BLOCK_SIZE))
    return base64.b64encode(ciphertext).decode('utf-8')


database = Database("accounts.db")


def init_account():
    hx_account = input("请输入核销账号：")
    hx_password = input("请输入核销密码：")
    database.insert_hx_account(hx_account, hx_password)


# ======================
# 菜单逻辑封装
# ======================

MENU_ITEMS = [
    "[0]. 导入商城账号",
    "[1]. 查看商城账号",
    "[2]. 新增商城账号",
    "[3]. 删除商城账号",
    "[4]. 设置核销账号",
    "[5]. 获取核销账号信息",
    "[6]. 查询失败金额",
    "[7]. 退出程序"
]


def show_menu_with_arrow(selected_index):
    lines = []
    for i, item in enumerate(MENU_ITEMS):
        if i == selected_index:
            lines.append(f"  > {item}")
        else:
            lines.append(f"    {item}")
    return '\n'.join(lines)


import os
import platform

def clear_screen():
    # 使用 ANSI 控制符清屏（不会触发新终端窗口）
    print('\033[H\033[J', end='')
# def clear_screen():
#     """跨平台清屏函数"""
#     system_name = platform.system()
#     if system_name == "Windows":
#         os.system('cls')
#     else:
#         os.system('clear')


def interactive_menu():
    index = [0]

    def get_text_fragments():
        lines = []
        for i, item in enumerate(MENU_ITEMS):
            if i == index[0]:
                lines.append(f"  > {item}")
            else:
                lines.append(f"    {item}")
        return [('', '\n'.join(lines))]

    text_control = FormattedTextControl(get_text_fragments)
    window = Window(content=text_control, dont_extend_height=True)
    layout = Layout(container=window)

    kb = KeyBindings()

    @kb.add('up')
    def _(event):
        index[0] = max(0, index[0] - 1)

    @kb.add('down')
    def _(event):
        index[0] = min(len(MENU_ITEMS) - 1, index[0] + 1)

    @kb.add('enter')
    def _(event):
        event.app.exit(result=index[0])

    style = Style.from_dict({
        '': '#ff0066',
    })

    while True:
        # 显示欢迎语 + 菜单
        clear_screen()
        print("\n🚀 欢迎使用自动化脚本管理系统 🚀\n")

        app = Application(layout=layout, key_bindings=kb, style=style, full_screen=False)
        result = app.run()

        clear_screen()  # 再次确认清屏，防止残留

        if result is not None:
            choice = str(result)
        else:
            choice = '7'

        # 执行菜单逻辑
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
            input("按回车键继续...")

        elif choice == "1":
            accounts = database.get_all_sc_account()
            print("\n====== 商城账号列表 ======\n")
            if not accounts:
                print("没有商城账号信息。\n")
            else:
                for account in accounts:
                    print(f"账号：{account.account}，密码：{account.password}")
            input("\n按回车键继续...")

        elif choice == "2":
            account = input("请输入商城账号：")
            password = input("请输入商城密码：")
            database.batch_insert_account([(account, password)])
            print("账号添加成功！")
            input("按回车键继续...")

        elif choice == "3":
            account = input("请输入要删除的商城账号：")
            database.del_account(account)
            print("账号删除成功！")
            input("按回车键继续...")

        elif choice == "4":
            init_account()
            print("核销账号设置完成！")
            input("按回车键继续...")

        elif choice == "5":
            hx_acc = database.get_hx_account()
            print("\n====== 核销账号信息 ======\n")
            if hx_acc:
                print(f"账号：{hx_acc.account}，密码：{hx_acc.password}")
            else:
                print("未设置核销账号。")
            input("\n按回车键继续...")

        elif choice == "6":
            day = input("请输入日期（格式 YYYY-MM-DD）：")
            fail_records = database.get_fail_summary(day)
            all_money = 0
            print(f"\n====== {day} 失败金额记录 ======\n")
            if not fail_records:
                print("没有失败的核销记录。\n")
            else:
                for record in fail_records:
                    print(f"账号：{record.account}，失败金额：{record.fail_money}")
                    all_money += record.fail_money
                print(f"\n总失败金额：{all_money}\n")
            input("按回车键继续...")

        elif choice == "7":
            sys.exit(0)  # 强制退出整个程序

        else:
            print("无效选项，请重新选择。")
            input("按回车键继续...")

        index[0] = 0  # 重置选中项




if __name__ == '__main__':
    interactive_menu()
