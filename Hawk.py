# coding:utf-8
import time
import threading
import os
import signal
from lib.common import *


trade_to_ID = {
    "CXC-ETH": "18",
    "BBB-ETH": "38",
    "ICX-ETH": "21",
    "LRC-ETH": "22",
    "SNT-ETH": "20",
    "TRX-ETH": "19",
    "BTM-ETH": "23",
    "BAT-ETH": "3",
    "OMG-ETH": "24",
    "AION-ETH": "35",
    "DNT-ETH": "25",
    "KNC-ETH": "26",
    "CREDO-ETH": "27",
    "FUEL-ETH": "28",
    "POE-ETH": "29",
    "VEN-ETH": "36",
    "CND-ETH": "30",
    "MANA-ETH": "32",
    "CDT-ETH": "31",
    "EOS-ETH": "39",
    "AST-ETH": "40",
    "EVX-ETH": "41",
    "AE-ETH": "42",
    "ZRX-ETH": "43",
    "GNT-ETH": "44",
    "ZIL-ETH": "45",
    "ELF-ETH": "46",
    "FUN-ETH": "47",
    "NAS-ETH": "48",
    "SALT-ETH": "49",
    "POWR-ETH": "50",
    "LINK-ETH": "51",
    "BNT-ETH": "52",
    "ENG-ETH": "53",
    "REQ-ETH": "54",
    "PAY-ETH": "55",
    "RDN-ETH": "56",
    "STORJ-ETH": "57",
    "MTL-ETH": "58",
    "DDN-ETH": "59"
}

# 设置截胡区间与真实价格的差异度
HAWK_RATE = 0.05


class Hawk():

    def __init__(self, session, tra_pwd, trade):
        '''
        初始化函数
        '''
        self.s = session
        self.tra_pwd = tra_pwd
        self.trade = trade

        # 当前市场上买卖一的价格和数量
        self.buy_price = None
        self.buy_count = None
        self.sell_price = None
        self.sell_count = None

        # 当前的真实价格和交易区间
        self.real_price = None
        self.hawk_down_price = None
        self.hawk_up_price = None

        self.MarketCoinId = trade_to_ID[trade]

        # 当前账户中的币种数量和eth数量
        self.coin_count = None
        self.eth_count = None

        # 未成交订单的数量
        self.recount = 0

        # 异常信号
        self.error_signal = False
        self.event = threading.Event()

    def set_bbaex_price(self):
        '''
        设置bbaex市场上当前的买卖价格
        '''
        paramsGet = {"top": "1"}
        headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0",
                   "Referer": "https://www.bbaex.com/", "Connection": "close", "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3", "DNT": "1"}
        response = self.s.get("https://www.bbaex.com/markets/" +
                              self.MarketCoinId, params=paramsGet, headers=headers)
        top = json.loads(response.content)
        try:
            self.sell_price = float(top['data']['sells'][0]['price'])
            self.sell_count = top['data']['sells'][0]['count']
        except Exception as e:
            print('no self.sell_price...')
            self.sell_price = None
            self.sell_count = None

        try:
            self.buy_price = float(top['data']['buys'][0]['price'])
            self.buy_count = top['data']['buys'][0]['count']
        except Exception as e:
            print('no self.buy_price....')
            self.buy_price = None
            self.buy_count = None

        if self.buy_price and self.sell_price:
            print_r(u"bbaex交易价格获取成功!当前买一价:{:.8F} eth,买一数量:{:.2F}  ;   卖一价:{:.8F} eth,卖一数量:{:.2F}".format(
                self.buy_price, self.buy_count, self.sell_price, self.sell_count))
            return True
        else:
            print_r(u"价格获取失败!")
            return False

    def set_hawk_price(self):
        '''
        获取当前交易对的场外价格
        '''
        try:
            coin_price = get_public_price(self.trade)
            eth_price = get_public_price('ETH-CNY')

            self.real_price = coin_price
            self.hawk_down_price = self.real_price*(1-HAWK_RATE)
            self.hawk_up_price = self.real_price*(1+HAWK_RATE)

            #print("coin_price(ETH):{:.8F}".format(self.real_price))
            #print "eth_price(CNY):"+str(eth_price)
            print_r(u"该交易对的场外价格为:{:.8F} eth".format(self.real_price))
            print_r(u"当前设置的买入价格:{:.8F};当前设置的卖出价格{:.8F}.".format(
                self.hawk_down_price, self.hawk_up_price))

            return True
        except:
            print_r(u"场外价格获取失败!")
            return False

    def get_own_coin(self):
        '''
        获取当前账户的coin余额和eth余额
        '''
        headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0",
                   "Referer": "https://www.bbaex.com/", "Connection": "close", "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3", "DNT": "1"}
        response = self.s.post(
            "https://www.bbaex.com/users/center", headers=headers)
        data = json.loads(response.content)
        coins = data['data']['coins']
        coinName = self.trade.split('-')[0]
        for coin in coins:
            if coin['coinName'] == coinName:
                self.coin_count = coin['count']
            elif coin['coinName'] == 'ETH':
                self.eth_count = coin['count']

        if self.coin_count and self.eth_count:
            print_r(u"币种余额和eth余额获取成功!账户内"+coinName+u"数量:{:.8F}个,eth数量:{:.8F}个".format(
                self.coin_count, self.eth_count))
            return True
        else:
            print_r(u"币种余额获取失败!")
            return False

    def buy(self, price, count):
        '''
        下买单
        '''
        paramsPost = {"count": count, "tradePwd": self.tra_pwd,
                      "marketCoinId": self.MarketCoinId, "price": price}
        headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0", "Referer": "https://www.bbaex.com/",
                   "Connection": "close", "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3", "DNT": "1", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        response = self.s.post(
            "https://www.bbaex.com/markets/buys", data=paramsPost, headers=headers)
        if response.status_code == 200:
            print("buy Order send succ!")
            print_r(response.content)
            return True
        else:
            print(response.status_code)
            print_r(response.content)
            return False

    def sell(self, price, count):
        '''
        下卖单
        '''
        paramsPost = {"count": count, "tradePwd": self.tra_pwd,
                      "marketCoinId": self.MarketCoinId, "price": price}
        headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0", "Referer": "https://www.bbaex.com/",
                   "Connection": "close", "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3", "DNT": "1", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        response = self.s.post(
            "https://www.bbaex.com/markets/sells", data=paramsPost, headers=headers)
        if response.status_code == 200:
            print("sell succ!")
            print_r(response.content)
            return True
        else:
            print(response.status_code)
            print_r(response.content)
            return False

    def cancel(self, trade_id):
        '''
        撤销指定的买卖单
        '''
        paramsPost = {"id": trade_id}
        headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0", "Referer": "https://www.bbaex.com/",
                   "Connection": "close", "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3", "DNT": "1", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        response = self.s.post(
            "https://www.bbaex.com/marketEntrusts/cancel", data=paramsPost, headers=headers)
        if response.status_code == 200:
            print("Cancel Order send succ!")
        else:
            print(response.status_code)

    def check_state(self):
        '''
        检测是否有未成交的订单,有的话则撤销
        '''
        paramsGet = {"top": "1"}
        headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0",
                   "Referer": "https://www.bbaex.com/", "Connection": "close", "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3", "DNT": "1"}
        response = self.s.get("https://www.bbaex.com/markets/" +
                              self.MarketCoinId, params=paramsGet, headers=headers)
        top = json.loads(response.content)
        mys = top['data']['mys']
        if len(mys) > 0:
            print_r(u"最近的交易仍未成交，请等待...")
            self.recount += 1
            if self.recount > 1:
                print_r(u"1s仍未成交，撤销所有买卖单")
                for my in mys:
                    trade_id = my['id']
                    self.cancel(trade_id)
            time.sleep(1)
            return self.check_state()
        self.recount = 0
        print_r(u'订单检测成功...')
        return True

    def cancel_all(self):
        '''
        检测挂单，撤销所有
        '''
        paramsGet = {"top": "10"}
        headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0",
                   "Referer": "https://www.bbaex.com/", "Connection": "close", "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3", "DNT": "1"}
        response = self.s.get("https://www.bbaex.com/markets/" +
                              self.MarketCoinId, params=paramsGet, headers=headers)
        top = json.loads(response.content)
        try:
            mys = top['data']['mys']
            for my in mys:
                trade_id = my['id']
                self.cancel(trade_id)
        except Exception as e:
            print(e)
        print('Cancel All Order send succ!')

    def check_tradeable(self, trade_type="buy"):
        '''
        检测账户中的资产总额是否小于了某个阈值,即设置亏损线
        '''
        if trade_type == "buy":
            pass

    def loop_run_hawk(self):
        '''
        循环检测当前的买一卖一价格,并进行交易
        '''
        while not self.error_signal:
            if self.set_bbaex_price():
                print('\033[1;31m')
                # 如果当前的卖一价格小于截胡下区间价格,则下买单买入
                if self.sell_price <= self.hawk_down_price:
                    trade_count = self.sell_count

                    # 检测最大可买数量
                    self.get_own_coin()
                    # 考虑交易的手续费
                    buyable_count = self.eth_count / (self.sell_price*1.001)
                    print_r(u"最大可买入数量:{:.8F}".format(buyable_count))
                    if trade_count > buyable_count:
                        trade_count = buyable_count

                    if trade_count >= 0.01:
                        # 下买单
                        self.buy(self.sell_price, trade_count)
                        print_r(u"下单类型：买单 ； 下单价格：{:.8F} ； 下单数量{:.8F}".format(self.sell_price,trade_count))
                        # 如果没有成交成功,或者没有成交完,则撤销订单(只针对当前的币种)
                        self.check_state()
                    else:
                        print_r(u"买入失败:交易余额不足!")

                # 如果当前的买一价格大于截胡上区间价格,则下卖单卖出
                if self.buy_price >= self.hawk_up_price:
                    trade_count = self.buy_count

                    # 检测最大可卖数量
                    self.get_own_coin()
                    # 考虑交易的手续费
                    #sellable_count = self.coin_count*(1-0.001)
                    sellable_count = self.coin_count
                    print_r(u"最大可卖出数量:{:8F}".format(sellable_count))
                    if trade_count > sellable_count:
                        trade_count = sellable_count

                    if trade_count >= 0.01:
                        # 下卖单
                        self.sell(self.buy_price, trade_count)
                        print_r(u"下单类型：卖单 ； 下单价格：{:.8F} ； 下单数量{:.8F}".format(self.buy_price,trade_count))
                        # 如果没有成交成功,或者没有成交完,则撤销订单(只针对当前的币种)
                        self.check_state()
                    else:
                        print_r(u"卖出失败:交易余额不足!")

                if self.event.is_set():
                    self.cancel_all()
                    os._exit(-1)

                #time.sleep(2)
                print('\033[0m')

            # 获取价格失败
            else:
                continue

    def loop_set_price_interval(self):
        '''
        循环设置截胡的价格区间
        '''
        while not self.error_signal:
            self.set_hawk_price()
            # self.check_is_alive()
            time.sleep(60)

    def exit_trade(self):
        '''
        退出程序
        '''
        self.cancel_all()

    def check_is_alive(self):
        '''
        测试一下当前的线程是否还存活
        '''
        f=open("signal.txt",'a')
        f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        f.write("\n")
        f.close()

    def handler(self,signal_num, frame):
        print("\nYou Pressed Ctrl-C.")
        try:
            self.error_signal=True
            self.exit_trade()
        except Exception as e:
            print(e)
            pass
        os._exit(signal_num)

    def hack(self):
        '''
        开始程序的主逻辑
        '''
        try:
            signal.signal(signal.SIGINT, self.handler)
            signal.signal(signal.SIGTERM, self.handler)
            t1 = threading.Thread(target=self.loop_set_price_interval)
            t2 = threading.Thread(target=self.loop_run_hawk)
            t1.setDaemon(True)
            t2.setDaemon(True)
            t1.start()
            t2.start()
            #t1.join()
            #t2.join()

            # 使用下面的方法代替join以让主线程捕捉signal
            while True:
                if t1.isAlive or t2.is_alive:
                    continue
                else:
                    break
                time.sleep(10)
            print_r("this is in hawk")
        except Exception,e:
            print e



if __name__ == '__main__':
    config = read_conf('conf/hawk.json')
    # signal.signal(signal.SIGINT, handler)
    # print config
    print_r(u"账户:{0}".format(config['account']['mobile']))
    session = login(config['account']['mobile'], config['account']['password'])

    for trade in config['Trades']:
        print('*'*50)
        if int(trade['pass']) == 1:
            print_r(u'{0}交易对设定为pass，跳过该交易对'.format(trade['trade']))
            continue
        print_r(u'当前截胡交易对{0}'.format(trade['trade']))
        demo = Hawk(session, config['account']['tra_pwd'], trade['trade'])
        demo.hack()
        print_r("this is out hawk")
    print(u'程序执行完毕，进入退出机制'.encode(code))
    exit(-1)
