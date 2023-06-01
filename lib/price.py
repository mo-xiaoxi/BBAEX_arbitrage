#-*-coding:utf-8-*-
import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2", "Accept": "*/*"}


#特别声明！！ KingN Coin (价值约150.21 CNY) 和 Kyber Network(价值约7.59 CNY CNY)都被简称为KNC，而bbaex里的KNC是指便宜的Kyber Network，所以这里别搞错了
#经过比对，bbaex api 上获取的价格有问题，是不准的；和火币及coinmarketcap上的有较大出入，而且网页上也是半天不更新，api和网页显示还不一样
#coinmarketcap 上的和火币上的貌似也有差别，不过差别不大
class Coinmarketcap():

    def __init__(self):
        pass
        # self.targetUrl = 'https://api.coinmarketcap.com/v1/ticker/?limit=0'
        # self.priceTable={}
        # self.priceETH=getETHPriceFromHuobi()
        # self.priceUSDT=getUSD2CNYExchange()
        # response = requests.get(self.targetUrl, headers=headers)
        # self.datas = json.loads(response.content)
        # theKyberNetworkPrice='ERROR'
        # #这里有个尴尬的问题，就是coinmarketcap这个api，它返回的单位只有USDT和BTC，而没有ETH；从而这里选择USDT价格来减少计算误差
        # for data in self.datas:
        #     if data['id']=='kyber-network':
        #         theKyberNetworkPrice =float(data['price_usd'].encode('utf-8'))*self.priceUSDT
        #     if data['price_usd']!=None:
        #         self.priceTable[data['symbol']]=float(data['price_usd'].encode('utf-8'))*self.priceUSDT
        # self.priceTable['KNC']=theKyberNetworkPrice
        #
        # #对于BBB和CXC，直接从bbaex尝试获取其价格，
        # self.targetUrl='https://www.bbaex.com/index'
        # response = requests.get(self.targetUrl, headers=headers)
        # datas2=json.loads(response.content)
        # #market:ETH，所以取第0维，第1维是btc区
        # information=datas2["data"]["markets"][0]
        # for coin in information[u"coins"]:
        #     if coin[u"coinEname"]==u"BBB":
        #         self.priceTable['BBB'] = float(coin[u"price"]) * self.priceETH
        #     if coin[u"coinEname"]==u"CXC":
        #         self.priceTable['CXC'] = float(coin[u"price"]) * self.priceETH
        # self.priceTable['CNY'] = 1.0

    #使用此函数来获取价格，单位是CNY
    def getSymbolPrice(self,symbol):
        WEBAPI_URL = 'http://120.78.184.89:18876/getCNYPrice/'
        targetUrl = WEBAPI_URL + symbol
        response = requests.get(targetUrl)
        return float(response.content)


def getETHPriceFromHuobi():
    '''
    :return:    float ethPrice
    '''
    targetUrl='https://api-otc.hb-otc.net/v1/otc/base/market/price'
    response = requests.get(targetUrl, headers=headers)
    data=json.loads(response.content)
    assert (data['data'][1]['coinName']=='ETH')
    ethPrice=data['data'][1]['price']
    return float(ethPrice)

def getUSD2CNYExchange():
    '''
    :return:    float usdtPrice
    '''
    paramsPost = {"from": "USD", "to": "CNY", "num": "1"}
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
               "Referer": "https://huilv.911cha.com/USDCNY.html", "Connection": "close",
               "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
               "Content-Type": "application/x-www-form-urlencoded"}
    cookies = {"Hm_lvt_65855f77bb6ee720c0a940b9cf8101a9": "1521036598",
               "Hm_lpvt_65855f77bb6ee720c0a940b9cf8101a9": "1521036644"}
    response = requests.post("https://huilv.911cha.com/", data=paramsPost, headers=headers, cookies=cookies)

    reg=r'今日最新价：([0-9\.]*)'
    usd2cnyExchange=re.findall(reg,response.content)[0]
    return float(usd2cnyExchange)

def getPriceFromHuobi(symbol='ethusdt'):

    targetAddress = 'https://api.huobi.pro'
    targetPath = '/market/detail/merged'
    params = {'symbol': symbol}

    url = targetAddress + targetPath
    response = requests.get(url, headers=headers, params=params)

    data = json.loads(response.content)
    if data["status"] == "ok":
        return data["tick"]["close"]
    else:
        return 'ERROR'

def checker():
    trade_pairs = [
        "BBB-ETH",
        "CXC-ETH",
        "POE-ETH",
        "ICX-ETH",
        "LRC-ETH",
        "SNT-ETH",
        "TRX-ETH",
        "BTM-ETH",
        "BAT-ETH",
        "OMG-ETH",
        "AION-ETH",
        "DNT-ETH",
        "KNC-ETH",
        "CREDO-ETH",
        "FUEL-ETH",
        "VEN-ETH",
        "MANA-ETH",
        "CDT-ETH",
        "EOS-ETH",
        "AST-ETH",
        "EVX-ETH",
        "AE-ETH",
        "ZRX-ETH",
        "GNT-ETH",
        "ZIL-ETH",
        "ELF-ETH",
        "FUN-ETH",
        "NAS-ETH",
        "SALT-ETH",
        "POWR-ETH",
        "LINK-ETH",
        "BNT-ETH",
        "ENG-ETH",
        "REQ-ETH",
        "PAY-ETH",
        "RDN-ETH",
        "STORJ-ETH",
        "MTL-ETH",
        "DDN-ETH"
    ]
    #38
    print("trade_pairs in bbaex:"+str(len(trade_pairs)))
    coinmarketcap= Coinmarketcap()
    #print("coinmarketcap.getPriceTableLength():"+str(coinmarketcap.getPriceTableLength()))
    i=0
    for trade_pair in trade_pairs:
        processedSymbol=trade_pair.replace('-ETH','')
        price=coinmarketcap.getSymbolPrice(processedSymbol)
        if price!='ERROR':
            #print(trade_pair+":"+str(float(price)*getUSDTPriceFromHuobi()))
            print(trade_pair.replace('-ETH','') + ":" + str(float(price))+"CNY")
        i+=1
    #38
    print("we searched for {times} times.".format(times=i))






if __name__ == '__main__':
    getSymbolPrice('ETH')





