# -*- coding: utf-8 -*-
# @Time    : 2017/8/2 22:02
# @Author  : 橄榄树

import time

import fundutil as util
from trade.strategytemplate import Strategytemplate


class FundTopic(Strategytemplate):
    def __init__(self):
        self.url = "http://fund.eastmoney.com/api/FundTopicInterface.ashx?callbackname=topicFundData&sort=SYL_1N&" \
                   "sorttype=DESC&ft=&pageindex=1&pagesize=10&dt=10&tp=414fefb3c7da352e&isbuy=1"
    """
    基金行情top10
    """
    def get_funddata(self):
        content = util.get_funddata(self.url)
        if content is not None:
            util.fund_topic_to_frame(content)

    def execute(self):
        self.get_funddata()


class FundPrice(Strategytemplate):
    """
    累计收益率
    """
    @staticmethod
    def get_fund_price():
        fundcodes = util.get_fund_code()
        nowtime = repr(time.time())
        for index in fundcodes:
            fund_price_url = "http://fund.eastmoney.com/api/PingZhongApi.ashx?m=0&fundcode="+index[0]+"&indexcode=000300&type=y&_="+nowtime[:nowtime.find('.')]
            fund_data = util.get_funddata(fund_price_url)
            util.fund_price_to_frame(fund_data, index[1], index[0])
        # 获取指数数据
        for code in ['000300', '000001', '399001']:
            fund_price = "http://fund.eastmoney.com/api/PingZhongApi.ashx?m=0&" \
                         "fundcode=" + fundcodes[0][0] + "&indexcode="+code+"&type=y&_=" + nowtime[:nowtime.find('.')]
            fund_data = util.get_funddata(fund_price)
            util.fund_price_to_frame(fund_data, fundcodes[-1][1], fundcodes[0][0], index_code=code)

    def execute(self):
        self.get_fund_price()


class FundUnitPrice(Strategytemplate):

    @staticmethod
    def get_fund_unitprice():
        """
        基金单位净值
        """
        fundcodes = util.get_fund_code()
        nowtime = repr(time.time())
        for code in fundcodes:
            unit_price_url = "http://fund.eastmoney.com/pingzhongdata/"+str(code[0].encode('utf-8'))+".js?v="\
                             + nowtime[:nowtime.find('.')]

            content = util.get_funddata(unit_price_url)
            util.get_fund_unitprice(code, content)

    def execute(self):
        self.get_fund_unitprice()


if __name__ == "__main__":
    topic = FundTopic()
    topic.execute()

    topic = FundPrice()
    topic.execute()

    topic = FundUnitPrice()
    topic.execute()



