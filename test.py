import time
import asyncio

from curl_cffi.requests import AsyncSession

async def test(cookie):
    url = "http://123.56.44.124:9460/api/xianyu_cookie/relogin"
    data = {   
        "cookie_str": cookie,
        "proxies": {}
    }

    async with AsyncSession() as session:  
        response = await session.post(url, json=data)
        print(response.text)

if __name__ == "__main__":
    cookie_list = [] 
    with open("xy_cookie_20251103", "r") as f:
        cookie_list = f.readlines()
        cookie_list = [cookie.strip() for cookie in cookie_list]
    for cookie in cookie_list:
        asyncio.run(test(cookie.strip()))
        time.sleep(1)
