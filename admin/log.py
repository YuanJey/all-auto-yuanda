import requests

class Log:
    def __init__(self):
        self.addUrl="http://47.239.98.81:8000/log/add?hx={}&sc={}"
        self.addsUrl="http://47.239.98.81:8000/log/adds"
        pass
    def add(self,hx,sc):
        hx_str = str(hx)
        sc_str = str(sc)
        requests.get(self.addUrl.format(hx_str, sc_str))
    def adds(self, hx, sc_list):
        list=[str(sc.account) for sc in sc_list]
        data = {
            "hx": str(hx),
            "sc_list": list
        }
        requests.post(self.addsUrl, json=data)