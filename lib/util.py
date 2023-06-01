# -*- coding: UTF-8 -*-

import requests
import re
import string
import random
import json
import damatuWeb
import sys

'''
JSESSIONID seems to be the only useful cookie.
SERVERID has some thing to do with haproxy load balance
'''

code = 'utf-8'
if "win" in sys.platform and "darwin" not in sys.platform:
    code = 'gb2312'

def getAccountAndPwdFromFile():
    CONFIG_FILE_PATH='./bin/C2C/conf.txt'
    account,pwd='',''
    with open(CONFIG_FILE_PATH,'r')as fd:
        for line in fd.readlines():
            if line.startswith('account:'):
                account=line.strip('\n')[len('account:'):]
            if line.startswith('pwd:'):
                pwd=line.strip('\n')[len('pwd:'):]
        assert account!='' and pwd!=''
        return (account,pwd)

def getCookieFromSetCookieHeader(setCookieString):
    '''
    :param setCookieString: JSESSIONID=81B80747DF30BCEE42436F82E19028A9; Path=/; HttpOnly, SERVERID=e56f46ad407ad71d2240e0d95124923c|1520413364|1520413364;Path=/
    :return:
    '''
    cookieDic={}
    cookies=setCookieString.split(',')
    for cookie in cookies:
        key=cookie.split(';')[0].strip(' ').split('=')[0]
        value=cookie.split(';')[0].strip(' ').split('=')[1]
        cookieDic[key]=value
    return cookieDic

def isLoginSucceed(response,account):
    data=json.loads(response)
    if data["code"]==1 and data["data"]["mobile"]==account:
        return True
    elif data["code"]==0 and data["msg"]==u"验证码不正确":
        return False
    elif data["code"]==0 and data["msg"]==u"密码错误":
        raise Exception(u"登录{account}时密码错误！请检查！".format(account=account).encode(code))
    else:
        cod=data["code"]
        msg=data["msg"]
        errStr=u"登录{account}时遇到未知错误，code:{code},msg:{msg}".format(code=cod,msg=msg,account=account)
        raise Exception(errStr.encode(code))


def login(account,pwd,captcha,session):
    paramsPost = {"code": captcha, "pwd": pwd, "account": account}
    headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0",
               "Referer": "https://www.bbaex.com/", "Connection": "close",
               "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
               "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

    response = session.post("https://www.bbaex.com/users/login", data=paramsPost, headers=headers)

    print("Status code:   %i" % response.status_code)
    print("Response body: %s" % response.content)
    if(isLoginSucceed(response.content,account)):
        print("congratulations, login succeed!")
        return session
    else:
        print("sorry, code error!")
        return None

def saveCaptchaPic(session):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0",
               "Referer": "https://www.bbaex.com/", "Connection": "close",
               "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2", "Accept": "*/*"}

    loginURL='https://www.bbaex.com/#/login'
    response=session.get(loginURL,headers=headers)

    paramsGet = {"0.29702075400577277": ""}
    response = session.get("https://www.bbaex.com/code", params=paramsGet, headers=headers)

    print("try getting the captcha pic... Status code:   %i" % response.status_code)
    picFilePath='pics/code.jpeg'
    with open(picFilePath,'wb')as fd:
        fd.write(response.content)
    return picFilePath

def identifyCaptcha(picFilePath):
    dmt = damatuWeb.DamatuApi("daladala32711", "hehedala123!@#")
    print("dm2 balance:"+dmt.getBalance())
    captcha=dmt.decode(picFilePath,92399)
    captcha = str(captcha).encode('utf-8').lower()
    print("captcha is :"+captcha)
    return captcha

def loginAndReturnSession(account,pwd):
    session =  requests.Session()
    picFilePath=saveCaptchaPic(session)
    print("captcha file saved to:"+picFilePath)
    captcha=identifyCaptcha(picFilePath)
    print("try logging in......")
    session = login(account,pwd,captcha,session)
    if not session:
        return loginAndReturnSession(account,pwd)
    return session

if __name__ == '__main__':
    account='17612345678'
    pwd='bbaex123$%^'
    loginAndReturnSession(account,pwd)


