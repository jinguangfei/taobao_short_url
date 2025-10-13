import requests
import sys
import random

# 8秒一次
import time
with open("src/api/chrome_ext/item_id_list", "r") as f:
    item_id_list = f.read().splitlines()
i = 0
r_type = sys.argv[1]
for j in range(100):
    item_id = item_id_list[i%len(item_id_list)]
    url = f"http://123.56.44.124:9458/api/chrome_ext/?item_id={item_id}&timeout=15&task_type={r_type}&batch=test_{random.randint(1,1000000)}"
    headers = {
        "accept": "text/plain"
    }
    try:
        response = requests.get(url, headers=headers)
        if len(response.text)>100:
            print(item_id,len(response.text))
        else:
            print(item_id,response.text)
        i += 1
    except Exception as e:
        print(e)
    time.sleep(15)