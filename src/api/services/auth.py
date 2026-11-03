import os
import hashlib
import secrets
from datetime import datetime, timedelta

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    iterations = 694200 # consider saving this as secret
    hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    return f"{iterations}:{salt.hex()}:{hash.hex()}"
