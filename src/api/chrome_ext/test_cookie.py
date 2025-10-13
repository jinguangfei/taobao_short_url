import requests
import time
import sys
import random

# 8秒一次
short_url_api = "http://123.56.44.124:9460/api/short_url/"
with open("src/api/chrome_ext/item_id_list", "r") as f:
    item_id_list = f.read().splitlines()

with open("src/tmp/hr_cookie_20251013_1", "r") as f:
    cookie_list = f.read().splitlines()

def check_cookie(cookie):
    url = short_url_api
    data = {
        "targetId": random.choice(item_id_list),
        "targetUrlType": "LT_TAOBAO",
        "cookie": cookie,
    }
    response = requests.post(url, json=data)
    return response.json()

if __name__ == "__main__":
    for cookie in cookie_list[:60]:
        print(check_cookie(cookie))
        time.sleep(1)
