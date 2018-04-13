# -*- coding: utf-8 -*-
# @Time    : 2017/9/6 0:54
# @Author  : 橄榄树

import datetime

from pandas import DataFrame
from pyalgotrade.stratanalyzer import returns, sharpe, drawdown
from pyalgotrade import dataseries
import pandas as pd
import numpy as np
from beta import Beta


class Analyzer(object):
    """
    此类是对pyalgotrade中原有的stratanalyzer进行封装
    将所有的分析结果都在此类中处理，并对结果进行保存
    """
    def __init__(self, strategy, index_code=None):
        """
        :param strategy: 策略
        :param index_code: index基准利率代码应该同tushare保持一致
        sh 上证指数 sz 深圳成指 hs300 沪深300指数 sz50 上证50指数 zxb 中小板指数 cyb 创业板指数
        :return:
        """
        self.__baseRet_code = index_code
        self.__baseRet_data = None
        self.__currBaseRet = []
        self.__last_baseRet = 0.0
        self.__baseRet = dataseries.SequenceDataSeries()
        self.__betaRet = dataseries.SequenceDataSeries()
        self.__alphaRet = dataseries.SequenceDataSeries()
        self.__sharpeRet = dataseries.SequenceDataSeries()
        self.__LongestDrawDown = dataseries.SequenceDataSeries()
        self.__MaxDrawDown = dataseries.SequenceDataSeries()
        self.__ret_analyzer = returns.Returns()
        self.__sharpe_ratio = sharpe.SharpeRatio(False)
        self.__draw_down = drawdown.DrawDown()
        self.__beta = Beta()

        strategy.attachAnalyzer(self.__ret_analyzer)
        strategy.attachAnalyzer(self.__sharpe_ratio)
        strategy.attachAnalyzer(self.__draw_down)
        strategy.attachAnalyzer(self.__beta)
        strategy.attachAnalyzer(self)

    def get_analyzerReturn(self):
        analyzerReturn = DataFrame()
        if self.__baseRet_code is not None:
            analyzerReturn["baseRet"] = np.array(self.__baseRet)
        analyzerReturn["date"] = np.array(self.__ret_analyzer.getReturns().getDateTimes())
        analyzerReturn['current_returns'] = np.array(self.__ret_analyzer.getReturns()) * 100
        analyzerReturn['total_returns'] = np.array(self.__ret_analyzer.getCumulativeReturns()) * 100
        analyzerReturn['MaxDrawDown'] = np.array(self.__MaxDrawDown) * 100
        analyzerReturn['LongestDrawDownDuration'] = np.array(self.__LongestDrawDown)
        analyzerReturn['sharpe'] = np.array(self.__sharpeRet)
        analyzerReturn['beta'] = np.array(self.__betaRet)
        analyzerReturn['alpha'] = np.array(self.__alphaRet)
        analyzerReturn = analyzerReturn.set_index('date')
        return analyzerReturn

    def __get_baseRet_data(self, bars):
        if self.__baseRet_code is not None:
            startdate = str((bars.getDateTime()-datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
            import tushare as ts
            data = ts.get_hist_data(self.__baseRet_code, start=startdate)
            self.__baseRet_data = pd.DataFrame(data)

    def __append_baseRet(self, bars):
        date = str(bars.getDateTime().strftime('%Y-%m-%d'))
        self.__last_baseRet = self.__last_baseRet + self.__baseRet_data['p_change'][date]
        # 当日涨跌幅
        self.__currBaseRet.append(self.__baseRet_data['p_change'][date])
        # 累计涨跌幅
        self.__baseRet.appendWithDateTime(date, self.__last_baseRet)

    def beforeOnBars(self, strat, bars):

        if self.__baseRet_code is not None and self.__baseRet_data is None:
            self.__get_baseRet_data(bars)
            self.__append_baseRet(bars)
        else:
            self.__append_baseRet(bars)

        self.__LongestDrawDown.appendWithDateTime(str(bars.getDateTime().strftime('%Y-%m-%d')),
                                                  self.__draw_down.getLongestDrawDownDuration().days)
        self.__MaxDrawDown.appendWithDateTime(str(bars.getDateTime().strftime('%Y-%m-%d')),
                                              self.__draw_down.getMaxDrawDown())
        self.__sharpeRet.appendWithDateTime(str(bars.getDateTime().strftime('%Y-%m-%d')),
                                            self.__sharpe_ratio.getSharpeRatio(0.04))
        self.__betaRet.appendWithDateTime(str(bars.getDateTime().strftime('%Y-%m-%d')),
                                          self.__beta.getBeta(np.array(self.__currBaseRet)))
        self.__alphaRet.appendWithDateTime(str(bars.getDateTime().strftime('%Y-%m-%d')),
                                           self.__beta.getAlpha(np.array(self.__baseRet)))

    def beforeAttach(self, strat):
        pass

    def attached(self, strat):
        pass



