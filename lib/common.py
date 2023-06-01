#coding:utf-8
import requests
import json
import urllib2
import sys
import datetime
import logging

code = 'utf-8'
if "win" in sys.platform and "darwin" not in sys.platform:
    code = 'gb2312'
markets = {}
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
    "MTL-CNY":"42",
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


def print_r(data):
	print(data.encode(code))


def init_log(filename):
    formattler = '%(asctime)s %(levelname)s : %(message)s'
    fmt = logging.Formatter(formattler)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(fmt)
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.WARN)
    file_handler.setFormatter(fmt)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


def login(account, password):
	import ysdm
	return ysdm.loginAndReturnSession(account,password)

	
def get_public_price(trade):
    data = trade.split('-')
    import price
    coinmarketcap = price.Coinmarketcap()
    if data[1]=='CNY':
        price = float(coinmarketcap.getSymbolPrice(data[0]))
        if price < 1.0:
            price = 1   
    else:
        price = float(coinmarketcap.getSymbolPrice(data[0]))/float(coinmarketcap.getSymbolPrice(data[1]))
    return price*1.08

def get_bbaex_price(trade): 
    session = requests.Session()
    headers = {"Accept":"*/*","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0","Referer":"https://www.bbaex.com/","Connection":"close","Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3","DNT":"1"}
    response = session.get("https://www.bbaex.com/coins", headers=headers)
    d = json.loads(response.content)
    tmp = trade.split('-')
    for data in d['data']['coins']:
        if data['coinEname']==tmp[0]:
            return data['coinEname']['price']
    index = int(trade_to_index[trade])
    return d['data']['coins'][index]['price']

def get_max_volume(trade,rank):
    rank = int(rank)
    # 下面两个价格应该调用函数获取
    bb_price = get_bbaex_price('BBB')
    coin_price = get_public_price(trade)
    if rank <=10:
        num = 60-rank*5
    else:
        num = 5
    if trade.split('-')[1]=='CNY':
        result = num*1.5*bb_price/(0.004*coin_price)
    else:
        result = num*1.5*bb_price/(0.001*coin_price)
    return result

    
def get_rank_information(trade, rank):
    '''
    获取第rank的交易量，并返回对应所需交易量。这里由于官方是ETH计量，我们是CXC计量。所以，需要转换一次。
    此外，若你要找第100名，而排行榜最多只有88名，则返回最后一个排名。
    trade = 'CXC-ETH' or 'CXC-CNY'
    rank = '50'
    得到eth交易量，为a1.此时，需要获取实时的eth/cxc，即实时cxc-eth价格，为a2，最后交易量为a1/a2
    '''
    global markets
    init_rank()
    coin_type = trade.split('-')[0]
    market_type = trade.split('-')[1]
    mt = 0
    if market_type == 'CNY':
        mt = 1
    ct = int(trade_to_index[coin_type])
    coin_rank = markets[mt]['coins'][ct]
    if coin_type != str(coin_rank['coinEname']):
        print_r(u"ERROR:币值索引计算错误！")
        exit(-1)
    rank_list = coin_rank['ranks']
    rank_num = len(rank_list)
    rank_index = rank-1
    if(rank_num < rank):
        print_r(u"WARNING:当前排行榜最高为{0}名！".format(rank_num))
        rank_index = rank_num-1
    trade_volume = rank_list[rank_index]['tradeVolume']
    return trade_volume


def caculate_best_price(best_buy_price, best_sell_price, coin_real_price, trade_min_accuracy):
	if coin_real_price > best_sell_price:
		best_price = best_sell_price - trade_min_accuracy
	elif coin_real_price < best_buy_price:
		best_price = best_buy_price + trade_min_accuracy
	else:
		best_price = coin_real_price
	return best_price

def read_conf(conf = 'conf.json'):
	with open(conf) as f:
		data = f.read()
	d = json.loads(data)
	return d

def write_conf(uid,filename = 'conf/now.json'):
    uid_now = {'now':uid}
    with open(filename,'w') as f:
        f.write(json.dumps(uid_now))
    return True
    
def get_yesterday(): 
    today=datetime.date.today() 
    oneday=datetime.timedelta(days=1) 
    yesterday=today-oneday  
    return yesterday

def get_yesterday_data():
    try:
        time_yesterday = get_yesterday()
        file = 'data/rank_{0}.json'.format(time_yesterday)
        with open(file,'r') as f:
            data = json.load(f)
    except Exception as e:
        print(e)
        print_r(u'json文件格式保存错误,读取失败...')
    return data

if __name__=='__main__':
	# get_rank_information('CXC-CNY',10)
    print get_max_volume('ETH-CNY')