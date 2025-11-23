# tasks/utils.py
import random
import time

OTP_TTL_SECONDS = 300  # 5 minutes
MAX_OTP_ATTEMPTS = 5

def generate_otp(length: int = 6) -> str:
    """Return a numeric OTP string."""
    if length <= 0:
        raise ValueError("length must be positive")
    return ''.join(random.choices("0123456789", k=length))

def otp_expired(sent_timestamp: float | None) -> bool:
    """
    sent_timestamp: float from time.time() when OTP was created.
    Returns True if expired or if sent_timestamp is None.
    """
    if sent_timestamp is None:
        return True
    return time.time() > (sent_timestamp + OTP_TTL_SECONDS)
