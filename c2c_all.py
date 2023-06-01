#/usr/bin/env python
#-*-coding:utf-8-*-
import gevent
from gevent import monkey,pool; monkey.patch_all()
from gevent import Timeout
from gevent import socket
import requests
import json
import time
import sys
import os
import signal
from lib.common import *

trade_to_ID ={
	 "CXC-CNY":"1",
	 "BBB-CNY":"20",
	 "DDN-CNY":"41",
	 "ETH-CNY":"2",
	 "ICX-CNY":"6",
	 "LRC-CNY":"7",
	 "SNT-CNY":"5",
	 "TRX-CNY":"4",
	 "BTM-CNY":"8",
	 "BAT-CNY":"3",
	 "OMG-CNY":"9",
	 "AION-CNY":"18",
	 "DNT-CNY":"10",
	 "KNC-CNY":"11",
	 "CREDO-CNY":"12",
	 "FUEL-CNY":"13",
	 "POE-CNY":"14",
	 "VEN-CNY":"19",
	 "CND-CNY":"15",
	 "MANA-CNY":"17",
	 "CDT-CNY":"16",
	 "EOS-CNY":"21",
	 "AST-CNY":"22",
	 "EVX-CNY":"23",
	 "AE-CNY":"24",
	 "ZRX-CNY":"25",
	 "GNT-CNY":"26",
	 "ZIL-CNY":"27",
	 "ELF-CNY":"28",
	 "FUN-CNY":"29",
	 "NAS-CNY":"30",
	 "SALT-CNY":"31",
	 "POWR-CNY":"32",
	 "LINK-CNY":"33",
	 "BNT-CNY":"34",
	 "ENG-CNY":"35",
	 "REQ-CNY":"36",
	 "PAY-CNY":"37",
	 "RDN-CNY":"38",
	 "STORJ-CNY":"39",
	 "MTL-CNY":"40"
	}


trade_to_index = {
	"CXC-CNY":"0",
	"BBB-CNY":"1",
	"DDN-CNY":"2",
	"ETH-CNY":"3",
	"XAS-CNY":"4",
	"NULS-CNY":"5",
	"ICX-CNY":"6",
	"LRC-CNY":"7",
	"SNT-CNY":"8",
	"TRX-CNY":"9",
	"BTM-CNY":"10",
	"BAT-CNY":"11",
	"OMG-CNY":"12",
	"AION-CNY":"13",
	"DNT-CNY":"14",
	"KNC-CNY":"15",
	"CREDO-CNY":"16",
	"FUEL-CNY":"17",
	"POE-CNY":"18",
	"VEN-CNY":"19",
	"CND-CNY":"20",
	"MANA-CNY":"21",
	"CDT-CNY":"22",
	"EOS-CNY":"23",
	"AST-CNY":"24",
	"EVX-CNY":"25",
	"AE-CNY":"26",
	"ZRX-CNY":"27",
	"GNT-CNY":"28",
	"ZIL-CNY":"29",
	"ELF-CNY":"30",
	"FUN-CNY":"31",
	"NAS-CNY":"32",
	"SALT-CNY":"33",
	"POWR-CNY":"34",
	"LINK-CNY":"35",
	"BNT-CNY":"36",
	"ENG-CNY":"37",
	"REQ-CNY":"38",
	"PAY-CNY":"39",
	"RDN-CNY":"40",
	"STORJ-CNY":"41",
	"MTL-CNY":"42"
}

C2C_min = {
	"CXC-CNY":"100",
	"BBB-CNY":"50",
	"ETH-CNY":"0.015",
	"ICX-CNY":"4",
	"LRC-CNY":"30",
	"SNT-CNY":"68",
	"TRX-CNY":"303",
	"BTM-CNY":"100",
	"BAT-CNY":"32",
	"OMG-CNY":"1",
	"AION-CNY":"4",
	"DNT-CNY":"130",
	"KNC-CNY":"4.5",
	"CREDO-CNY":"540",
	"FUEL-CNY":"140",
	"POE-CNY":"175",
	"VEN-CNY":"3",
	"CND-CNY":"112",
	"MANA-CNY":"140",
	"CDT-CNY":"240",
	"EOS-CNY":"4",
	"AST-CNY":"70",
	"EVX-CNY":"8",
	"AE-CNY":"8",
	"ZRX-CNY":"30",
	"GNT-CNY":"70",
	"ZIL-CNY":"175",
	"ELF-CNY":"8",
	"FUN-CNY":"400",
	"NAS-CNY":"4",
	"SALT-CNY":"4",
	"POWR-CNY":"50",
	"LINK-CNY":"50",
	"BNT-CNY":"5",
	"ENG-CNY":"8",
	"REQ-CNY":"100",
	"PAY-CNY":"12",
	"RDN-CNY":"10",
	"STORJ-CNY":"30",
	"MTL-CNY":"3",
	"DDN-CNY":"100",
	"XAS-CNY":"25",
	"NULS-CNY":"4"

}

class C2C():
	def __init__(self, session, tra_pwd, trade):
		self.session = session
		self.tra_pwd = tra_pwd
		self.trade = trade 
		self.MarketCoinId = trade_to_ID[trade]
		self.recount = 0
		self.oldId = 0
		self.retry_interval = 0

	def cancel_all(self):
		'''
		取消挂单
		'''
		paramsGet = {"pageSize":"10","page":"1","status":"1600001"}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}

		response = self.session.get("https://www.bbaex.com/sellers/my", params=paramsGet, headers=headers)
		data = json.loads(response.content)
		for d in data['data']['rows']:
			trade_id = d['id']
			paramsGet = {"id":trade_id}
			response = self.session.get("https://www.bbaex.com/sellers/cancel", params=paramsGet, headers=headers)
			log.info("Cancel all order send succ!")
			return self.handler_content(response.content)
		return True

	def cancel(self):
		'''
		取消挂单
		'''
		paramsGet = {"pageSize":"10","page":"1","status":"1600001"}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}

		response = self.session.get("https://www.bbaex.com/sellers/my", params=paramsGet, headers=headers)
		data = json.loads(response.content)
		for d in data['data']['rows']:
			trade_id = d['id']
			if int(d['coinId'])== int(self.MarketCoinId):
				paramsGet = {"id":trade_id}
				response = self.isession.get("https://www.bbaex.com/sellers/cancel", params=paramsGet, headers=headers)
				log.info("Cancel order send succ!")
				return self.handler_content(response.content)
		return True


	def buy(self, interval, price, entrustId):
		'''
		购买
		'''
		paramsPost = {"count":interval,"coinId":self.MarketCoinId,"tradePwd":self.tra_pwd,"price":price,"entrustId":entrustId}
		# print(paramsPost)
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1","Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}
		response = self.session.post("https://www.bbaex.com/buys", data=paramsPost, headers=headers)
		log.info("Buy order send succ!")
		return self.handler_content(response.content)
	
	def sell(self, interval, price):
		paramsPost = {"count":interval,"coinId":self.MarketCoinId,"tradePwd":self.tra_pwd,"price":price}
		# print(paramsPost)
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1","Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}
		response = self.session.post("https://www.bbaex.com/sellers", data=paramsPost, headers=headers)
		log.info("Sell order send succ!")
		return self.handler_content(response.content)

	def pay(self,tradeID):
		paramsPost = {"payType":"1700002","id":tradeID}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1","Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}
		response = self.session.post("https://www.bbaex.com/orders/pay", data=paramsPost, headers=headers)
		log.info("Pay order send succ!")
		return self.handler_content(response.content)

	def confirm(self,tradeID):
		gevent.sleep(2)
		paramsPost = {"id":tradeID}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1","Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}
		response = self.session.post("https://www.bbaex.com/orders/receive", data=paramsPost, headers=headers)
		log.info("confirm order succ!")
		return self.handler_content(response.content)


	def get_succ_id_init(self, buyID, sellID, all_flag=False):
		paramsGet = {"pageSize":"10","page":"1","status":"200001,200002"}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.session.get("https://www.bbaex.com/orders", params=paramsGet, headers=headers)
		data = json.loads(response.content)
		tradeID = []
		if not len(data['data']['rows']):
			return tradeID
		for d in data['data']['rows']:
			log.info('buyID:{0},buyName:{1},sellID:{2},sellName:{3},tradeID:{4}-{5}'.format(d['buyId'],d['buyName'].encode(code),d['sellId'],d['sellName'].encode(code),d['coinId'],self.MarketCoinId))
			if all_flag:
				if int(d['buyId']) == int(buyID) and int(d['sellId']) == int(sellID):
					log.info(u'交易对{0},交易匹配成功，将确认付款与收货'.format(self.trade).encode(code))
					tradeID.append(d['id'])
			else:
				if int(d['buyId']) == int(buyID) and int(d['sellId']) == int(sellID) and int(d['coinId'])== int(self.MarketCoinId):
					log.info(u'交易对{0},交易匹配成功，将确认付款与收货'.format(self.trade).encode(code))
					tradeID.append(d['id'])

		if not len(tradeID):
			log.info(u'交易对{0},检测结束，未找到符合条件的订单，..'.format(self.trade).encode(code))
		return tradeID

	def get_succ_id(self, buyID, sellID):
		paramsGet = {"pageSize":"10","page":"1","status":"200001,200002"}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.session.get("https://www.bbaex.com/orders", params=paramsGet, headers=headers)
		data = json.loads(response.content)
		tradeID = []
		if not len(data['data']['rows']):
			log.info(u"交易对{0},等待后台交易匹配...".format(self.trade).encode(code))
			gevent.sleep(1)
			self.recount +=1
			if self.recount > 5:
				log.warn(u"交易对{0},网络延迟过大，退出...".format(self.trade).encode(code))
				return tradeID
			return self.get_succ_id(buyID, sellID)

		for d in data['data']['rows']:
			log.info('buyID:{0},buyName:{1},sellID:{2},sellName:{3},tradeID{4}-{5}'.format(d['buyId'],d['buyName'].encode(code),d['sellId'],d['sellName'].encode(code),d['coinId'],self.MarketCoinId))
			if int(d['buyId']) == int(buyID) and int(d['sellId'])==int(sellID) and  int(d['coinId'])== int(self.MarketCoinId):
				log.info(u'交易对{0},交易匹配成功，将确认付款与收货'.format(self.trade).encode(code))
				tradeID.append(d['id'])
			else:
				log.info(u"交易对{0},检测下一个匹配到的订单".format(self.trade).encode(code))
		if not len(tradeID):
			log.warn(u'交易对{0},检测结束，未找到符合条件的订单，请手动确认被截胡的交易单..'.format(self.trade).encode(code))
			self.cancel()
		return tradeID



	def get_trading_volume_yesterday(self, rank):
		rank = int(rank)
		log.info(u'交易对{0},从昨日数据获得待刷量'.format(self.trade).encode(code))
		data = get_yesterday_data()
		index = int(trade_to_index[self.trade])
		coin = data[1]['coins'][index]
		coinEname = coin['coinEname']+'-CNY'
		assert(self.trade==coinEname)
		log.info(u"要刷的币种{0},实际的币种{1}".format(self.trade,coinEname).encode(code))
		havedone = self.get_havedone(rank)
		ranks = coin['ranks']
		count = len(ranks)
		if count > rank:
			trading_volume = float(ranks[rank]['tradeVolume']) - float(havedone)
		else:
			trading_volume = float(ranks[-1]['tradeVolume']) - float(havedone)
		log.info(u"交易对{0},以昨日的排名情况进行参考，刷到{1}名，需刷交易量为{2}".format(self.trade,rank,trading_volume).encode(code))
		return trading_volume


	def get_havedone(self,rank):
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.session.get("https://www.bbaex.com/tradeRank", headers=headers)
		data = json.loads(response.content)
		index = int(trade_to_index[self.trade])
		# C2C
		coin = data['data']['markets'][1]['coins'][index]
		coinEname = coin['coinEname']+'-CNY'
		assert(self.trade==coinEname)
		try:
			myrank = coin['myRank']
			myReward = coin['myReward']
			havedone = float(coin['ranks'][myrank]['tradeVolume'])
			log.info(u"交易对{0},此时排名为{1},奖励为{2}BBB".format(self.trade,myrank,myReward).encode(code))
		except Exception as e:
			log.info(e)
			log.info(u"交易对{0},还未刷单,未有排名及奖励".format(self.trade).encode(code))
			havedone = 0.0
		return havedone

	def get_trading_volume(self, rank):
		rank = int(rank)
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.session.get("https://www.bbaex.com/tradeRank", headers=headers)
		data = json.loads(response.content)
		index = int(trade_to_index[self.trade])
		# C2C
		coin = data['data']['markets'][1]['coins'][index]
		coinEname = coin['coinEname']+'-CNY'
		assert(self.trade==coinEname)
		log.info(u"要刷的币种{0},实际的币种{1}".format(self.trade,coinEname).encode(code))
		try:
			myrank = coin['myRank']
			myReward = coin['myReward']
			havedone = float(coin['ranks'][myrank]['tradeVolume'])
			log.info(u"交易对{0},此时排名为{1},奖励为{2}BBB".format(self.trade,myrank,myReward).encode(code))
		except Exception as e:
			log.info(e)
			log.info(u"交易对{0},还未刷单,未有排名及奖励".format(self.trade).encode(code))
			havedone = 0.0
	
		trans_interval = 2*float(self.get_interval()) #减去转移币的交易额

		try:		
			ranks = data['data']['markets'][1]['coins'][index]['ranks']
			count = len(ranks)
			log.info(u"交易对{0},已有前{1}人进行刷单,我们需刷进前{2}名".format(self.trade,count,rank).encode(code))
			log.info(u"交易对{0},其中最后一名的交易额为{1}".format(self.trade,ranks[-1]['tradeVolume']).encode(code))
			max_volume = get_max_volume(self.trade,rank)
			if count > rank:
				tradeVolume = min(float(ranks[rank]['tradeVolume']),max_volume*0.9)
				trading_volume = tradeVolume - float(havedone) - float(trans_interval)
			else:
				tradeVolume = min(float(ranks[rank]['tradeVolume']),max_volume*0.9)
				trading_volume = tradeVolume - float(havedone) - float(trans_interval)

			log.info(u"交易对{0},待刷交易量为{1}".format(self.trade,trading_volume).encode(code))
			return trading_volume
		except Exception as e:
			log.warn(e)
			log.warn(u"交易对{0},无排行榜信息".format(self.trade))
			return 0

	def get_trade(self):
		return self.trade

	def get_price(self):
		paramsGet = {"top":"10","coinId":self.MarketCoinId}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.session.get("https://www.bbaex.com/coins/detail", params=paramsGet, headers=headers)
		top = json.loads(response.content)
		public_price = get_public_price(self.trade)
		sells = top['data']['sells']
		if len(sells)>7:
			top_price = sells[-2]['price']
			for i in range(len(sells)-1,-1,-1):
				if sells[i]['price'] < top_price:
					best_price = float(sells[i]['price'])
					break
				if i==0:
					best_price = float(sells[i]['price'])*0.98
		else:
			best_price = public_price*2.0
		log.info(u'交易对{0},public_price:{1},best_price:{2}'.format(self.trade,public_price,best_price).encode(code))
		assert(float(best_price)>=float(public_price)*0.8)
		return best_price

	def get_interval(self, c2c=True):
		'''
		单次成交数量
		'''
		paramsGet = {"coinId":self.MarketCoinId}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/index.html","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.session.get("https://www.bbaex.com/coins/balance", params=paramsGet, headers=headers)
		data = json.loads(response.content)
		result_sell = data['data']['count']
		result_min = C2C_min[self.trade]
		if float(result_min) > float(result_sell):
			self.retry_interval += 1
			log.warn(u'交易对{0},现拥有币种不足，第{1}次检测...'.format(self.trade,self.retry_interval).encode(code))
			if self.retry_interval < 3:
				return self.get_interval()
			self.retry_interval = 0
			log.warn(u"交易对{0},拥有币种数量不足以进行C2C交易,跳过该交易对...".format(self.trade).encode(code))
			return 0
		# 价格为最小数量，或现有数量
		if c2c:
			result = float(result_min)
		else:
			result = max(float(result_min),float(result_sell))
		log.info(u"交易对{0},可交易币数量{1},我们设定单次交易数量为{2}".format(self.trade,result_sell,result).encode(code))
		self.retry_interval = 0
		return result

	def get_sell_id(self, sellId):
		paramsGet = {"top":"10","coinId":self.MarketCoinId}
		headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
		response = self.session.get("https://www.bbaex.com/coins/detail", params=paramsGet, headers=headers)
		top = json.loads(response.content)
		sells = top['data']['sells']
		for sell in sells:
			if int(sell['sellId']) == int(sellId) and int(sell['coinId'])== int(self.MarketCoinId):
				return sell['id']
		gevent.sleep(1)
		log.info(u'交易对{0},没有发现sellID,请等待...'.format(self.trade).encode(code))
		self.get_sell_id(sellId)

	
	def get_entrustId(self, sellId):
		log.info(u'交易对{0},等待卖单上榜...'.format(self.trade).encode(code))
		entrustId = 0
		while not entrustId or self.oldId==entrustId:
			entrustId = self.get_sell_id(sellId)
		self.oldId = entrustId
		return entrustId


	def handler_content(self,data):
		log.info(data)
		try:
			data = json.loads(data)
			log.warn(data['msg'])
			if data['msg'] != '':
				log.error('*'*100)
				log.error(u"交易对{0}可能出现了错误，为了安全，我们进入撤单退出机制...".format(self.trade).encode(code))
				log.error(u"错误信息为{0}".format(data['msg']).encode(code))
				log.error('*'*100)
				self.cancel()
				return False
		except Exception as e:
			log.debug(e)
		return True


def c2c_check_security(demo,uid):
	'''
	进入与退出处理,撤销挂单，确认正在进行中的订单
	'''
	log.info(u'c2c进入安全检测机制...'.encode(code))
	demo.cancel()
	log.info(u'c2c撤单结束,开始确认机制...'.encode(code))
	tradeID = demo.get_succ_id_init(uid,uid)
	for i in tradeID:
		demo.pay(i)
		demo.confirm(i)
	log.info(u'c2c安全机制执行完毕...'.encode(code))
	return True


def c2c_rank_one(demo, rank, yesterday,uid):
	# 初始化状态
	c2c_check_security(demo,uid)
	if int(yesterday):
		trading_volume = demo.get_trading_volume_yesterday(int(rank))
	else:
		trading_volume = demo.get_trading_volume(int(rank))
	trading_volume = float(trading_volume)
	i = 0.0
	price = 0.0
	while i < trading_volume:
		interval = float(demo.get_interval())
		if interval <= 0:
			log.error(u'交易对{0}刷单失败，成交价格为{1}CNY, 需完成交易量{2},已完成交易量: {3},持有币种数量过少'.format(demo.trade,price,trading_volume,i).encode(code))
			break
		price = demo.get_price()
		if not demo.sell(interval, price):
			log.error(u'交易对{0}刷单失败，成交价格为{1}CNY, 需完成交易量{2},已完成交易量: {3},售出失败'.format(demo.trade,price,trading_volume,i).encode(code))
			break
		entrustId = demo.get_entrustId(uid)
		if not demo.buy(interval, price,entrustId):
			log.error(u'交易对{0}刷单失败，成交价格为{1}CNY, 需完成交易量{2},已完成交易量: {3},购买失败'.format(demo.trade,price,trading_volume,i).encode(code))
			break
		tradeID = demo.get_succ_id(uid,uid)
		if not len(tradeID):
			log.error(u'此次交易被截胡，未完成刷单,继续下一次'.encode(code))
			break
		for j in tradeID:
			flag1 = demo.pay(j)
			flag2 = demo.confirm(j)
			if flag1 and flag2:
				i += 2*interval
				log.warn(u'交易对{0},成交价格为{1}CNY, 需完成交易量{2},已完成交易量: {3}'.format(demo.trade,price,trading_volume,i).encode(code))
			else:
				log.error(u'交易对{0}刷单失败，成交价格为{1}CNY, 需完成交易量{2},已完成交易量: {3},付款或确认失败'.format(demo.trade,price,trading_volume,i).encode(code))
				break
	log.warn('*'*100)
	if i>=trading_volume:
		log.warn(u"请务必关注该信息，出现该信息表明该交易对刷单完成...".encode(code))
		log.warn(u'交易对{0},成交价格为{1}CNY, 需完成交易量{2},已完成交易量: {3}'.format(demo.trade,price,trading_volume,i).encode(code))
	else:
		log.error(u"请务必关注该信息，刷单失败！...".encode(code))
		log.error(u'交易对{0},成交价格为{1}CNY, 需完成交易量{2},已完成交易量: {3}'.format(demo.trade,price,trading_volume,i).encode(code))
	log.warn('*'*100)
	c2c_check_security(demo,uid)
	return True

def trans_check_security(demo_now, uid_now, demo_next, uid_next):
	'''
	进入与退出处理,撤销挂单，确认正在进行中的订单
	'''
	log.info(u'trans进入安全检测机制...'.encode(code))
	demo_now.cancel()
	demo_next.cancel()
	log.info(u'trans撤单结束,开始确认机制...'.encode(code))
	tradeID = demo_now.get_succ_id_init(uid_next,uid_now)
	for i in tradeID:
		demo_next.pay(i)
		demo_now.confirm(i)
	log.info(u'trans安全机制执行完毕...'.encode(code))
	return True

def transfer_one(demo_now, uid_now, demo_next, uid_next):
	# 初始化状态
	trans_check_security(demo_now, uid_now, demo_next, uid_next)
	interval = float(demo_now.get_interval(c2c=False))
	if interval <= 0:
		log.error(u'请务必关注该信息，交易对{0}转移失败,卖出失败...'.format(demo_now.trade).encode(code))
		return False
	price = demo_now.get_price()
	if not demo_now.sell(interval, price):
		log.error(u"请务必关注该信息，交易对{0}转移失败,卖出失败...".format(demo_now.trade).encode(code))
		return False
	entrustId = demo_next.get_entrustId(uid_now)
	if not demo_next.buy(interval, price, entrustId):
		log.error(u"请务必关注该信息，交易对{0}转移失败,购买失败...".format(demo_now.trade).encode(code))
		return False
	tradeID = demo_next.get_succ_id(buyID=uid_next, sellID=uid_now)
	if not len(tradeID):
		log.error(u'交易对{0},此次交易被截胡，未完成转移,'.format(demo_now.trade).encode(code))
		return False
	for i in tradeID:
		if not demo_next.pay(i):
			log.error(u"请务必关注该信息，交易对{0}转移失败,付款失败...".format(demo_now.trade).encode(code))
			return False
		if not demo_now.confirm(i):
			log.error(u"请务必关注该信息，交易对{0}转移失败,确认付款失败...".format(demo_now.trade).encode(code))
			return False
	log.warn('*'*100)
	log.warn(u"请务必关注该信息，出现该信息表明该交易对转移完成...".encode(code))
	log.warn(u'交易对{0},成交价格为{1}CNY, 已完成交易量: {2}'.format(demo_now.trade,price,interval).encode(code))
	log.warn('*'*100)
	trans_check_security(demo_now, uid_now, demo_next, uid_next)
	return True

def c2c_rank_all(session, tra_pwd, uid, trades):
	global demos_now
	jobs = []
	timer = Timeout(60*120).start()#每个协程执行最多60分钟
	p = pool.Pool(10)
	for trade in trades:
		if int(trade['pass'])==1:
			log.info(u'{0}交易对设定为pass，跳过该交易对'.format(trade['trade']).encode(code))
			continue
		demo_now = C2C(session,tra_pwd,trade['trade'])
		demos_now.append(demo_now)
		jobs.append(p.spawn(c2c_rank_one,demo_now, trade['rank'], trade['yesterday'], uid))
	try:
		gevent.joinall(jobs,timeout=timer)#wait all jobs done
	except Timeout:
		log.error(u"可能由于网络延迟,刷单未完成...".encode(code))
	except Exception as e:
		log.error(e)
	finally:
		for demo_now in demos_now:
			c2c_check_security(demo_now, uid)
	log.warn(u'C2C一轮刷单完毕...'.encode(code))
	return True




def transfer_all(session_now, tra_pwd_now, uid_now, session_next, tra_pwd_next, uid_next, trades):
	global demos_now
	global demos_next
	jobs = []
	timer = Timeout(60*120).start()#每个协程执行最多30分钟
	p = pool.Pool(10)
	for trade in trades:
		if int(trade['pass'])==1:
			log.info(u'{0}交易对设定为pass，跳过该交易对'.format(trade['trade']).encode(code))
			continue
		demo_now = C2C(session_now,tra_pwd_now,trade['trade'])
		demo_next = C2C(session_next,tra_pwd_next,trade['trade'])
		demos_now.append(demo_now)
		demos_next.append(demo_next)
		jobs.append(p.spawn(transfer_one, demo_now, uid_now, demo_next, uid_next))
	try:
		gevent.joinall(jobs,timeout=timer)#wait all jobs done
	except Timeout:
		log.error(u"可能由于网络延迟,刷单未完成...".encode(code))
	except Exception as e:
		log.error(e)
	finally:
		for j in range(len(demos_now)):
			trans_check_security(demos_now[j], uid_now, demos_next[j], uid_next)
	return True


def c2c_exit(demo,uid):
	demo.cancel_all()
	tradeID = demo.get_succ_id_init(uid,uid,all_flag=True)
	for i in tradeID:
		demo.pay(i)
		demo.confirm(i)

def trans_exit(demo_now, uid_now, demo_next, uid_next):
	demo_now.cancel_all()
	demo_next.cancel_all()
	tradeID = demo_now.get_succ_id_init(uid_next,uid_now,all_flag=True)
	for i in tradeID:
		demo_next.pay(i)
		demo_now.confirm(i)



def exit():
	global demos_now
	global demos_next
	global uid_now
	global uid_next
	global c2c
	log.warn("You pressed Ctrl+C!")
	log.warn(u"进入安全退出机制,请等待几秒...".encode(code))
	write_conf(uid_now,filename = 'conf/now.json')
	jobs = []
	for i in range(len(demos_now)):
		if c2c:
			jobs.append(gevent.spawn(c2c_exit,demos_now[i],uid_now))
		else:
			jobs.append(gevent.spawn(trans_exit,demos_now[i],uid_now,demos_next[i],uid_next))
		break
	gevent.joinall(jobs)
	log.warn(u"安全退出结束...".encode(code))
	os._exit(1)



if __name__=='__main__':
	# 初始化读取配置工作
	base = read_conf('conf/base.json')
	config = read_conf('conf/c2c_all.json')
	now  = read_conf('conf/now.json')
	
	accounts = base['accounts']
	uids = config['UIDS']
	uid_now = now['now']
	index = uids.index(uid_now)
	uid_next = uids[index+1]
	trades = config['Trades']
	
	# log初始化
	filename = 'data/'+uid_now+'_c2c_all.log'
	log = init_log(filename)

	gevent.signal(signal.SIGINT, exit)
	demos_now = []
	demos_next = []
	log.warn(u"账户:{0},UID:{1}开始刷C2C交易对".format(accounts[uid_now]['mobile'],uid_now).encode(code))
	session_now = login(accounts[uid_now]['mobile'], accounts[uid_now]['password'])
	c2c = True
	while True:
		c2c = True
		log.warn(u"账户:{0},UID:{1}开始刷C2C交易对".format(accounts[uid_now]['mobile'],uid_now).encode(code))
		c2c_rank_all(session_now, accounts[uid_now]['tra_pwd'], uid_now, trades)
		demos_now = []
		c2c = False
		log.warn(u"转币操作:  账户:{0},UID:{1}->账户:{2},UID:{3}".format(accounts[uid_now]['mobile'],uid_now,accounts[uid_next]['mobile'],uid_next).encode(code))
		session_next = login(accounts[uid_next]['mobile'], accounts[uid_next]['password'])
		transfer_all(session_now, accounts[uid_now]['tra_pwd'], uid_now, session_next, accounts[uid_next]['tra_pwd'], uid_next, trades)
		log.warn(u'交易对转移完毕...'.encode(code))
		try:
			uid_now = uid_next
			index = uids.index(uid_now)
			write_conf(uid_now,filename = 'conf/now.json')
			uid_next = uids[index+1]
			session_now = session_next
		except Exception as e:
			log.warn(e)
			log.warn(u'所有配置的交易对已刷完,请检查...'.encode(code))
			break

















