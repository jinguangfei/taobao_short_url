import requests
import json
#抓取Riview
class ReviewSpider:
    #页面初始化
    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            "cookie":"sn=;t=a6cb6dba589cbc166371829fcd6dffa9;existShop=MTc2Nzk2MDM5Mg%3D%3D;cookie1=AVNUTuW%2FhaMYHVsfdbhWgajRbFlPJfnDzQIagL%2BsPWs%3D;csg=975f6c30;cnaui=2221135981126;wk_cookie2=1413f0055274c97d6ed9eecf8d5b0ebb;cookie2=1bdb120e03e1d6d2b6f5e5e8da6e3d8d;xlly_s=1;sca=be63c560;skt=55acfa1919079d33;unb=2221155259452;_tb_token_=e73ee47603565;sgcookie=E1000jYbcH6ev36WJr8RgotywU%2Bn3%2FrBxXYDliz3NZTjJnwELrNnEHdQxfWE85M5C3Z2qb9DPZHgcJJP00OzJGEOC4qQdFwgaBW%2FJXy8WQcYNJo%3D;aui=2221135981126;_samesite_flag_=true;tfstk=gE8iCJXpS9w7yZeEr-7sbxpEJinp1N_feKUAHZBqY9WQBRU9gs7DLKh1BIk6nEXeglU9khEc0KpHXi8AHEcc5eKTkOH1oIJRoYH-y4d61NbqeY34RvAGusuA3DIwzHW3zYH-y2d61Z_qeC3fJjUhZ_7V_iSVLXffL1zw3OSUL_f5utJ23XAFds7V3K7qtBWCgZW23fZ__TjRYekx1qgXAoEv-1jGErB3orcAsGXy_9fCOeufjTRNKrkwCo-NL_YEhRBX-B8NwpuLSZAFiLbwxvzMnC-Wh_JZ-R5MbQARxEMzo6teCMCMxjrFQQWwIGxuLfXXWdYcfUk8RO-HREb9vA4Rhi-p5gTtLPbyVCQ90pl4utxFggSbYuJ_Dr1EMeqbcG5CtTeLuoiPrEii6Xc3VosNO1RqtXqj4G5CtThntulPb61wg;wk_unb=UUpjN4iiiXL6VsJqcg%3D%3D;_cc_=UIHiLt3xSw%3D%3D;thw=cn;isg=BLKy6TGPD633KzP20Qr9Vr1sA_6UQ7bdu2mqQnyLyWVQD1IJZNGn7WR9_auzZC51;3PcFlag=1767960343220;_l_g_=Ug%3D%3D;_nk_=tb084846517514;cancelledSubSites=empty;cookie17=UUpjN4iiiXL6VsJqcg%3D%3D;dnk=tb084846517514;lgc=tb084846517514;sg=42f;tracknick=tb084846517514;uc1=cookie15=V32FPkk%2Fw0dUvg%3D%3D&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&pas=0&cookie14=UoYY5MekmyofwA%3D%3D&existShop=false&cookie21=U%2BGCWk%2F7og%3D%3D;uc3=nk2=F5RFiAbzT0jVwBqkCLA%3D&id2=UUpjN4iiiXL6VsJqcg%3D%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D&vt3=F8dD29MAWjalJ5o%2FLJw%3D;uc4=id4=0%40U2gp9x1SjU5tG4IZvLA7e4EfZhYtLygh&nk4=0%40FY4O4bEOD2kCV7YI2TdLGFgG4gUDeMuV5w%3D%3D"
        }
    #获取访问数据
    def getReview(self, sellerId, itemid):
        currentpage = 1
        totalpage = 99999
        while currentpage <= totalpage :
            # bosci 1990484446, dyson 2089100916
            url = "https://rate.tmall.com/list_detail_rate.htm?itemId=" + str(itemid) + "&sellerId=" + str(sellerId) + "&order=3&callback=jsonp867&currentPage=" + str(currentpage)
            r = requests.get(url, headers=self.headers)
            
            # 检查响应状态码
            if r.status_code != 200:
                print(f"请求失败，状态码: {r.status_code}")
                print(f"响应内容: {r.text[:500]}")
                break
            
            rtext = r.text.strip()
            
            # 检查是否是 JSONP 格式
            if not rtext.startswith('jsonp867(') or not rtext.endswith(')'):
                print(f"响应不是预期的 JSONP 格式")
                print(f"响应前500字符: {rtext[:500]}")
                print(f"响应后100字符: {rtext[-100:]}")
                # 检查是否是 HTML（登录页面）
                if '<html' in rtext.lower() or '<script' in rtext.lower():
                    print("检测到 HTML 响应，可能是登录页面或反爬虫页面")
                break
            
            try:
                # 提取 JSON 部分：去掉 'jsonp867(' 和最后的 ')'
                json_str = rtext[9:-1]  # 'jsonp867(' 是9个字符
                rjson = json.loads(json_str)
                
                # 检查 JSON 结构
                if 'rateDetail' not in rjson:
                    print(f"JSON 结构异常，缺少 rateDetail 字段")
                    print(f"JSON 内容: {json.dumps(rjson, ensure_ascii=False, indent=2)[:500]}")
                    break
                
                totalpage = rjson['rateDetail']['paginator']['lastPage']
                ratelist = rjson['rateDetail']['rateList']
                
                if not ratelist:
                    print(f"第 {currentpage} 页没有数据")
                    break
                
                for obj in ratelist:
                    id = str(obj['id'])
                    auctionSku = obj['auctionSku']
                    sellerId = obj['sellerId']
                    '''... ...'''
                
                print('done item ' + itemid +  ', page ' + str(currentpage))
                currentpage = currentpage + 1
                
            except json.JSONDecodeError as e:
                print(f"JSON 解析失败: {e}")
                print(f"尝试解析的内容: {json_str[:200] if 'json_str' in locals() else rtext[:200]}")
                break
            except KeyError as e:
                print(f"JSON 结构缺少字段: {e}")
                print(f"JSON 内容: {json.dumps(rjson, ensure_ascii=False, indent=2)[:500]}")
                break
            except Exception as e:
                print(f"处理数据时出错: {e}")
                import traceback
                traceback.print_exc()
                break

spider = ReviewSpider()
spider.getReview('2089100916', '537174397861')