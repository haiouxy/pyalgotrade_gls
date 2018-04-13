# -*- coding: utf-8 -*-
# @Time    : 2017/8/2 22:02
# @Author  : 橄榄树

import scipy.stats as ss
import numpy as np

from pyalgotrade.technical import ma
from pyalgotrade import dataseries
from pyalgotrade import technical


class BullCurveEventWindow(technical.EventWindow):

    def __init__(self, period, mean, sigma, alpha):
        assert(period > 0)
        super(BullCurveEventWindow, self).__init__(period)
        self.__index = -1
        self.__mean = mean
        self.__sigma = sigma
        self.__a = ss.t.ppf(1-alpha/2, period)
        self.__hisValue = []
        self.__value = None

    def onNewValue(self, dateTime, value):
        super(BullCurveEventWindow, self).onNewValue(dateTime, value)
        self.__hisValue.append(value)

        if value is not None and self.windowFull():
            self.__index += 1
            self.__value = np.log(self.__hisValue[self.__index]) + self.__mean[self.__index] * \
                           self.getWindowSize() + self.__a * self.__sigma[self.__index] * np.sqrt(self.getWindowSize())
        if self.__value is not None:
            self.__value = np.exp(self.__value)

    def getValue(self):
        return self.__value


class BearCurveEventWindow(technical.EventWindow):
    def __init__(self, period, mean, sigma, alpha):
        assert(period > 0)
        super(BearCurveEventWindow, self).__init__(period)
        self.__index = -1
        self.__mean = mean
        self.__sigma = sigma
        self.__a = ss.t.ppf(1-alpha/2, period)
        self.__hisValue = []
        self.__value = None

    def onNewValue(self, dateTime, value):
        super(BearCurveEventWindow, self).onNewValue(dateTime, value)
        self.__hisValue.append(value)

        if value is not None and self.windowFull():
            self.__index += 1
            self.__value = np.log(self.__hisValue[self.__index]) + self.__mean[self.__index] * \
                           self.getWindowSize() - self.__a * self.__sigma[self.__index] * np.sqrt(self.getWindowSize())
        if self.__value is not None:
            self.__value = np.exp(self.__value)

    def getValue(self):
        return self.__value


class BBCurve(dataseries.SequenceDataSeries):

    def __init__(self, dataSeries, period, clossarr, alpha, maxLen=None):
        """
        :param dataSeries:
        :param period:  没几日产生一次布朗运动
        :param clossarr: 收盘价数组，用于计算均值和方差
        :param alpha: 牛熊线间的置信度为(1-alpha)
        :param maxLen:
        """
        super(BBCurve, self).__init__(maxLen)
        self.__index = 0
        self.__period = period
        self.__bull = []
        self.__bear = []
        mean = self.getMean(clossarr)
        sigma = self.getVar(clossarr)
        self.__bullllCurveEventWindow = BullCurveEventWindow(period, mean, sigma, alpha)
        self.__bearCurveEventWindow = BearCurveEventWindow(period, mean, sigma, alpha)

        dataSeries.getNewValueEvent().subscribe(self.__onNewValue)

    def getBullValue(self):
        return self.__bull

    def getBearValue(self):
        return self.__bear

    def __onNewValue(self, dataSeries, dateTime, value):
        self.__index += 1

        self.__bullllCurveEventWindow.onNewValue(dateTime, value)
        self.__bearCurveEventWindow.onNewValue(dateTime, value)
        bull = self.__bullllCurveEventWindow.getValue()
        bear = self.__bearCurveEventWindow.getValue()

        self.__bull.append(bull)
        self.__bear.append(bear)

    def getMean(self, clossarr):
        # 对数日收益率序列
        logreturns = np.diff(np.log(clossarr))
        _mean = np.frompyfunc(lambda n: np.mean(logreturns[n:self.__period+n]), 1, 1)
        mean = np.array(_mean(np.arange(0, len(clossarr) - self.__period+1)))
        return mean

    def getVar(self, clossarr):
        # 对数日收益率序列
        logreturns = np.diff(np.log(clossarr))
        _var = np.frompyfunc(lambda n: np.var(logreturns[n:self.__period+n]), 1, 1)
        var = np.array(_var(np.arange(0, len(clossarr) - self.__period+1)))
        return np.sqrt(var.astype(float))
