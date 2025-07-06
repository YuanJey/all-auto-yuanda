import sqlite3
from datetime import datetime

from database.accounts import SCAccount, HXAccount, SCFailSummary, SCAccountState


class Database:
    def __init__(self, db_file):
        # current_date = datetime.now()
        # day = current_date.strftime("%Y-%m-%d")
        # self.conn = sqlite3.connect("./db/"+day+"_"+db_file)
        self.conn = sqlite3.connect(db_file)
        self.conn.execute('PRAGMA journal_mode=WAL;')
        self.cursor = self.conn.cursor()
        self.create_table()
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sc_accounts (
                account TEXT PRIMARY KEY,
                password TEXT,
                login BOOLEAN
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sc_accounts_state (
                account TEXT PRIMARY KEY,
                state INT,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
             CREATE TABLE IF NOT EXISTS hx_accounts(
                type INTEGER PRIMARY KEY,
                account TEXT NOT NULL UNIQUE,
                password TEXT,
                key TEXT)
        ''')
        ##每天失败金额统计
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sc_fail_summary (
                account TEXT PRIMARY KEY,
                fail_money REAL,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def init_sc_accounts_state(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
                            DELETE
                            FROM sc_accounts_state
                            WHERE update_time < DATE(?)
                            ''', (today,))
        self.conn.commit()

    def insert_sc_account_state(self, account, state):
        now = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
            INSERT OR REPLACE INTO sc_accounts_state (account, state, update_time) VALUES (?, ?, ?)
        ''', (account, state, now))  # 添加了 now 作为第三个参数
        self.conn.commit()

    def get_sc_accounts_by_state(self, state):
        """
        根据状态获取账户列表

        :param state: int, 要查询的状态值
        :return: list of tuples (account, state, update_time)
        """
        self.cursor.execute('''
                            SELECT account, state, update_time
                            FROM sc_accounts_state
                            WHERE state = ?
                            ORDER BY update_time DESC
                            ''', (state,))
        rows = self.cursor.fetchall()
        return [SCAccountState(*row) for row in rows]

    #插入失败金额账号
    def insert_fail_summary(self, account, fail_money):
        now = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
            INSERT OR REPLACE INTO sc_fail_summary (account, fail_money, update_time)
            VALUES (?, ?, ?)
        ''', (account, fail_money, now))
        self.conn.commit()

    def get_fail_summary(self, update_date):
        """
        获取指定日期的失败金额记录（忽略时间部分）

        :param update_date: str, 格式 "YYYY-MM-DD"
        :return: list of SCFailSummary
        """
        self.cursor.execute('''
                            SELECT *
                            FROM sc_fail_summary
                            WHERE DATE (update_time) = ?
                            ''', (update_date,))
        rows = self.cursor.fetchall()
        return [SCFailSummary(*row) for row in rows]

    def batch_insert_account(self, accounts):
        self.cursor.executemany('INSERT OR REPLACE INTO sc_accounts (account, password) VALUES (?, ?)', accounts)
        self.conn.commit()
    def del_account(self, account):
        self.cursor.execute('DELETE FROM sc_accounts WHERE account = ?', (account,))
        self.conn.commit()
    def get_all_sc_account(self):
        self.cursor.execute('SELECT * FROM sc_accounts  ORDER BY account ASC')
        rows = self.cursor.fetchall()
        accounts = [SCAccount(*row) for row in rows]
        return accounts

    def get_last_sc_account(self):
        self.cursor.execute('SELECT * FROM sc_accounts ORDER BY account DESC LIMIT 1')
        row = self.cursor.fetchone()
        if row:
            return SCAccount(*row)
        return None
    def get_login_sc_account(self):
        self.cursor.execute('SELECT * FROM sc_accounts WHERE login=1  ORDER BY account ASC')
        rows = self.cursor.fetchall()
        accounts = [SCAccount(*row) for row in rows]
        return accounts
    def logout_sc_account(self, account):
        self.cursor.execute('UPDATE sc_accounts SET login=0 WHERE account=?', (account,))
    def login_sc_account(self, account):
        self.cursor.execute('UPDATE sc_accounts SET login=1 WHERE account=?', (account,))





    def init_account_order(self, account, balance):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute('''
            INSERT OR REPLACE INTO sc_account_order (
                account, 
                balance, 
                transfed, 
                update_time, 
                order_complete
            )
            SELECT ?, ?, ?, ?, ?
            FROM sc_account_order
            WHERE account = ? 
              AND DATE(update_time) < DATE(?)
            UNION ALL
            SELECT ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 
                FROM sc_account_order 
                WHERE account = ?
            )
        ''', (
            # 第一部分：如果存在且时间小于今天，更新
            account, balance, 0, now, 0, account, today,
            # 第二部分：如果不存在，插入
            account, balance, 0, now, 0, account
        ))
        self.conn.commit()
    def complete_account_transfer(self, account):
        self.cursor.execute('UPDATE sc_account_order SET transfed = 1 WHERE account = ?', (account,))
        self.conn.commit()
    def complete_account_order(self, account):
        self.cursor.execute('UPDATE sc_account_order SET order_complete = 1 WHERE account = ?', (account,))
        self.conn.commit()
    def insert_hx_account(self, account, password,key):
        self.cursor.execute('''
            INSERT OR REPLACE INTO hx_accounts (account, type, password,key)
            VALUES (?, ?, ?, ?)
        ''', (account, 1, password,key))
        self.conn.commit()
    def get_hx_account(self):
        self.cursor.execute('SELECT * FROM hx_accounts WHERE type = 1')
        row = self.cursor.fetchone()
        if row:
            return HXAccount(*row)
        return None
# if __name__ == '__main__':
#     db = Database("accounts.db")
#     # 示例批量插入
#     accounts = [
#         ("account1", "password1"),
#         ("account2", "password2"),
#         ("account3", "password3")
#     ]
#     db.batch_insert_account(accounts)
#
#     # 获取所有账户
#     # all_accounts = db.get_all_sc_account()
#     # for account in all_accounts:
#     #     print(f"Account: {account.account}, Password: {account.password}")
#     # # 初始化账户订单
#     # db.init_account_order("account1", 1000.0)
#     # # 完成订单
#     # db.complete_account_order("account1")
#     all_not_transfed_accounts=db.get_not_transfed_accounts()
#     for account in all_not_transfed_accounts:
#         print(f"未转账账号: {account.account}")
#     all_transfed_accounts=db.get_transfed_accounts()
#     for account in all_transfed_accounts:
#         print(f"已转账账号: {account.account}")
#     db.init_account_order("account1",3000)