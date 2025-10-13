import re
import json
import asyncio
from curl_cffi.requests import AsyncSession
from typing import Dict, Tuple
import urllib.parse
import time
import hashlib

def md5_data(tk: str, data_str : str = "", t : str = "", app_key : str = "12574478") -> Tuple[str,str]:
    t = t if t else str(int(time.time()*1000))
    app_key = app_key if app_key else "12574478"
    data = (r'%s&%s&%s&%s' % (tk,t,app_key,data_str)).encode("utf-8")
    m = hashlib.md5()
    m.update(data)
    sign = m.hexdigest()
    return t, sign, data_str

def parse_url(url: str) -> Tuple[str,Dict]:
    url_params = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(url_params.query)
    for k, v in query_params.items():
        query_params[k] = v[0]
    url_params = url_params._asdict() # convert to dict 
    url_path = url_params.get("scheme") + "://" + url_params.get("netloc") + url_params.get("path")
    return url_path,query_params

def build_url(url_path: str, query_params: Dict) -> str:
    return url_path + "?" + "&".join([f"{k}={v}" for k,v in query_params.items()])

def parse_cookie_str(cookie_str : str) -> dict:
    return {i.split("=")[0]:i.split("=",1)[1] for i in cookie_str.replace("; ",";").split(";") if len(i.split("="))>1}

async def get_mi_id(cookie : str = "", proxies : dict = {}) -> str:
    url = "http://123.56.44.124:9460/api/mi_id/"
    async with AsyncSession() as s:
        res = await s.post(url, json={"cookie":cookie, "proxies":proxies})
        return json.loads(res.text).get("result")

async def get_tk() -> str:
    url = "http://123.56.44.124:9460/api/taobao_tk/"
    async with AsyncSession() as s:
        res = await s.get(url)
        return res.text

cart_url = "https://h5api.m.taobao.com/h5/mtop.taobao.third.pcdetail.data.get/1.0/?jsv=2.7.2&appKey=12574478&t=1760318672445&sign=caaaad6a8d82de38eaf515876746188f&api=mtop.taobao.third.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&dataType=json&valueType=string&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=json&data=%7B%22id%22%3A%22668872706204%22%2C%22detail_v%22%3A%223.3.2%22%2C%22mi_id%22%3A%2200001PFY7E3Swjamrq-PYwjtgnwR-nOQN2eJey5eOfYAJp8%22%2C%22exParams%22%3A%22%7B%5C%22from%5C%22%3A%5C%22cart%5C%22%2C%5C%22id%5C%22%3A%5C%22668872706204%5C%22%2C%5C%22skuId%5C%22%3A%5C%220%5C%22%2C%5C%22upStreamPrice%5C%22%3A%5C%22%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22from%3Dcart%26id%3D668872706204%26mi_id%3D00001PFY7E3Swjamrq-PYwjtgnwR-nOQN2eJey5eOfYAJp8%26skuId%3D0%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fcart.taobao.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fcart.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22Cart%5C%22%7D%22%7D"
def build_cart_url(item_id : str, mi_id : str, cookie : str) -> str:
    url_path, query_params = parse_url(cart_url)

    cookie_dict = parse_cookie_str(cookie)
    tk_cookie = cookie_dict.get("_m_h5_tk","")
    tk_g = re.search(r"(.*?)_",tk_cookie)
    tk = tk_g.group(1) if tk_g else ""

    exParams = {
        "from": "cart",
        "id": item_id,
        "skuId": "0",
        "upStreamPrice": "",
        "queryParams": f"from=cart&id={item_id}&mi_id={mi_id}&skuId=0",
        "domain": "https://cart.taobao.com",
        "path_name": "/cart.htm",
        "pcSource": "Cart"
    }
    data = {
        "id": item_id,
        "detail_v": "3.3.2",
        "mi_id": mi_id,
        "exParams": json.dumps(exParams).replace(" ", "")
    }
    data_str = json.dumps(data).replace(" ", "")
    t = int(time.time()*1000)
    t, sign, data_str = md5_data(tk, data_str, t)
    query_params["t"] = t
    query_params["sign"] = sign
    query_params["data"] = urllib.parse.quote(data_str)
    return build_url(url_path, query_params)

if __name__ == "__main__":
    cookie = "_samesite_flag_=true;3PcFlag=1759333234063;cookie2=18b17e2554749826c7d8cc567fd779d4;t=7cf6db599c4a7bdb58cefc4928e68059;_tb_token_=e673153188445;cna=dzlkIeuENUoCAbSMRsF/Z1qP;xlly_s=1;unb=2220922073984;lgc=tb278010826805;cancelledSubSites=empty;cookie17=UUpjNmpJo%2B%2FvPZHD1A%3D%3D;dnk=tb278010826805;tracknick=tb278010826805;_l_g_=Ug%3D%3D;sg=54a;_nk_=tb278010826805;cookie1=AQWasc5FhKy%2F7gR7SkAj7gSoumVfO1bUN%2FNY4WxRmko%3D;sgcookie=E100%2BKXK2OSywf1nm11vA1vkBJ71pR3UccjVYYrddMfoxvZb7jX%2Fiu9g%2FcRoYSBVAWhlDstziMtwpf0GNjdEuqxH13NVuAFp4dc9N%2FCUKoq43J4%3D;havana_lgc2_0=eyJoaWQiOjIyMjA5MjIwNzM5ODQsInNnIjoiOWQzODU0NTZlZGVhNzY4YzRjZjU4MjY5NDE3Y2EzOTQiLCJzaXRlIjowLCJ0b2tlbiI6IjFWMGxsd2hhdTFTSEJKNEVsZm8xYUxnIn0;_hvn_lgc_=0;cookie3_bak=18b17e2554749826c7d8cc567fd779d4;cookie3_bak_exp=1759592636194;sn=;uc3=lg2=V32FPkk%2Fw0dUvg%3D%3D&id2=UUpjNmpJo%2B%2FvPZHD1A%3D%3D&vt3=F8dD2k60ESOSGsqknEM%3D&nk2=F5RHprSFOyukskTwVSY%3D;csg=44b0405f;env_bak=FM%2BgzieMD6rmz7D%2FnntDUKZ4rn3m1stBEtjkNE9jCjhE;skt=e12cbb181cc1ae67;existShop=MTc1OTMzMzQzNg%3D%3D;uc4=nk4=0%40FY4MtLWMvAjWYc1w7qzsiQGaINNBUweQlQ%3D%3D&id4=0%40U2gp9rljY9%2BoTqIwVaJi7%2ByeCT6og6C%2B;_cc_=WqG3DMC9EA%3D%3D;uc1=cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&existShop=false&pas=0&cookie14=UoYbwhLlsxvZbw%3D%3D&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&cookie21=WqG3DMC9Eman;havana_lgc_exp=1790437480171;sdkSilent=1759362280171;thw=cn;tfstk=gUmS3Cg-l_fWD40TPkJVlhZdQ8ZB3K-wd9wKIvIPpuER96HTgMJu4eqIOSG3azr8YMFKZbgULUDPAqGoBzrEAvjQpvhHEWJkuYDuxkdw_DtZEYf5I4MegkpKHkyBkeHp6YDuxtjkYjfqE9_qD4VLpWpbDJy5JkEK9oEYiJ2dwJIJhxF0MJQRvyIAHR2F9_hLvKMYiJEL9XUJhxF0pkFKKFB_dUNoFdhLRFZhauH8GMIKDH471YQFvMnbFziKeS6PUmw7P5Udpndo2jkK404D_1qn3VGIJXYNouMKyueZE3sbXY3qA-oeLwN-ZmMxqr6R2kg-N2UilhbgyxMK7ri2Bhq7273UqvW6axiSaYmjL9QYVuub50ZdKMl3VR4sckXhXxEzpX4iYCjuwvHijVr60aEth2hsRgofb56eLw6bSMeb_K9f-wcidEoKQgAGnze0FrJXh_33y-2b_K9f-w48n-XwhK_OK;isg=BNDQjqsnjI7KKFCKNq_xVY_0oR4imbTjqTOrgcqhnCv-BXCvcqmEcyan383l1Wy7"
    print(asyncio.run(get_mi_id(cookie=cookie, proxies={})))
    #print(asyncio.run(get_tk()))
    #url_path, query_params = parse_url(cart_url)
    #print(url_path, query_params)
    #print(build_url(url_path, query_params))
    #cookie = "_m_h5_tk=b783769690156b818e3eca8f28bdbce8_1760325056370; _m_h5_tk_enc=5416853f4408f3c2475112b4121894c6; t=3b4102a8adb146d9d0c4c0e5319b0661; _samesite_flag_=true; cookie2=108d684748eb523fbdf2475e4fb25329; _tb_token_=f35ba017307fb; xlly_s=1; cancelledSubSites=empty; 3PcFlag=1760251399567; unb=2220983334442; lgc=tb422904006286; cookie17=UUpjNmpDK73vcLJ7dg%3D%3D; dnk=tb422904006286; tracknick=tb422904006286; _l_g_=Ug%3D%3D; sg=62a; _nk_=tb422904006286; cookie1=UUpjP%2FK8wkWDnVNtVcIUPmf%2BK3d1f7nUCxz4xoSG4kY%3D; sgcookie=E100%2FQmu%2FPFs7mL%2BkGEPVsLXSSbZ%2Bx4VN4rMqZa4qNz3eFLEh6eEQ86ciEAYJnssL6ExNj8ckhxVnEn9ND9NDcFKe0ZX19IYZn83Q1kF9yn6mNk%3D; havana_lgc2_0=eyJoaWQiOjIyMjA5ODMzMzQ0NDIsInNnIjoiNzhlOTRkYTEwNzllMWMzNzQ0Y2VkZjRjY2E3MzU2ZmEiLCJzaXRlIjowLCJ0b2tlbiI6IjFOeGRYSHloNkVBd19rUFVZNXd4bmx3In0; _hvn_lgc_=0; cookie3_bak=108d684748eb523fbdf2475e4fb25329; cookie3_bak_exp=1760510792841; sn=; uc3=vt3; csg=068f3f47; env_bak=FM%2BgwFS8%2F1yDTydnY5fElf2hIjwloAhAEzcxRSrHmPst; skt=bb07bf57e31fcff3; existShop=MTc2MDI1MTU5Mg%3D%3D; uc4=nk4; _cc_=VFC%2FuZ9ajQ%3D%3D; thw=cn; aui=2220983334442; cna=sDpyIf6b0iQCATFBnpDbWFmm; uc1=pas; mtop_partitioned_detect=1; sca=9325ec8a; havana_lgc_exp=1791424971552; sdkSilent=1760349771551; havana_sdkSilent=1760349771551; mtop_partitioned_detect=1; _m_h5_tk=ccdf3414d69793e743975e31405177f8_1760330803807; _m_h5_tk_enc=23cdd8abeefca4cdc609f6e81da0fa1f; isg=BJ-fowhmC7qjHQ-hcgSQQT9ILvUpBPOmNKTi2zHsMs6VwL9COdYs9sYSglC-2Mse; tfstk=gCNoCKOPNmtswoOWEwc5eLgW9_BYwbGICkdKvXnF3moX23d882l30kQS2yS7xWmqavw-v0nntyZGkGCO6zaSObSOX1n0Y70iOD5KTth2ZtND0GCO6z6rPXUVXWETHB3sWBlEUv5qgmgHLLRUYxRqRmRr8Que0Z0I0XuyUB5qg43eTLoUYr7mRmoETXrEgZ0I0DlETUAXzcDt3SSe9Pc4pvDui4DobrX6TB2v6YmaPmAFbS0oOczrmBREjdVwDyrFxBhaCoVnQlCHGbUg3juunwJq4A2z2qZhsQozizPr27Svw0P7uRFL0wREx-yZBRzPDK003zFmH5SMtYw4VRM39iCswRUTOAPPZhixC2qia-j2ZlSz3KJNGGRIuwF2dpMrlqmO_z-OpAX9mx_cod9IUqgz8ZbDdUHrlqmOoZvajYujrPf.."
    #print(build_cart_url("851335536454", "00001PFY7E3Swjamrq-PYwjtgnwR-nOQN2eJey5eOfYAJp8", cookie))