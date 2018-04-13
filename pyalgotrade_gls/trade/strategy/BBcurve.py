# -*- coding: utf-8 -*-
# @Time    : 2017/8/2 22:02
# @Author  : 橄榄树

import pandas as pd
import numpy as np

from pyalgotrade import strategy
from pyalgotrade.broker import backtesting

from trade.analyzer.analyzer_tushare import Analyzer
from trade.analyzer.transaction import Transaction
from trade.analyzer.tradeposition import TradePosition
from trade.feed.csvfeed import GenericBarFeed
from trade.technical import BBCurve


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, t, clossarr, alpha):
        super(MyStrategy, self).__init__(feed, 100000)
        self.__position = None
        self.__instrument = instrument
        self.getBroker().setCommission(backtesting.FixedPerTrade(5))
        self.__BBcurve = BBCurve.BBCurve(feed[self.__instrument].getPriceDataSeries(), t, clossarr, alpha)
        self.__analyzer = Analyzer(self, 'hs300')
        self.__transaction = Transaction(self)
        self.__transposition = TradePosition(self)
        self.__Value = []
        self.__bull = None
        self.__bear = None

    def getBBcures(self):
        return self.__BBcurve

    def getValue(self):
        return self.__Value

    def getAnalyzer(self):
        return self.__analyzer

    def getTransposition(self):
        return self.__transposition

    def getTransaction(self):
        return self.__transaction

    def onBars(self, bars):
        bar = bars[self.__instrument]
        shares = self.getBroker().getShares(self.__instrument)
        self.__Value.append(bar.getPrice())
        bull = self.__BBcurve.getBullValue()
        bear = self.__BBcurve.getBearValue()
        if bull[-1] is not None:
            if bar.getPrice() > bull[-1]:
                self.marketOrder(self.__instrument, 100, True)

            if bar.getPrice() < bear[-1]:
                self.marketOrder(self.__instrument, -1 * shares, True)


def run_strategy():
    feed = GenericBarFeed()
    trade_data = pd.read_csv('D:\sh600519.csv')
    instrument = "sh600519"
    feed.addBarsFromDataFrame(instrument, trade_data)
    clossarr = np.array(trade_data['close'])
    # 每period日生成一个布朗运动
    period = 20
    alpha = 0.8
    myStrategy = MyStrategy(feed, instrument, period, clossarr, alpha)

    myStrategy.run()
    data = myStrategy.getAnalyzer().get_analyzerReturn()
    print data
    data2 = myStrategy.getTransaction().getResultInfo()
    print data2
    data3 = myStrategy.getTransposition().getPosition()
    print data3


run_strategy()
