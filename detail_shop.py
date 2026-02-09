import os
import requests
import re
import json 
import time
import hashlib,urllib
from urllib.parse import quote
import copy

url_base = 'https://h5api.m.tmall.com/h5/mtop.taobao.shop.simple.fetch/1.0/?jsv=2.6.2&appKey=12574478&t={}&sign={}&api=mtop.taobao.shop.simple.fetch&type=originaljson&v=1.0&timeout=10000&dataType=json&sessionOption=AutoLoginAndManualLogin&needLogin=true&LoginRequest=true&jsonpIncPrefix=_1767085160743_&data={}'
header = {
    "Accept-Encoding": "deflate, gzip",
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "referer": "https://hot.taobao.com/",
    "cookie":'',
    #"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
}

get_proxy_url = 'http://101.200.137.28:9238/vps?method=GetIP&port=' 
def load_proxy(port):
    tmp_data = requests.get(get_proxy_url + str(port)).json().get("RESULT", {}) 
    _ip_ = tmp_data.get("wanIp", "") + ":" + tmp_data.get("proxyport", "") 
    proxy_ip = { 
        'http': 'http://zhihai:zhihaiSQUID2018@%s' % _ip_,
        'https': 'http://zhihai:zhihaiSQUID2018@%s' % _ip_
    }
    print('获取代理成功，代理：', proxy_ip)
    return proxy_ip
proxies = load_proxy(8436)

cookies = ['mtop_partitioned_detect=1;_m_h5_tk=5f5fbe6118dc763aafd105f6a8b2ff37_1763915741532;_m_h5_tk_enc=9a7ba402ef70f61ce78e692125b84054;XSRF-TOKEN=a9bea0cb-98c9-4fc4-a6cd-c76fb7e24851;_samesite_flag_=true;cookie2=181445ea59ed3ba14cfac483023944fc;t=a0c0f86d6035842eb25bcab704446198;_tb_token_=e1e71336eee77;cbc=;sgcookie=E100tNoBgDMJ3L%2B%2BQoS1iZcN3RTImsNTEIuYY4W23PeYmmgwPtDQ0qhl5GCGlBjzhg2qEPIhUI21jP6b4%2BmLSvYWH9OWCWmKpB0qLJ0RPfG%2FVzQ%3D;wk_cookie2=1a54e1923142377d2b8e5c2c88a939e2;wk_unb=UUpgR1F2o9saHYiupw%3D%3D;unb=2211385261407;uc1=pas=0&cookie21=UIHiLt3xTwwM1Oej1w%3D%3D&existShop=false&cookie15=VFC%2FuZ9ayeYq2g%3D%3D&cookie16=URm48syIJ1yk0MX2J7mAAEhTuw%3D%3D&cookie14=UoYY4HDIoRTjSg%3D%3D;sn=;uc3=nk2=F5RDJLj96eB5XXk%3D&vt3=F8dD2klrDdV4k7H5Ru8%3D&id2=UUpgR1F2o9saHYiupw%3D%3D&lg2=VT5L2FSpMGV7TQ%3D%3D;csg=e8f8cd3c;ultraCookieBase=;lgc=tb687344797;cancelledSubSites=empty;cookie17=UUpgR1F2o9saHYiupw%3D%3D;dnk=tb687344797;skt=1b1ad7eaa92191fe;existShop=MTc2MzkwNzgzNg%3D%3D;uc4=nk4=0%40FY4I572WkfL5Avqh9vPB9RLINFkvuA%3D%3D&id4=0%40U2gqyOyiK3hwNyfAMrmsY5VhyJf0CHpN;publishItemObj=;tracknick=tb687344797;lc=V3pIOMbhCemA6IiAZino1w%3D%3D;_cc_=UIHiLt3xSw%3D%3D;lid=tb687344797;_l_g_=Ug%3D%3D;sg=774;_nk_=tb687344797;cookie1=VAZ%2BhIBD1qBY6VetfrijvD%2F5Upr2nxsL5Dgc9STHTTc%3D;']
cookies = ['JSESSIONID=AWG66WB1-T2L1L0LCGT7ZLC2YK0MX2-31CS0HJM-9KZ2;XSRF-TOKEN=8c0acc63-7208-481d-8a89-72f7b1e26af2;_cc_=VFC%2FuZ9ajQ%3D%3D;_l_g_=Ug%3D%3D;_m_h5_tk=c5a2b32503fa1cbfd8c9434f21b5cfe9_1766409769358;_m_h5_tk_enc=538416875bfe1ca3134d37bd34c17687;_nk_=tb973236733;_samesite_flag_=true;_tb_token_=3e139317de385;_w_tb_nick=tb973236733;cancelledSubSites=empty;cookie1=UUHxzCZY3K2YZ0qBD5Efl1q3pR%2F669mz%2FbWo3GibfmI%3D;cookie17=UUpgRK4AfZTzsJXyDw%3D%3D;cookie2=14394eb53929a8eb36934722121dc385;csg=fa8e0333;dnk=tb973236733;lgc=tb973236733;lid=tb973236733;munb=2212307685712;ockeqeudmj=qZBpOIQ%3D;sg=328;sgcookie=E100vymfCVnecsfFd6gnotaxKxFlkCwcAcXdJB2uSPfMckzcdpihGKy4JjOFEx8KFHjZRCh1bevSp2d9OA7dZLTJM7R6g0KLbHjQA%2FbkXk2cF50%3D;skt=926dad0ad7c16a54;t=fc00dd5ac1bc295585e6e2fd88b6b26b;tmp0=CjeTRP%2FMhsEzWYPp%2FDx4GIQMWQM1lQuyrFRot%2FrlQ%2BIiuYb691P7zCvRS2fM5Kp0Z4xAGHSROsNaz5ZBLKtS2fcNnaRDOC4EkjBe60HnAHUo%2Byol7aDtZLZFdNnAeWJck9FrPyrExfwTQ7Xs9JbloQ%3D%3D;tracknick=tb973236733;uc1=cookie21=VT5L2FSpczFp&cookie14=UoYY5RNe0sXHLQ%3D%3D&existShop=false&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D;uc3=vt3=F8dD2keld66%2FfEyjbvw%3D&id2=UUpgRK4AfZTzsJXyDw%3D%3D&lg2=W5iHLLyFOGW7aA%3D%3D&nk2=F5RMHlkiOtPtTOw%3D;uc4=nk4=0%40FY4HWyxqx3R5PiaWisDqiJi1ILIrXw%3D%3D&id4=0%40U2gqy1%2FrkCScMUggnLQo80ln4gvNUgMj;unb=2212307685712;wk_cookie2=10c67e5d9dc7dbed674ce66b88ac8a5b;wk_unb=UUpgRK4AfZTzsJXyDw%3D%3D']


ci =0
for line in range(0,4):
    
    if True:      
 
        base_data = '{\"shopId\":\"144807160\",\"sellerId\":\"2738112600\"}'
        # base_data = '{\"shopId\":\"144807160\",\"sellerId\":\"\"}'
        t = "%.3f" % time.time()
        t = t.replace(".","")

        headers = copy.deepcopy(header)

        header["cookie"] = cookies[ci]
        print(header["cookie"])
        token_group = re.search(r"_m_h5_tk=(.*?)_", header["cookie"]) 
        token = token_group.group(1) if token_group else ""
        print(token)
        data_base = '%s&%s&12574478&%s'
        data = data_base % (token,t,base_data)

        m = hashlib.md5()
        m.update(data.encode())
        sign = m.hexdigest()
        url = url_base.format(t, sign, quote(base_data.encode("utf-8")))
        print(url)
        # proxies = {
        #     'http': 'http://1262292604226523136:W3PUFPuo@http-dynamic-S02.xiaoxiangdaili.com:10030',
        #     'https': 'http://1262292604226523136:W3PUFPuo@http-dynamic-S02.xiaoxiangdaili.com:10030'
        # }
        # print(header)

        try:
            print(url)
            print(header)
            print(proxies)
            response = requests.get(url=url, headers=header, timeout=60, proxies=proxies)
            # response = requests.get(url=url, headers=header, timeout=60)
        except Exception as e:
            print(e)
            ci = ci + 1
            if ci == len(cookies):
                ci = 0
            print('============== error  qie ====================================')
            id_tiao = item_id
            time.sleep(0.1)
            continue
        # print('================================')
        # print(response.headers)
        print(response.text)
        if '_____tmd_____/page/set_x5referer' in response.text:
            ci = ci + 1
            if ci == len(cookies):
                ci = 0
            
            print('============== qie ====================================')
            time.sleep(0.1)
            
            continue
        elif '"FAIL_SYS_TOKEN_EXOIRED::令牌过期"' in response.text:
            cks = header["cookie"] 
            cs = cks.split(';')
            ck_str = ''
            for ckkk in cs:
                # 取第一个分号前的部分（键值对）
                key_value = ckkk.split('=')[0]
                if '_m_h5_tk' in key_value:
                    pass
                else:
                    ck_str = ck_str + ";" + ckkk

            # 分割为单个cookie项
            cookie_str = response.headers.get("Set-Cookie", '')
            cookie_list = cookie_str.split(', ')

            # 构建cookie字典
            cookie_dict = {}
            for cookie in cookie_list:
                # 取第一个分号前的部分（键值对）
                key_value = cookie.split(';')[0]
                if '=' in key_value:
                    key, value = key_value.split('=', 1)  # 只分割第一个=
                    cookie_dict[key] = value

            # 提取目标值
            m_h5_tk = cookie_dict.get('_m_h5_tk')
            m_h5_tk_enc = cookie_dict.get('_m_h5_tk_enc')
            new_cookie = '_m_h5_tk=' +  m_h5_tk + ";_m_h5_tk_enc=" + m_h5_tk_enc + ck_str
            cookies[ci] = new_cookie
            print(new_cookie)
            time.sleep(1)
            continue
        elif '哎哟喂,被挤爆啦,请稍后重试' in response.text:
            print(response.text)
            time.sleep(180)
        elif 'mtopjsonp1(' in response.text:
            # fw.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))+":##:"+str(item_id)+":##:"+response.text+'#$#$#$\n')
            # fw1.write(str(item_id) + '\n')
            print('============== success ' + str(item_id) + ' ====================================')
            time.sleep(27)
        else:
            break