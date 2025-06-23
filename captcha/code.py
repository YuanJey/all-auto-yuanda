from abc import ABC, abstractmethod

class Code(ABC):
    @abstractmethod
    def get_captcha_base64(self):
        pass
    @abstractmethod
    def get_captcha_result(self,base64_image):
         pass