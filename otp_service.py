import hashlib
from datetime import datetime, timedelta, timezone
import random


def generate_otp():
    return str(random.randint(100000, 999999))


def hash_otp(otp: str):
    return hashlib.sha256(otp.encode()).hexdigest()


def get_expiry(minutes=10):
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)