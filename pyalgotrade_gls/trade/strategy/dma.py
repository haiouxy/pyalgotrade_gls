# -*- coding: utf-8 -*-
# @Time    : 2017/8/2 22:02
# @Author  : 橄榄树

from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import macd
from pyalgotrade.broker import backtesting
from trade.analyzer.analyzer_tushare import Analyzer
from trade.analyzer.transaction import Transaction
from trade.analyzer.tradeposition import TradePosition

from trade.technical import dma
import pandas as pd
# from trade.feed.genericbarfeed import GenericBarFeed
from trade.feed.csvfeed import GenericBarFeed

import trade.analyzer.analyzer_db as analyzer_db
from trade.feed.feed_db import FeedClient


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        super(MyStrategy, self).__init__(feed, 100000)
        self.__position = None
        self.__instrument = instrument
        self.getBroker().setCommission(backtesting.FixedPerTrade(5))
        # 指数数据
        # self.setUseAdjustedValues(False)
        self.__dma = dma.DMA(feed[instrument].getPriceDataSeries(), 30, 10, 10)
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
        if len(self.__dma.getDMA()) < 2:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        shares = self.getBroker().getShares(self.__instrument)
        dma = self.__dma.getDMA()
        ama = self.__dma.getAMA()

        if dma[-1] > dma[-2] and dma[-1] > ama[-1] and dma[-2] < ama[-2]:
            self.marketOrder(self.__instrument, 100, True)

        if dma[-1] < dma[-2] and dma[-1] < ama[-1] and dma[-2] > ama[-2]:
            self.marketOrder(self.__instrument, -1*shares, True)

        """
        if bar.getPrice() > self.__sma[-1]:
            self.marketOrder(self.__instrument, 100, True)

        # Check if we have to exit the position.
        elif bar.getPrice() <= self.__sma[-1]:
            self.marketOrder(self.__instrument, -1*shares, True)
        """

def run_strategy(smaPeriod):
    feed = GenericBarFeed()
    # feed = yahoofeed.Feed()
    feed.addBarsFromCSV("sh600519", "D:\sh600519.csv")
    #tradedata = ts.get_hist_data("600848", start='2017-12-05')
    #startdate = "2017-12-05"
    enddate = "2017-09-25"
    #client = FeedClient()
    #data = pd.DataFrame(client.get_trade_index("sh600848", startdate))
    #tradedata['date'] = tradedata.index
    #feed.addBarsFromCSV("orcl", "D:\orcl-2000.csv")
    #feed.addBarsFromCSV("java", "D:\orcl-2000.csv")
    #feed.addBarsFromDataFrame("600848", data)

    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, "sh600519", smaPeriod)

    myStrategy.run()

    data = myStrategy.getAnalyzer().get_analyzerReturn()
    analyzer_db.insert_analyzer('sma', data)
    data2 = myStrategy.getTransaction().getResultInfo()
    analyzer_db.insert_transaction('sma', data2)
    data3 = myStrategy.getTransposition().getPosition()
    analyzer_db.insert_transposition('sma', data3)

run_strategy(5)
