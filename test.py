import asyncio
import random
from curl_cffi.requests import AsyncSession
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'priority': 'u=0, i',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}
login_url = "https://login.taobao.com/jump?target=https%3A%2F%2Flogin.1688.com%2Fmember%2Fpop_signin_route.htm%3Ffrom%3Dhttps%253A%252F%252Fwww.1688.com%252F"

cookie = ""
headers['cookie'] = cookie
headers['referer'] = f'https://login.taobao.com/member/login.jhtml?lang=zh_cn&appName=taobao&appEntrance=default&styleType=vertical&bizParams=&notLoadSsoView=false&notKeepLogin=false&isMobile=false&iframeUUID=havana_d42ea9&from=b2b_pop_new&style=b2b&newMini2=true&full_redirect=false&reg=http%3A%2F%2Fmember.1688.com%2Fmember%2Fjoin%2Fenterprise_join.htm&redirectURL=https%3A%2F%2Flogin.taobao.com%2Fjump%3Ftarget%3Dhttps%253A%252F%252Flogin.1688.com%252Fmember%252Fpop_signin_route.htm%253Ffrom%253Dhttps%25253A%25252F%25252Fwww.1688.com%25252F&rnd={random.random()}'
async def run():
    async with AsyncSession() as session:
        response = await session.get(login_url, headers=headers)
        print(response.text)
        print(response.headers)

if __name__ == "__main__":
    asyncio.run(run())