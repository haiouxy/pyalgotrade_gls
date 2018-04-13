# -*- coding: utf-8 -*-
# @Time    : 2017/9/6 0:54
# @Author  : 橄榄树

import numpy as np
from pyalgotrade import stratanalyzer
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.utils import stats


def cov(x, y):
    ret = np.cov(x, y, bias=1, ddof=1)
    return ret[0][1]


class Beta(stratanalyzer.StrategyAnalyzer):
    """
    alpha beta 的计算方法
    """

    def __init__(self):
        super(Beta, self).__init__()
        self.__returns = []
        self.__total_returns = []

        # Only use when self.__useDailyReturns == False
        self.__firstDateTime = None
        self.__lastDateTime = None
        # Only use when self.__useDailyReturns == True
        self.__currentDate = None
        self.__beta = 0.0

    def getReturns(self):
        return self.__returns

    def beforeAttach(self, strat):
        # Get or create a shared ReturnsAnalyzerBase
        analyzer = returns.ReturnsAnalyzerBase.getOrCreateShared(strat)
        analyzer.getEvent().subscribe(self.__onReturns)

    def __onReturns(self, dateTime, returnsAnalyzerBase):
        # 每日收益
        netReturn = returnsAnalyzerBase.getNetReturn()
        # 累计收益
        CumulativeReturn = returnsAnalyzerBase.getCumulativeReturn()
        self.__returns.append(netReturn)
        self.__total_returns.append(CumulativeReturn)

    def getBeta(self, riskRate):
        ret = 0.0
        # tushare获取的涨跌幅数据已*100 故在此/100
        volatility = stats.stddev(np.array(riskRate)/100, 1)
        if volatility != 0 and not np.isnan(volatility):
            ret = cov(np.array(self.__returns), np.array(riskRate)/100) / pow(volatility, 2)
        self.__beta = ret
        return ret

    def getAlpha(self, riskRate):
        ret = 0.0
        if len(self.__returns) > 0:
            ret = self.__total_returns[-1] - 0.04 - (self.__beta * riskRate[-1]/100)
        return ret
