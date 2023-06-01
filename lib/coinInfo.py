# -*- coding: UTF-8 -*-
import urllib2
import json
import time
import common
import operator
import datetime
from common import print_r

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


def init_rank():
    '''
    初始化实时排名数据
    '''
    global markets
    headers = {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0",
               "Referer": "https://www.bbaex.com/", "Connection": "close", "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3", "DNT": "1"}
    rank_url = "https://www.bbaex.com/tradeRank"
    request = urllib2.Request(rank_url, headers=headers)
    response = urllib2.urlopen(request)
    markets = json.loads(response.read())
    markets = markets['data']['markets']


def init_rank_from_json(file_name=None):
    '''
    从json文件中初始化排名数据；不指定文件名时，默认从前一天的json文件中读取
    '''
    global markets
    if not file_name:
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today-oneday
        file_name = "data/rank_"+str(yesterday)+".json"
    log = open(file_name, 'r')
    markets = json.loads(log.read())


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
    ct = int(trade_to_index[trade])
    coin_rank = markets[mt]['coins'][ct]
    if coin_type != str(coin_rank['coinEname']):
        print_r("ERROR:币值索引计算错误！")
        exit(-1)
    rank_list = coin_rank['ranks']
    rank_num = len(rank_list)
    rank_index = rank-1
    if(rank_num < rank):
        print_r("WARNING:当前排行榜最高为{0}名！".format(rank_num))
        rank_index = rank_num-1
    trade_volume = rank_list[rank_index]['tradeVolume']
    return trade_volume


def monitor(uuids, get_yestoday=False):
    '''
    uuids = ['6449','2333'] #为我们使用的userID
    打印出来吧
    UUID CXC-ETH BBB-ETH.... CXC-CNY BBB-CNY
    6449 12		19			99		100
    '''
    global markets
    if not get_yestoday:
        init_rank()
    else:
        init_rank_from_json()
    count_info = {}
    totalBB = 0
    for id in uuids:
        count_info[id] = {}
        for i in range(0, 2):
            if i == 0:
                market_type = 'ETH'
            else:
                market_type = 'CNY'
            for coin in markets[i]['coins']:
                coin_type = coin['coinEname']
                trade_name = coin_type+'-'+market_type
                for line in coin['ranks']:
                    if line['uid'] == int(id):
                        count_info[id][trade_name] = {
                            'rank': line['rank'], 'reward': line['reward']}
                        tmp_reward = line['reward']
                        if id != '6449':
                            tmp_reward=tmp_reward*1.5
                        totalBB += tmp_reward
                        continue
    #print count_info
    # out put result
    print_r(u"uid     交易对     排名     奖励(BB)\n")
    for id in uuids:
        if count_info[id]:
            for trade in count_info[id]:
                print_r(str(id)+'     '+trade+'     '+str(count_info[id][trade]['rank']).strip()+'     '+str(
                    count_info[id][trade]['reward']))
    print_r(u"今日总奖励BB个数(包含二级邀请奖励)："+str(totalBB))


def out_of_rank(uuids, trade_list, get_yestoday=False):
    '''
    监控排行榜，给出不在排行榜中的uuid和对应的交易对信息(只监控给定交易对的信息)
    '''
    global markets
    if not get_yestoday:
        init_rank()
    else:
        init_rank_from_json()
    out_info = {}
    for id in uuids:
        out_list = []
        for i in range(0, 2):
            if i == 0:
                market_type = 'ETH'
            else:
                market_type = 'CNY'
            for coin in markets[i]['coins']:
                coin_type = coin['coinEname']
                trade_name = coin_type+'-'+market_type
                if trade_name in trade_list:
                    is_found = False
                    for line in coin['ranks']:
                        if line['uid'] == int(id):
                            is_found = True
                            break
                    if not is_found:
                        out_list.append(trade_name)
                else:
                    continue
        out_info[id] = out_list
    print_r(u"落榜信息如下：\n")
    print_r(u"uid    交易对")
    for id in out_info.iterkeys():
        out_list = out_info[id]
        #print len(out_list)
        for trade in out_list:
            print_r("{0}  {1}".format(id, trade))


def caculate_bitfit(trade, get_yestoday=False):
    '''
    实时依据排行榜信息，计算前1-100名对应交易对的收益。
    收益计算价格为 收益的BBB*BBB实时价格-刷到对应交易量的手续费
    包括币币市场和C2C市场
    trade = 'CXC-ETH' or 'CXC-CNY'
    get_yestody参数为true时，获取的是昨日收盘数据
    '''
    global markets
    if not get_yestoday:
        init_rank()
    else:
        init_rank_from_json()

    print_r("========="+trade+"=========")

    coin_type = trade.split('-')[0]
    market_type = trade.split('-')[1]

    # 下面两个价格应该调用函数获取
    bb_price = common.get_bbaex_price('BBB')
    coin_price = common.get_public_price(coin_type+'-CNY')

    mt = 0
    if market_type == 'CNY':
        mt = 1
    ct = int(trade_to_index[trade])
    coin_rank = markets[mt]['coins'][ct]
    if coin_type != str(coin_rank['coinEname']):
        print_r(u"ERROR:币值索引计算错误！")
        exit(-1)
    rank_list = coin_rank['ranks']
    rank_num = len(rank_list)
    profit_dict = {}
    for i in range(0, rank_num):
        income = rank_list[i]['reward']*bb_price
        outcome = rank_list[i]['tradeVolume']*coin_price*0.001
        profit = income - outcome
        profit_dict[str(i+1)] = profit

    sorted_profit = sorted(profit_dict.iteritems(),
                           key=operator.itemgetter(1), reverse=True)
    disp_num = 10
    if rank_num < 10:
        disp_num = rank_num
    for i in range(0, disp_num):
        print_r(u"TOP {0}:刷到第{1}名，收益为{2} CNY\n".format(
            i+1, sorted_profit[i][0], sorted_profit[i][1]))

    # 返回收益最高的刷单排名
    return sorted_profit[0][0]


def get_best_rank(trade, get_yestoday=False):
    '''
    实时依据排行榜信息，计算前1-100名对应交易对的收益。
    收益计算价格为 收益的BBB*BBB实时价格-刷到对应交易量的手续费
    包括币币市场和C2C市场
    trade = 'CXC-ETH' or 'CXC-CNY'
    get_yestody参数为true时，获取的是昨日收盘数据
    '''
    global markets
    if not get_yestoday:
        init_rank()
    else:
        init_rank_from_json()

    print_r("========="+trade+"=========")

    coin_type = trade.split('-')[0]
    market_type = trade.split('-')[1]

    # 下面两个价格应该调用函数获取
    bb_price = common.get_bbaex_price('BBB')
    coin_price = common.get_public_price(coin_type+'-CNY')

    mt = 0
    if market_type == 'CNY':
        mt = 1
    ct = int(trade_to_index[trade])
    coin_rank = markets[mt]['coins'][ct]
    if coin_type != str(coin_rank['coinEname']):
        print_r(u"ERROR:币值索引计算错误！")
        exit(-1)
    rank_list = coin_rank['ranks']
    rank_num = len(rank_list)
    profit_dict = {}
    for i in range(0, rank_num):
        income = rank_list[i]['reward']*bb_price*1.5
        if mt:
            outcome = rank_list[i]['tradeVolume']*coin_price*0.004
        else:
            outcome = rank_list[i]['tradeVolume']*coin_price*0.001
        profit = income - outcome
        profit_dict[str(i+1)] = profit

    sorted_profit = sorted(profit_dict.iteritems(),
                           key=operator.itemgetter(1), reverse=True)
    disp_num = 10
    if rank_num < 10:
        disp_num = rank_num
    results = []
    for i in range(0, disp_num):
        print_r(u"TOP {0}:刷到第{1}名，收益为{2} CNY\n".format(
            i+1, sorted_profit[i][0], sorted_profit[i][1]))
        tmp = (trade,sorted_profit[i][0],sorted_profit[i][1])
        results.append(tmp)
    # 返回收益最高的刷单排名
    return results



def get_trade_count(trade, rank, get_yestoday=False):
    '''
    传入交易对和排名，获取该交易对在该排名的交易量。默认获取实时数据；get_yestody参数为true时，获取的是昨日收盘数据
    '''
    global markets
    if not get_yestoday:
        init_rank()
    else:
        init_rank_from_json()

    print_r("========="+trade+"=========")

    coin_type = trade.split('-')[0]
    market_type = trade.split('-')[1]

    mt = 0
    if market_type == 'CNY':
        mt = 1
    ct = int(trade_to_index[trade])
    coin_rank = markets[mt]['coins'][ct]
    if coin_type != str(coin_rank['coinEname']):
        print_r(u"ERROR:币值索引计算错误！")
        exit(-1)
    rank_list = coin_rank['ranks']
    rank_num = len(rank_list)

    if rank_num == 0:
        print_r(u"ERROR:当前交易对没有交易信息")
        exit(-1)

    # 如果要求的排名大于了当前的总排名数量，则输出最后一名的交易数量
    if rank_num < rank:
        rank = rank_num

    tradeVolume = rank_list[rank-1]['tradeVolume']
    print_r(u"交易对："+trade+"    "+u"排名："+str(rank)+"    "+u"交易量："+str(tradeVolume))
    return tradeVolume


def save_rank_data(rank):
    '''
    获取所有币币和C2C的rank位排名。一般在晚上11点，进行数据备份时使用
    然后，将信息写成文件。用于第二天设定刷量交易额.交易额转换为实时币种，而非ETH
    格式如下
    'CXC-ETH':'22222',
    'BBB-ETH':'22222',
    'CXC-CNY':'2222',...
    '''
    global markets
    init_rank()
    time_now = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
    log = open("rank_"+str(rank)+"_"+time_now+".log", 'a')
    for i in range(0, 2):
        if i == 0:
            market_type = 'ETH'
        else:
            market_type = 'CNY'
        for coin in markets[i]['coins']:
            coin_type = coin['coinEname']
            trade_name = coin_type+'-'+market_type
            if rank > len(coin['ranks']):
                log.write(trade_name+":None\n")
            else:
                log.write(trade_name+":" +
                          str(coin['ranks'][rank-1]['tradeVolume'])+'\n')


def save_rank_json():
    '''
    将当前的排行榜保存为json文件，该函数用于每晚0点前保存当日交易数据用于次日计算
    '''
    global markets
    init_rank()
    time_now = time.strftime("%Y-%m-%d", time.localtime())
    log = open("data/rank_"+time_now+".json", 'w')
    log.write(json.dumps(markets))





if __name__ == '__main__':
    pass