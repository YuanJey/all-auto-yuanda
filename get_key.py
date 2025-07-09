from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

KEY = b'YourKey123456789'  # 必须是 16、24 或 32 字节长度
BLOCK_SIZE = 16  # AES block size
def aes_encrypt(plaintext: str) -> str:
    # D5yk9yiQbQq0Qvkb8YOC9Q==
    cipher = AES.new(KEY, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(plaintext.encode('utf-8'), BLOCK_SIZE))
    return base64.b64encode(ciphertext).decode('utf-8')
if __name__ == "__main__":
    dec="17600090001"
    aes_encrypt(dec)
    print(aes_encrypt(dec))