# -*- coding: utf-8 -*-
# @Time    : 2017/8/2 22:02
# @Author  : 橄榄树


import tushare as ts
from trade.strategytemplate import Strategytemplate
import trade.tushare.stockutil as sutil


class Stock(Strategytemplate):
    """
    基础数据下载，行业地域分类以及成分股
    """
    @staticmethod
    def get_stock_basics():
        """
        指数以及名称
        :return:
        """
        data = ts.get_stock_basics()
        if len(data) > 0:
            sutil.insert_stock_basics_db(data)

    @staticmethod
    def get_stock_index():
        """
        行业地域分类
        :return:
        """
        data = ts.get_index()
        if len(data) > 0:
            sutil.insert_stock_index_db(data)

    @staticmethod
    def get_sz50s():
        """
        上证50成分股
        :return:
        """
        data = ts.get_sz50s()
        if len(data) > 0:
            sutil.insert_stock_element_db('50', data)

    @staticmethod
    def get_hs300s():
        data = ts.get_hs300s()
        if len(data) > 0:
            sutil.insert_stock_element_db('300', data)

    def execute(self):
        self.get_stock_basics()
        self.get_stock_index()
        self.get_sz50s()
        self.get_hs300s()


if __name__ == "__main__":
    stock = Stock()
    stock.execute()




