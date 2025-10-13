from typing import Union
def lt_check_body( body : Union[str, None]) -> tuple[str, str]:
    if body is None:
        return "{}", "not_have_resource"
    body_info = ""
    start = body.find("mtopjsonp")
    if start>-1:
        body = body[start+body.find("("):-1].replace("({","{",1)
    deny_flag = body.find("action=deny")>-1 or body.find("pureDenyWait=")> -1 or body.find("bixi") > -1
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

def pc_check_body(body : Union[str, None]) -> tuple[str, str]:
    if body is None:
        return "{}", "not_have_resource"
    body_info = ""
    start = body.find("mtopjsonp")
    if start>-1:
        body = body[start+body.find("("):-1].replace("({","{",1)
    start = body.find('loaderData":')
    if start>-1:
        end = body.find(',"routePath')
        body = body[start+12:end]
    deny_flag = body.find("action=deny")>-1 or body.find("pureDenyWait=")> -1
    slide_flag = body.find("punish?x5secdata")>-1
    noitem_flag = body.find("noitem")>-1
    login_flag = body.find("login.jhtml")>-1 or body.find("login.htm")>-1 or body.find(
"登录查看更多优惠")>-1
    success_flag = body.count("sku2info") >= 1
    if login_flag:
        body_info = "login"
    elif success_flag :
        body_info = "success"
    elif noitem_flag:
        body_info = "noitem"
    elif len(body)<10:
        body_info = "not_have_resources"
    elif deny_flag: 
        body_info = "deny"
    elif slide_flag: 
        body_info = "slide"
    else:
        body_info = "success"
    return body, body_info

def check_body( body : Union[str, None], task_type : str) -> tuple[str, str]:
    if task_type == "LT_TAOBAO":
        return lt_check_body(body)
    elif task_type == "CART_TAOBAO":
        return pc_check_body(body)
    else:
        return pc_check_body(body)