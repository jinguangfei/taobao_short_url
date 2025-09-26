import asyncio
import traceback
import json
from re import I
from curl_cffi.requests import AsyncSession
from curl_cffi.requests.models import Response

class MyQueue(object):

    def __init__(self, queue_name : str = "vps"):
        self.url = f"http://123.56.44.124:9461/{queue_name}/"

    async def get_one_info(self, key="" ,add_t :int = 20, start_t :int = 0, end_t :int = 0, level :int = 0, loop_type :int = 1, view_name :str = ""):
        one_key_info = dict()
        try:
            url = self.url + "?" + f"view_name={view_name}&one_key={key}&add_t={add_t}&start_t={start_t}&end_t={end_t}&level={level}&loop_type={loop_type}"
            print(url)
            async with AsyncSession() as s:
                res = await s.get(url)
            #one_key_info.key_info= res.text.replace("\"","")
            one_key_info = json.loads(res.text)
        except Exception as e:
            print(e)
            pass
        return one_key_info

    async def wait(self, key : str, add_t :int = 20, view_name : str = ""):
        url = self.url + "?" + f"view_name={view_name}"
        try:
            data = {
                "key": key,
                "add_t": add_t
            }
            async with AsyncSession() as s:
                res = await s.put(url, data=data)
        except Exception as e:
            print(e)
            pass

    async def delete(self, key : str, view_name : str = ""):
        url = self.url + "?" + f"view_name={view_name}"
        try:
            data = {
                "key": key
            }
            async with AsyncSession() as s:
                res = await s.delete(url, data=data)
        except Exception as e:
            print(e)
            pass

    async def update_flag(self, key : str, flag : int, view_name : str = ""):
        url = self.url + "update_flag?" + f"view_name={view_name}"
        try:
            data = {
                "key": key,
                "flag": flag
            }
            async with AsyncSession() as s:
                res = await s.put(url, data=data)
        except Exception as e:
            print(traceback.format_exc())
            pass

if __name__ == "__main__":
    item = MyQueue(queue_name="cookie")
    print(asyncio.run(item.get_one_info(add_t=12,view_name="chrome_ext")))
    asyncio.run(item.wait(key="96689",add_t=100,view_name="chrome_ext"))
    asyncio.run(item.delete(key="96689",view_name="chrome_ext"))
