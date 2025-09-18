from typing import Union
def check_body( body : Union[str, None]) -> tuple[str, str]:
    if body is None:
        return "{}", "not_have_resource"
    body_info = ""
    start = body.find("mtopjsonp")
    if start>-1:
        body = body[start+body.find("("):-1].replace("({","{",1)
    deny_flag = body.find("action=deny")>-1 or body.find("pureDenyWait=")> -1
    deny2_flag = body.find(u"立即登录")>-1
    slide_flag = body.find("action=captcha")>-1 
    login_flag = body.find('"popData":{}')>-1 or body.find("login.jhtml")>-1 or body.find("window.location.href")>-1 or body.find(u"立即登录")>-1
    if body.count("sku2info")>0:
        body_info = "success"
    elif deny_flag: 
        body_info = "deny"
    elif deny2_flag: 
        body_info = "login"
    elif slide_flag: 
        body_info = "slide"
    elif len(body) < 1000:
        body_info = "noitem"
    elif login_flag:
        body_info = "login"
    else:
        body_info = "success"
    return body, body_info