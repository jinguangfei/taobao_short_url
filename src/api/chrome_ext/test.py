from calendar import c
import requests
import sys
import random
from src.core.redis_script import redis_pool

url_redis_key = "chrome_ext:item_url"

# 8秒一次
import time
with open("src/tmp/20251015_item_url", "r") as f:
    item_id_list = f.read().splitlines()
    item_id_list = [item_id.split(" ")[0] for item_id in item_id_list][100:]
    #item_id_dict = {item_id.split(" ")[0]:item_id.split(" ")[1] for item_id in item_id_list}
    #redis_pool.hmset(url_redis_key, item_id_dict)
i = 0
r_type = sys.argv[1]
for j in range(200):
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
    time.sleep(1)