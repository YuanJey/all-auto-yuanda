

class SCAccount:
    def __init__(self, account,password,login):
        self.account = account
        self.password = password
        self.login = login


class SCAccountState:
    def __init__(self, account,state,update_time):
        self.account = account
        self.state = state
        self.update_time = update_time
class HXAccount:
    def __init__(self,type,account, password,key):
        self.type = type
        self.account = account
        self.password = password
        self.key = key
class SCFailSummary:
    def __init__(self, account, fail_money,update_time):
        self.account = account
        self.fail_money = fail_money
        self.update_time = update_time
