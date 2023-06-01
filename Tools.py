# coding:utf-8
import lib.coinInfo as coinInfo
import argparse
import sys

uuids = ["6449","7895", "7896", "7898", "6453","6506"]

trade_list = [
    'BBB-CNY',
    'DDN-CNY',
    'ICX-CNY',
    'LRC-CNY',
    'SNT-CNY',
    'TRX-CNY',
    'BTM-CNY', 
    'BAT-CNY',
    'OMG-CNY',
    'AION-CNY',
    'DNT-CNY',
    'KNC-CNY',
    'POE-CNY',
    'VEN-CNY',
    'MANA-CNY',
    'EOS-CNY',
    'AST-CNY',
    'EVX-CNY',
    'AE-CNY',
    'ZRX-CNY',
    'GNT-CNY',
    'ZIL-CNY',
    'ELF-CNY',
    'NAS-CNY',
    'SALT-CNY'
    'POWR-CNY',
    'LINK-CNY',
    'ENG-CNY',
    'REQ-CNY',
    'PAY-CNY',
    'RDN-CNY',
    'STORJ-CNY',
    'MTL-CNY',
    'BBB-ETH',
    'DDN-ETH',
    'ICX-ETH',
    'LRC-ETH',
    'SNT-ETH',
    'TRX-ETH',
    'BTM-ETH', 
    'BAT-ETH',
    'OMG-ETH',
    'AION-ETH',
    'DNT-ETH',
    'KNC-ETH',
    'POE-ETH',
    'VEN-ETH',
    'MANA-ETH',
    'EOS-ETH',
    'AST-ETH',
    'EVX-ETH',
    'AE-ETH',
    'ZRX-ETH',
    'GNT-ETH',
    'ZIL-ETH',
    'ELF-ETH',
    'NAS-ETH',
    'SALT-ETH'
    'POWR-ETH',
    'LINK-ETH',
    'ENG-ETH',
    'REQ-ETH',
    'PAY-ETH',
    'RDN-ETH',
    'STORJ-ETH',
    'MTL-ETH'
]

rank = 50

is_yestoday = False


def main():
    global uuids, trade_list, rank, is_yestoday
    parser = argparse.ArgumentParser(prog='python ./Tools.py',formatter_class=argparse.RawTextHelpFormatter)

    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--trade_count', action='store_true',
                   help='获取某个交易对指定排名的交易量；需要设置trade_list和rank两个变量')

    g.add_argument('--monitor', action='store_true',
                   help='获取账号列表中所有账号的排名以及总收益;需要设置uuids变量')

    g.add_argument('--out_rank', action='store_true',
                   help='获取账号列表中所有账号在指定交易对上的落榜数据;需要设置uuids和trade_list两个变量')

    g.add_argument('--profit_rank', action='store_true',
                   help='计算排行榜中收益前十的名次')

    g.add_argument('--save_json', action='store_true',
                   help='保存今日的排行榜信息;注意该选项下-y参数无效')

    parser.add_argument('-y', action='store_true',
                        help='添加该选项后，数据源切换为昨天的数据，该参数全局可用')

    args = parser.parse_args(sys.argv[1:])

    if args.y:
        is_yestoday = True

    if args.trade_count:
        for trade in trade_list:
            coinInfo.get_trade_count(trade, rank, is_yestoday)
    elif args.monitor:
        coinInfo.monitor(uuids, is_yestoday)
    elif args.out_rank:
        coinInfo.out_of_rank(uuids, trade_list, is_yestoday)
    elif args.profit_rank:
        for trade in trade_list:
            coinInfo.caculate_bitfit(trade, is_yestoday)
    elif args.save_json:
        coinInfo.save_rank_json()
    else:
        parser.print_usage


if __name__ == '__main__':
    main()
    
