# zodb_database.py
from ZODB import FileStorage, DB
import transaction
from persistent.mapping import PersistentMapping
from database.accounts import SCAccount, SCAccountOrder
from datetime import datetime
class ZODatabase:
    def __init__(self, db_file='mydata.fs'):
        self.storage = FileStorage.FileStorage(db_file)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()

        # 初始化 root 数据结构（如果不存在）
        if not hasattr(self.root, 'sc_accounts'):
            self.root.sc_accounts = PersistentMapping()  # 存储 SCAccount
        if not hasattr(self.root, 'sc_account_orders'):
            self.root.sc_account_orders = PersistentMapping()  # 存储 SCAccountOrder

    def close(self):
        self.connection.close()
        self.db.close()
        self.storage.close()

    # ==== sc_accounts ====
    def batch_insert_account(self, accounts):
        for account, password in accounts:
            self.root.sc_accounts[account] = SCAccount(account, password, False)
        transaction.commit()

    def get_all_sc_account(self):
        return sorted(self.root.sc_accounts.values(), key=lambda x: x.account)

    def get_login_sc_account(self):
        return [acc for acc in self.root.sc_accounts.values() if acc.login]

    def logout_sc_account(self, account):
        if account in self.root.sc_accounts:
            self.root.sc_accounts[account].login = False
            transaction.commit()

    def login_sc_account(self, account):
        if account in self.root.sc_accounts:
            self.root.sc_accounts[account].login = True
            transaction.commit()

    # ==== sc_account_order ====
    def init_account_order(self, account, balance):
        now = datetime.now()
        if account in self.root.sc_account_orders:
            order = self.root.sc_account_orders[account]
            if order.update_time.date() < now.date():
                order.balance = balance
                order.transfed = False
                order.order_complete = False
                order.update_time = now
        else:
            self.root.sc_account_orders[account] = SCAccountOrder(
                account=account,
                balance=balance,
                transfed=False,
                update_time=now,
                order_complete=False
            )
        transaction.commit()

    def complete_account_transfer(self, account):
        if account in self.root.sc_account_orders:
            self.root.sc_account_orders[account].transfed = True
            transaction.commit()

    def complete_account_order(self, account):
        if account in self.root.sc_account_orders:
            self.root.sc_account_orders[account].order_complete = True
            transaction.commit()

    def get_order_account(self, account):
        return self.root.sc_account_orders.get(account, None)

    def get_not_transfed_accounts(self):
        return [acc for acc in self.root.sc_account_orders.values() if not acc.transfed]

    def get_transfed_accounts(self):
        return [acc for acc in self.root.sc_account_orders.values() if acc.transfed]