import requests


class Log:
    def __init__(self):
        self.addUrl="http://47.122.40.107:8000/log/add?hx={}&sc={}"
        pass
    def add(self,hx,sc):
        hx_str = str(hx)
        sc_str = str(sc)
        requests.get(self.addUrl.format(hx_str, sc_str))