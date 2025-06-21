

class SCAccount:
    def __init__(self, account,password,login):
        self.account = account
        self.password = password
        self.login = login


class SCAccountOrder:
    def __init__(self, account,balance,transfed, update_time,order_complete):
        self.account = account
        self.balance = balance
        self.transfed = transfed
        self.update_time = update_time
        self.order_complete=order_complete
class HXAccount:
    def __init__(self,type,account, password):
        self.type = type
        self.account = account
        self.password = password
class SCFailSummary:
    def __init__(self, account, fail_money,update_time):
        self.account = account
        self.fail_money = fail_money
        self.update_time = update_time
