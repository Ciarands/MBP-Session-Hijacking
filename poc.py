import time
import orjson
from hashlib import md5
from base64 import b64encode
from Cryptodome.Cipher import DES3
from Cryptodome.Util.Padding import pad

APP_KEY = "moviebox"
ENCRYPTION_IV = b"\x77\x45\x69\x70\x68\x54\x6e\x21"
ENCRYPTION_KEY = b"\x31\x32\x33\x64\x36\x63\x65\x64\x66\x36\x32\x36\x64\x79\x35\x34\x32\x33\x33\x61\x61\x31\x77\x36"

def get_md5_signature(payload: bytes):
    if not payload:
        return None
    return md5(
        md5(APP_KEY.encode()).hexdigest().encode()
        + ENCRYPTION_KEY
        + payload
    ).hexdigest()

def des3_encrypt(plaintext: bytes):
    cipher = DES3.new(ENCRYPTION_KEY, DES3.MODE_CBC, ENCRYPTION_IV)
    return b64encode(cipher.encrypt(pad(plaintext, DES3.block_size)))

if __name__ == "__main__":
    base = {"app_key": md5(APP_KEY.encode()).hexdigest()}
    encrypted_payload = des3_encrypt(orjson.dumps({
        "uid": int(input("Input user id:")),
        "expired_date": str(int(time.time() + 43200))
    }))
    base.update({"encrypt_data": encrypted_payload.decode(), "verify": get_md5_signature(encrypted_payload)})
    print(b64encode(orjson.dumps(base)).decode())
