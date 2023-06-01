import hashlib
import requests
import json
import base64

def md5str(str):
		m=hashlib.md5(str)
		return m.hexdigest()
		
def md5(byte):
		return hashlib.md5(byte).hexdigest()
		
class DamatuApi():
	
	ID = '54935'
	KEY = '1a86ecf65a0a73e0d9fe3365f948483e'
	HOST = 'http://api.dama2.com:7766/app/'

	def __init__(self,username,password):
		self.username=username
		self.password=password
		
	def getSign(self,param=b''):
		return (md5(self.KEY+self.username+ param) )[:8]
		
	def getPwd(self):
		return md5str(self.KEY +md5str(md5str(self.username) + md5str(self.password)))
		
	def post(self,path,data={}):
		url = self.HOST + path
		response = requests.post(url,data=data)
		return response.content
	
	def getBalance(self):
		data={'appID':self.ID,
			'user':self.username,
			'pwd':dmt.getPwd(),
			'sign':dmt.getSign()
		}
		res = self.post('d2Balance',data)
		jres = json.loads(res)
		if jres['ret'] == 0:
			return jres['balance']
		else:
			return jres['ret']
    
	def decode(self,filePath,type):
		f=open(filePath,'rb')
		fdata=f.read()
		filedata=base64.b64encode(fdata)
		f.close()
		data={'appID':self.ID,
			'user':self.username,
			'pwd':dmt.getPwd(),
			'type':type,
			'fileDataBase64':filedata,
			'sign':dmt.getSign(fdata)
		}		
		res = self.post('d2File',data)
		jres = json.loads(res)
		if jres['ret'] == 0:
			return(jres['result'])
		else:
			return jres['ret']

	
	def reportError(self,id):
		data={'appID':self.ID,
			'user':self.username,
			'pwd':dmt.getPwd(),
			'id':id,
			'sign':dmt.getSign(id.encode(encoding = "utf-8"))
		}	
		res = self.post('d2ReportError',data)
		jres = json.loads(res)
		return jres['ret']

dmt=DamatuApi("daladala32711","hehedala123!@#")
# print(dmt.getBalance())
#print(dmt.decode('./pics/1.jpeg',92399))
#print(dmt.reportError('894657096'))

