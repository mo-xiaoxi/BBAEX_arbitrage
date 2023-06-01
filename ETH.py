#/usr/bin/env python
#-*-coding:utf-8-*-
import gevent
from gevent import monkey,pool; monkey.patch_all()
from gevent import Timeout
import json
import time
import threading
import os
import signal
import time
from lib.common import *

trade_to_ID ={
	 "CXC-ETH":"18",
	 "BBB-ETH":"38",
	 "ICX-ETH":"21",
	 "LRC-ETH":"22",
	 "SNT-ETH":"20",
	 "TRX-ETH":"19",
	 "BTM-ETH":"23",
	 "BAT-ETH":"3",
	 "OMG-ETH":"24",
	 "AION-ETH":"35",
	 "DNT-ETH":"25",
	 "KNC-ETH":"26", 
	 "CREDO-ETH":"27",
	 "FUEL-ETH":"28",
	 "POE-ETH":"29",
	 "VEN-ETH":"36",
	 "CND-ETH":"30",
	 "MANA-ETH":"32",
	 "CDT-ETH":"31",
	 "EOS-ETH":"39",
	 "AST-ETH":"40",     
	 "EVX-ETH":"41",
	 "AE-ETH":"42",
	 "ZRX-ETH":"43",
	 "GNT-ETH":"44",
	 "ZIL-ETH":"45",
	 "ELF-ETH":"46",
	 "FUN-ETH":"47",
	 "NAS-ETH":"48",
	 "SALT-ETH":"49",
	 "POWR-ETH":"50",
	 "LINK-ETH":"51",
	 "BNT-ETH":"52",
	 "ENG-ETH":"53",
	 "REQ-ETH":"54",
	 "PAY-ETH":"55",
	 "RDN-ETH":"56",
	 "STORJ-ETH":"57",
	 "MTL-ETH":"58",
	 "DDN-ETH":"59"
 }


trade_to_index = {
	 "CXC-ETH":"0",
	 "BBB-ETH":"1",
	 "DDN-ETH":"2",
	 "XAS-ETH":"3",
	 "NULS-ETH":"4",
	 "ICX-ETH":"5",
	 "LRC-ETH":"6",
	 "SNT-ETH":"7",
	 "TRX-ETH":"8",
	 "BTM-ETH":"9",
	 "BAT-ETH":"10",
	 "OMG-ETH":"11",
	 "AION-ETH":"12",
	 "DNT-ETH":"13",
	 "KNC-ETH":"14",
	 "CREDO-ETH":"15",
	 "FUEL-ETH":"16",
	 "POE-ETH":"17",
	 "VEN-ETH":"18",
	 "CND-ETH":"19",
	 "MANA-ETH":"20",
	 "CDT-ETH":"21",
	 "EOS-ETH":"22",
	 "AST-ETH":"23",
	 "EVX-ETH":"24",
	 "AE-ETH":"25",
	 "ZRX-ETH":"26",
	 "GNT-ETH":"27",
	 "ZIL-ETH":"28",
	 "ELF-ETH":"29",
	 "FUN-ETH":"30",
	 "NAS-ETH":"31",
	 "SALT-ETH":"32",
	 "POWR-ETH":"33",
	 "LINK-ETH":"34",
	 "BNT-ETH":"35",
	 "ENG-ETH":"36",
	 "REQ-ETH":"37",
	 "PAY-ETH":"38",
	 "RDN-ETH":"39",
	 "STORJ-ETH":"40",
	 "MTL-ETH":"41"
}

trade_min_accuracy =  0.00000001




	
	

class ETH():
	def __init__(self, session, tra_pwd, trade, rank, yesterday):
		self.s = session
		self.tra_pwd = tra_pwd
		self.trade = trade 
		self.rank = int(rank)
		self.yesterday = int(yesterday)
		self.recount = 0
		self.event = threading.Event()
		self.MarketCoinId = trade_to_ID[trade]
		# print(self.__dict__)
	
	def init_rank(self):
		if self.yesterday:
			self.trading_volume = self.get_trading_volume_yesterday()
		else:
			self.trading_volume = self.get_trading_volume()



	def init_interval(self, price, factor=0.5):
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.s.post("https://www.bbaex.com/users/center", headers=headers)
		data = json.loads(response.content)
		coins = data['data']['coins']
		coinName = self.trade.split('-')[0]
		for coin in coins:
			if coin['coinName'] == coinName:
				result_sell = coin['count']	
		# ETH数量
		eth = coins[2]['count']
		result_buy = eth/price
		count = min(float(result_sell),float(result_buy))
		result = float(count)*float(factor)
		log.info(u"可交易币数量{0},我们设定单次交易数量为{1}".format(count,result))
		return result



	def log_content(self, data):
		print(data)
		try:
			data = json.loads(data)
			log.info(data['msg'])
			if data['msg'] != '':
				log.warn(u"可能出现了错误，为了安全，我们进入撤单退出机制...")
				# 出现错误，通知主进程进行撤单操作
				self.event.set()
		except Exception as e:
			print(e)
		return 


	def get_trading_volume_yesterday(self):
		'''
		不减去已刷数量，只适合第一次刷
		'''
		log.info(u'从昨日数据获得待刷量，但检测现已刷数量，因此只适合第一次刷，请注意！!')
		data = get_yesterday_data()
		index = int(trade_to_index[self.trade])
		coin = data[0]['coins'][index]
		coinEname = coin['coinEname']
		log.info(u"要刷的币种{0},实际的币种{1}".format(self.trade,coinEname))
		havedone = self.get_havedone()
		ranks = coin['ranks']
		count = len(ranks)
		if count > self.rank:
			trading_volume = ranks[self.rank]['tradeVolume']
		else:
			try:
				trading_volume = float(ranks[-1]['tradeVolume'])
			except Exception as e:
				# DDN没有交易数据
				trading_volume = 1.0
		trading_volume -= havedone
		log.info(u"以昨日的排名情况进行参考，刷到{0}名，需刷交易量为{1}".format(self.rank,trading_volume))
		return trading_volume


	def get_havedone(self):
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.s.get("https://www.bbaex.com/tradeRank", headers=headers)
		data = json.loads(response.content)
		# print("Account:{0}")
		index = int(trade_to_index[self.trade])
		# ETH
		coin = data['data']['markets'][0]['coins'][index]
		coinEname = coin['coinEname']
		try:
			myrank = coin['myRank']
			myReward = coin['myReward']
			havedone = int(coin['ranks'][myrank]['tradeVolume'])
			log.info(u"此时排名为{0},奖励为{1}BBB,已刷交易量为{2}".format(myrank,myReward,havedone))
		except Exception as e:
			print(e)
			log.info(u"还未刷单,未有排名及奖励")
			havedone = 0
		return havedone


	def get_trading_volume(self):
		'''
		查询获得对应排名的交易量
		'''

		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.s.get("https://www.bbaex.com/tradeRank", headers=headers)
		data = json.loads(response.content)
		# print("Account:{0}")
		index = int(trade_to_index[self.trade])
		# ETH
		coin = data['data']['markets'][0]['coins'][index]
		coinEname = coin['coinEname']
		log.info(u"要刷的币种{0},实际的币种{1}".format(self.trade,coinEname))
		try:
			myrank = coin['myRank']
			myReward = coin['myReward']
			havedone = coin['ranks'][myrank]['tradeVolume']
			log.info(u"此时排名为{0},奖励为{1}BBB,已刷交易量为{2}".format(myrank,myReward,havedone))
		except Exception as e:
			print(e)
			log.info(u"还未刷单,未有排名及奖励")
			havedone = 0
		
		try:		
			ranks = coin['ranks']
			count = len(ranks)
			log.info(u"已有前{0}人进行刷单,我们需刷进前{1}名".format(count,self.rank))
			log.info(u"其中最后一名的交易额为{0}".format(ranks[-1]['tradeVolume']))
			if count > self.rank:
				trading_volume = float(ranks[self.rank]['tradeVolume']) - float(havedone)
			else:
				try:
					trading_volume = float(ranks[-1]['tradeVolume']) - float(havedone)
				except Exception as e:
					# DDN没有交易数据
					trading_volume = 1
			log.info(u"待刷交易量为{0}".format(trading_volume))
			return trading_volume
		except Exception as e:
			print(e)
			log.info(u"无排行榜信息")
			return 0

	
	def check_state(self):
		'''
		检测是否有未成交的订单
		'''
		paramsGet = {"top":"1"}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.s.get("https://www.bbaex.com/markets/"+self.MarketCoinId, params=paramsGet, headers=headers)
		top = json.loads(response.content)
		mys = top['data']['mys']
		if len(mys)>0:
			log.info(u"最近的交易仍未成交，请等待...")
			self.recount+=1
			if self.recount>1:
				log.warn(u"1s仍未成交，撤销所有买卖单")
				for my in mys:
					trade_id = my['id']
					self.cancel(trade_id)
			time.sleep(1)
			return self.check_state()		
		self.recount = 0
		log.info(u'订单检测成功...')
		return True


	def get_price(self):
		'''
		获得价格
		'''
		paramsGet = {"top":"1"}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.s.get("https://www.bbaex.com/markets/"+self.MarketCoinId, params=paramsGet, headers=headers)
		top = json.loads(response.content)
		public_price = get_public_price(self.trade)
		try:
			best_sell_price = top['data']['sells'][0]['price'] 
		except Exception as e:
			print('no best_sell_price...')
			best_sell_price = public_price*1.1
		try:
			best_buy_price = top['data']['buys'][0]['price']
		except Exception as e:
			print('no best_buy_price....')
			best_buy_price = public_price*0.9
		best_price = caculate_best_price(best_buy_price,best_sell_price,public_price,trade_min_accuracy)
	
		if best_price==best_sell_price or best_price==best_buy_price:
			log.warn(u'买卖差距过小，无法刷单,buy{0},sell{1},now{2}'.format(best_buy_price,best_sell_price,best_price))
			log.warn(u'程序退出')
			os._exit(1)
		print("best_sell_price:{0},best_buy_price:{1},public_price:{2},best_price:{3}".format(best_sell_price,best_buy_price,public_price,best_price))
		return best_price


	def cancel_all(self):
		'''
		检测挂单，撤销所有
		'''
		paramsGet = {"top":"10"}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.s.get("https://www.bbaex.com/markets/"+self.MarketCoinId, params=paramsGet, headers=headers)
		top = json.loads(response.content)
		try:
			mys = top['data']['mys']
			for my in mys:
				trade_id = my['id']
				self.cancel(trade_id)
		except Exception as e:
			print(e)
		print('Cancel All Order send succ!')

	def exit(self):
		self.cancel_all()
		print('demo exit...')



	def cancel(self, trade_id):
		'''
		撤销所有买卖单
		'''
		paramsPost = {"id":trade_id}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1","Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}
		response = self.s.post("https://www.bbaex.com/marketEntrusts/cancel", data=paramsPost, headers=headers)
		if response.status_code==200:
			print("Cancel Order send succ!")
			self.log_content(response.content)
			self.now -= 2*float(self.interval)
		else:
			print(response.status_code)
			self.log_content(response.content)



	def buy(self, price):
		paramsPost = {"count":self.interval,"tradePwd":self.tra_pwd,"marketCoinId":self.MarketCoinId,"price":price}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1","Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}
		response = self.s.post("https://www.bbaex.com/markets/buys", data=paramsPost, headers=headers)
		if response.status_code==200:
			print("buy Order send succ!")
			self.log_content(response.content)
		else:
			print(response.status_code)
			self.log_content(response.content)		
		return True

	def sell(self, price):
		paramsPost = {"count":self.interval,"tradePwd":self.tra_pwd,"marketCoinId":self.MarketCoinId,"price":price}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1","Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}
		response = self.s.post("https://www.bbaex.com/markets/sells", data=paramsPost, headers=headers)
		if response.status_code==200:
			print("sell succ!")
			self.log_content(response.content)
		else:
			print(response.status_code)
			self.log_content(response.content)

		return True
	
	def get_info(self):
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","Cache-Control":"max-age=0","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.s.get("https://www.bbaex.com/users/info", headers=headers)

		print("Status code:   %i" % response.status_code)
		print("Response body: %s" % response.content)


	def hack(self):
		self.init_rank()
		self.now = 0.0
		while self.now < float(self.trading_volume):
			if self.check_state():
				price = self.get_price()
				self.interval = self.init_interval(price)
			self.now += 2*float(self.interval)
			t1 = threading.Thread(target=self.sell,args=(price,))
			t2 = threading.Thread(target=self.buy,args=(price, ))
			t1.setDaemon(True)
			t2.setDaemon(True)
			t1.start()
			t2.start()
			t1.join()
			t2.join()
			if self.event.is_set():
				self.cancel_all()
				os._exit(-1)
			log.info(u'交易对{0},成交价格为{1}CNY, 需完成交易量{2},已完成交易量: {3}'.format(self.trade,price,self.trading_volume,self.now))





def handler(signal_num,frame):
	print("\nYou Pressed Ctrl-C.") 
	global demo
	try:
		demo.exit()
	except Exception as e:
		print(e)
		pass
	os._exit(signal_num)


if __name__ == '__main__':
	base = read_conf('conf/base.json')
	accounts = base['accounts']
	config = read_conf('conf/eth.json')
	uid = config['uid']
	trades = config['Trades']
	mobile = accounts[uid]['mobile']
	password = accounts[uid]['password']
	tra_pwd = accounts[uid]['tra_pwd']
	signal.signal(signal.SIGINT, handler)
	# print config
	filename = 'data/' + uid + '_eth.log'
	log = init_log(filename)
	log.warn(u"账户:{0},UID:{1}".format(mobile, uid))
	session = login(mobile, password)
	recount = 0

	while True:
		recount+=1
		log.warn(u"账户:{0},UID:{1}，第{2}次刷单".format(mobile,uid,recount))
		demos=[]
		jobs=[]
		timer= Timeout(60*30).start()#每个协程执行最多30分钟
		p = pool.Pool(10)
		gevent.signal(signal.SIGINT, exit)

		for trade in config['Trades']:
			print('*' * 50)
			if int(trade['pass']) == 1:
				log.info(u'{0}交易对设定为pass，跳过该交易对'.format(trade['trade']))
				continue
			log.info(u'开始刷交易对{0}'.format(trade['trade']))
			demo = ETH(session, tra_pwd, trade['trade'], trade['rank'], trade['yesterday'])
			demos.append(demo)
			jobs.append(p.spawn(demo.hack()))
		try:
			gevent.joinall(jobs, timeout=timer)  # wait all jobs done
		except Timeout:
			logging.error(u"可能由于网络延迟,刷单未完成...".encode(code))
		except Exception as e:
			logging.error(e)
		log.info(u'程序执行完毕，进入退出机制'.encode(code))
		#demo.exit()
