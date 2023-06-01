#-*-coding:utf-8-*-
import datetime
import sys, hashlib, os, random, urllib, urllib2,json
from datetime import *
import time
import re
import requests

code = 'utf-8'
if "win" in sys.platform and "darwin" not in sys.platform:
    code = 'gb2312'
count = 0

def print_r(data):
	print(data.encode(code))

class APIClient(object):
	'''
	云打码平台接口
	'''
	def http_request(self, url, paramDict):
		post_content = ''
		for key in paramDict:
			post_content = post_content + '%s=%s&'%(key,paramDict[key])
		post_content = post_content[0:-1]
		#print post_content
		req = urllib2.Request(url, data=post_content)
		req.add_header('Content-Type', 'application/x-www-form-urlencoded')
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
		response = opener.open(req, post_content)
		return response.read()

	def http_upload_image(self, url, paramKeys, paramDict, filebytes):
		timestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		boundary = '------------' + hashlib.md5(timestr).hexdigest().lower()
		boundarystr = '\r\n--%s\r\n'%(boundary)

		bs = b''
		for key in paramKeys:
			bs = bs + boundarystr.encode('ascii')
			param = "Content-Disposition: form-data; name=\"%s\"\r\n\r\n%s"%(key, paramDict[key])
			#print param
			bs = bs + param.encode('utf8')
		bs = bs + boundarystr.encode('ascii')

		header = 'Content-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: image/gif\r\n\r\n'%('sample')
		bs = bs + header.encode('utf8')

		bs = bs + filebytes
		tailer = '\r\n--%s--\r\n'%(boundary)
		bs = bs + tailer.encode('ascii')


		headers = {'Content-Type':'multipart/form-data; boundary=%s'%boundary,
			'Connection':'Keep-Alive',
			'Expect':'100-continue',
			}
		response = requests.post(url, params='', data=bs, headers=headers)
		return response.text



def reporterror(json_id):
	client = APIClient()
	paramDict = {}
	paramDict['username'] = 'm0xiaoxi'
	paramDict['password'] = '5c437035eb87f482a9c34b479d2f5ee0'
	paramDict['id'] = json_id
	paramDict['softid'] = 67968
	paramDict['softkey'] = '94a402a488a649c5acbee3f980add733'
	result = client.http_request('http://api.ysdm.net/reporterror.json', paramDict)
	global count
	count+=1
	if count ==3:
		print 'reporterror to much!'
		sys.exit(1)
	return

def identifyCaptcha(picFilePath):
	client = APIClient()
	paramDict = {}
	result = ''
	paramDict['username'] = 'm0xiaoxi'
	paramDict['password'] = '5c437035eb87f482a9c34b479d2f5ee0'
	paramDict['typeid'] = '3040'
	paramDict['timeout'] = '10'
	paramDict['softid'] = 67968
	paramDict['softkey'] = '94a402a488a649c5acbee3f980add733'
	paramKeys = ['username',
				'password',
				'typeid',
				'timeout',
				'softid',
				'softkey'
				]
	filebytes = open(picFilePath, "rb").read()
	result = client.http_upload_image("http://api.ysdm.net/create.json", paramKeys, paramDict, filebytes)
	data = json.loads(result)
	print_r(result)
	code = str(data['Result']).lower()
	json_id = str(data['Id'])
	if len(code)==4:
		return code,json_id
	reporterror(json_id)
	return None

def isLoginSucceed(response,account,json_id):
    data=json.loads(response)
    if data["code"]==1 and data["data"]["mobile"]==account:
    	global count
    	count = 0
        return True
    elif data["code"]==0 and data["msg"]==u"验证码不正确":
    	print_r(data["msg"])
    	reporterror(json_id)
    	return False
    elif data["code"]==0 and data["msg"]==u"密码错误":
        raise Exception(u"登录{account}时密码错误！请检查！".format(account=account).encode(code))
    else:
        cod=data["code"]
        msg=data["msg"]
        errStr=u"登录{account}时遇到未知错误，code:{code},msg:{msg}".format(code=cod,msg=msg,account=account)
        raise Exception(errStr.encode(code))



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



def login(account,pwd,captcha,session,json_id):
    paramsPost = {"code": captcha, "pwd": pwd, "account": account}
    headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0",
               "Referer": "https://www.bbaex.com/", "Connection": "close",
               "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
               "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

    response = session.post("https://www.bbaex.com/users/login", data=paramsPost, headers=headers)

    print("Status code:   %i" % response.status_code)
    print("Response body: %s" % response.content)
    if(isLoginSucceed(response.content,account,json_id)):
        print("congratulations, login succeed!")
        return session
    else:
        print("sorry, code error !")
        return None

def loginAndReturnSession(account,pwd):
    session =  requests.Session()
    picFilePath=saveCaptchaPic(session)
    print("captcha file saved to:"+picFilePath)
    captcha,json_id=identifyCaptcha(picFilePath)
    print("try logging in......")
    session = login(account,pwd,captcha,session,json_id)
    if not session:
    	return loginAndReturnSession(account,pwd)
    return session

if __name__ == '__main__':
    account='17612345678'
    pwd='bbaex123$%^'
    loginAndReturnSession(account,pwd)