import requests


class Log:
    def __init__(self):
        self.addUrl="http://47.122.40.107:8000/log/add?hx={}&sc={}"
        pass
    def add(self,hx,sc):
        requests.get(self.addUrl.format(hx,sc))