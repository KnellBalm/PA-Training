from datetime import datetime
import random
import uuid

def generate_session_id():
    return str(uuid.uuid4())

def generate_ts(day, hour=None):
    if hour is None:
        hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{day} {hour:02}:{minute:02}:{second:02}"

def batch(iterable, n=5000):
    """yield fixed-size chunks"""
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]
