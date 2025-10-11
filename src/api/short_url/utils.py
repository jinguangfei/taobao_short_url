from curl_cffi.requests import AsyncSession
import json


async def get_mi_id(cookie : str = "", proxies : dict = {}) -> str:
    url = "http://123.56.44.124:9460/api/mi_id/"
    async with AsyncSession() as s:
        res = await s.post(url, json={"cookie":cookie, "proxies":proxies})
        return json.loads(res.text).get("result")