# -*- coding: utf-8 -*-
# @Time    : 2017/8/2 22:02
# @Author  : 橄榄树

from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.broker import backtesting
from trade.analyzer.analyzer_tushare import Analyzer
from trade.analyzer.transaction import Transaction
from trade.analyzer.tradeposition import TradePosition

import pandas as pd
from trade.feed.csvfeed import GenericBarFeed


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(MyStrategy, self).__init__(feed, 100000)
        self.__position = None
        self.__instrument = instrument
        self.getBroker().setCommission(backtesting.FixedPerTrade(5))
        self.__short_sma = ma.SMA(feed[instrument].getPriceDataSeries(), 4)
        self.__long_sma = ma.SMA(feed[instrument].getPriceDataSeries(), 40)
        self.__analyzer = Analyzer(self, 'hs300')
        self.__transaction = Transaction(self)
        self.__transposition = TradePosition(self)

    def getAnalyzer(self):
        return self.__analyzer

    def getTransposition(self):
        return self.__transposition

    def getTransaction(self):
        return self.__transaction

    def onBars(self, bars):
        if len(self.__long_sma) < 2:
            return
        shares = self.getBroker().getShares(self.__instrument)

        if self.__short_sma[-1] > self.__short_sma[-2] and self.__short_sma[-1] > self.__long_sma[-1] and self.__short_sma[-2] < self.__long_sma[-2]:
            self.marketOrder(self.__instrument, 100, True)

        if self.__long_sma[-1] < self.__long_sma[-2] and self.__short_sma[-1] < self.__long_sma[-1] and self.__short_sma[-2] > self.__long_sma[-2]:
            self.marketOrder(self.__instrument, -1*shares, True)


def run_strategy():
    feed = GenericBarFeed()
    trade_data = pd.read_csv('D:\sh600519.csv')
    instrument = "sh600519"
    feed.addBarsFromDataFrame(instrument, trade_data)
    myStrategy = MyStrategy(feed, instrument)
    myStrategy.run()

    data = myStrategy.getAnalyzer().get_analyzerReturn()
    print data
    data2 = myStrategy.getTransaction().getResultInfo()
    print data2
    data3 = myStrategy.getTransposition().getPosition()
    print data3


run_strategy()
