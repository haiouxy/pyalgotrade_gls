# -*- coding: utf-8 -*-
# @Time    : 2018/4/2 0:23
# @Author  : 橄榄树


from pyalgotrade import strategy
from pyalgotrade.broker import backtesting
from trade.analyzer.analyzer_tushare import Analyzer
from trade.analyzer.transaction import Transaction
from trade.analyzer.tradeposition import TradePosition

from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.model_selection import GridSearchCV

import pandas as pd
import numpy as np
from trade.feed.csvfeed import GenericBarFeed


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, svmstrategy, scaler, period):
        super(MyStrategy, self).__init__(feed, 100000)
        self.__histValue = []
        self.__svmstrategy = svmstrategy
        self.__period = period
        self.__scaler = scaler
        self.__interval = 5
        self.__position = None
        self.__price = 0
        self.__instrument = instrument
        self.getBroker().setCommission(backtesting.FixedPerTrade(5))
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
        bar = bars[self.__instrument]
        close = bar.getPrice()
        self.__histValue.append(close)
        if len(self.__histValue) < self.__period:
            return
        # 确保是最近period 天的数据
        np.delete(self.__histValue, 0, axis=0)
        prodata = self.getProData(bar)
        # 数据进行正则化
        prodata = self.__scaler.transform([prodata])
        self.__interval = self.__interval-1 if self.__interval>0 else 0
        # 预测结果
        ret = self.__svmstrategy.predict(prodata)
        if ret[0] == '1' and self.__position is None:
            self.__price = bar.getPrice()
            self.__position = self.enterLong(self.__instrument, 100, True)
            self.__interval = 5
            # self.marketOrder(self.__instrument, 100, True)
        if self.__interval != 0 and self.__position is not None and ((bar.getPrice()-self.__price)/self.__price > 0.002):
            self.__position.exitMarket()
            self.__position = None
        if self.__interval == 0 and self.__position is not None:
            self.__position.exitMarket()
            self.__position = None

    def getProData(self, bar):
        open = bar.getOpen()
        high = bar.getHigh()
        low = bar.getLow()
        close = bar.getClose()
        volume = bar.getVolume()
        # 计算 15日内的最大值，最小值，以及收益率
        interval_max = np.max(self.__histValue)
        interval_min = np.min(self.__histValue)
        interval_return = (self.__histValue[-1] - self.__histValue[0]) / self.__histValue[0]
        # 封装数据
        prodata = np.array([open, high, low, close, volume, interval_max, interval_min, interval_return])
        return prodata


def run_strategy():
    period = 15
    feed = GenericBarFeed()
    data = pd.read_csv("D:\sh600519.csv")
    feed.addBarsFromDataFrame("sh600519", data)
    scaler, svmstrategy = svm_strategy(data, 15)

    myStrategy = MyStrategy(feed, "sh600519", svmstrategy, scaler, period)

    myStrategy.run()

    data = myStrategy.getAnalyzer().get_analyzerReturn()
    import trade.analyzer.analyzer_db as analyzer_db
    analyzer_db.insert_analyzer('svm', data)
    data2 = myStrategy.getTransaction().getResultInfo()
    analyzer_db.insert_transaction('svm', data2)
    data3 = myStrategy.getTransposition().getPosition()
    analyzer_db.insert_transposition('svm', data3)

# run_strategy(5)


def svm_strategy(tradedata, period):
    tradedata.sort_values(by='date')
    dataframe = tradedata.set_index('date')
    # 删除不需要的值
    dataframe = dataframe.drop(['code', 'money', 'traded_market_value', 'market_value', 'turnover'], axis=1)
    dataframe = dataframe.drop(['adjust_price', 'report_type', 'report_date', 'PE_TTM'], axis=1)
    dataframe = dataframe.drop(['PB', 'PC_TTM', 'PS_TTM', 'adjust_price_f'], axis=1)

    # 经测试  for循环效率比较低，故采用这种方式
    _max = np.frompyfunc(lambda n: np.max(dataframe['close'][n - period:n] if n > period else None), 1, 1)
    interval_max = np.array(_max(np.arange(0, len(dataframe['close']))))
    dataframe['interval_max'] = interval_max

    _min = np.frompyfunc(lambda n: np.min(dataframe['close'][n - period:n] if n > period else None), 1, 1)
    interval_min = np.array(_min(np.arange(0, len(dataframe['close']))))
    dataframe['interval_min'] = interval_min

    _return = np.frompyfunc(lambda n: (dataframe['close'][n] - dataframe['close'][n - period])
                                      / dataframe['close'][n] if n > period else None, 1, 1)
    interval_max = np.array(_return(np.arange(0, len(dataframe['close']))))
    dataframe['interval_return'] = interval_max

    _rise = np.frompyfunc(lambda n: dataframe['rise'][n + period] if n < len(dataframe['close']) - period else None, 1,1)
    interval_rise = np.array(_rise(np.arange(0, len(dataframe['close']))))

    dataframe['rise'] = interval_rise

    dataframe = dataframe.dropna()  # 去掉前后period天无效的数据。

    print dataframe.head()
    dataframe['rise'][dataframe['rise'] > 0] = '1'
    dataframe['rise'][dataframe['rise'] < 0] = '0'
    category = dataframe['rise']

    features = dataframe.drop(['rise'], axis=1)
    scaler = preprocessing.StandardScaler().fit(features)
    features_scaler = scaler.transform(features)

    x_train, x_test, y_train, y_test = train_test_split(features_scaler, category, random_state=1, train_size=0.6)
    svmstrategy = svm.SVC(C=2, kernel='rbf', gamma=0.1)
    svmstrategy.fit(x_test, y_test)
    print svmstrategy.score(x_test, y_test)

    return scaler, svmstrategy





def get_best_svm():
    """
    通过GridSearchCV获取svm模型最优参数
    :return:
    """
    tradedata = pd.read_csv('D:\sh600519.csv')
    tradedata.sort_values(by='date')
    # 周期
    period = 15
    dataframe = tradedata.set_index('date')
    # 删除不需要的值
    dataframe = dataframe.drop(['code', 'money', 'traded_market_value', 'market_value', 'turnover'], axis=1)
    dataframe = dataframe.drop(['adjust_price', 'report_type', 'report_date', 'PE_TTM'], axis=1)
    dataframe = dataframe.drop(['PB', 'PC_TTM', 'PS_TTM', 'adjust_price_f'], axis=1)

    # 经测试  for循环效率比较低，故采用这种方式
    _max = np.frompyfunc(lambda n: np.max(dataframe['close'][n-period:n] if n > period else None), 1, 1)
    interval_max = np.array(_max(np.arange(0, len(dataframe['close']))))
    dataframe['interval_max'] = interval_max

    _min = np.frompyfunc(lambda n: np.min(dataframe['close'][n - period:n] if n > period else None), 1, 1)
    interval_min = np.array(_min(np.arange(0, len(dataframe['close']))))
    dataframe['interval_min'] = interval_min

    _return = np.frompyfunc(lambda n: (dataframe['close'][n]-dataframe['close'][n-period])
                                      / dataframe['close'][n] if n > period else None, 1, 1)
    interval_max = np.array(_return(np.arange(0, len(dataframe['close']))))
    dataframe['interval_return'] = interval_max

    _rise = np.frompyfunc(lambda n: dataframe['rise'][n+period] if n < len(dataframe['close']) - period else None, 1, 1)
    interval_rise = np.array(_rise(np.arange(0, len(dataframe['close']))))

    dataframe['rise'] = interval_rise

    dataframe = dataframe.dropna()  # 去掉前后period天无效的数据。

    print dataframe.head()
    dataframe['rise'][dataframe['rise'] > 0] = '1'
    dataframe['rise'][dataframe['rise'] < 0] = '0'
    category = dataframe['rise']

    features = dataframe.drop(['rise'], axis=1)
    scaler = preprocessing.StandardScaler().fit(features)
    features_scaler = scaler.transform(features)

    x_train, x_test, y_train, y_test = train_test_split(features_scaler, category, random_state=1, train_size=0.6)
    # 通过GridSearchCV 获取csv最优参数
    svmstrategy = svm.SVC(kernel='rbf')
    params = {'C': np.arange(1, 200, 1), 'gamma': np.arange(0.1, 2, 0.1)}
    grid = GridSearchCV(svmstrategy, param_grid=params, cv=5)
    grid = grid.fit(x_train, y_train)
    print grid.best_estimator_
    print grid.best_score_


# get_best_svm()

run_strategy()


