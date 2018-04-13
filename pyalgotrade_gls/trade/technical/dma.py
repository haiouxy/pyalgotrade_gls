# -*- coding: utf-8 -*-
# @Time    : 2017/8/2 22:02
# @Author  : 橄榄树

from pyalgotrade.technical import ma
from pyalgotrade import dataseries


class DMA(dataseries.SequenceDataSeries):

    def __init__(self, dataSeries, fastMA, slowMA, signalMA, maxLen=None):
        assert(fastMA > 0)
        assert(slowMA > 0)
        assert(fastMA > slowMA)
        assert(signalMA > 0)

        super(DMA, self).__init__(maxLen)

        # We need to skip some values when calculating the fast EMA in order for both EMA
        # to calculate their first values at the same time.
        # I'M FORCING THIS BEHAVIOUR ONLY TO MAKE THIS FITLER MATCH TA-Lib MACD VALUES.
        self.__skip = fastMA - slowMA

        self.__fastMAWindow = ma.SMAEventWindow(fastMA)
        self.__slowMAWindow = ma.SMAEventWindow(slowMA)
        self.__signalMAWindow = ma.SMAEventWindow(signalMA)
        self.__ama = dataseries.SequenceDataSeries(maxLen)
        self.__dma = dataseries.SequenceDataSeries(maxLen)
        dataSeries.getNewValueEvent().subscribe(self.__onNewValue)

    def getAMA(self):
        return self.__ama

    def getDMA(self):
        return self.__dma

    def __onNewValue(self, dataSeries, dateTime, value):
        dma = None
        ama = None

        self.__slowMAWindow.onNewValue(dateTime, value)

        if self.__skip > 0:
            self.__skip -= 1
        else:
            self.__fastMAWindow.onNewValue(dateTime, value)
            if self.__fastMAWindow.windowFull():
                dma = self.__fastMAWindow.getValue() - self.__slowMAWindow.getValue()

        self.__signalMAWindow.onNewValue(dateTime, dma)
        if self.__signalMAWindow.windowFull():
            ama = self.__signalMAWindow.getValue()

        self.__dma.appendWithDateTime(dateTime, dma)
        self.__ama.appendWithDateTime(dateTime, ama)