import time
import random

def generate_id():
    timestamp = int(time.time() * 1000)  # Get current timestamp in milliseconds
    random_number = random.randint(0, 9999)  # Generate a random number between 0 and 9999
    id = f"{timestamp}{random_number}"
    return id

def generate_time():
    timestamp = int(time.time() * 1000)  # Get current timestamp in milliseconds
    return (f"{timestamp}")