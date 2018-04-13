# -*- coding: utf-8 -*-
# @Time    : 2017/9/21 23:04
# @Author  : 橄榄树


from pyalgotrade import stratanalyzer
from pyalgotrade import broker
from pandas import DataFrame


class Transaction(stratanalyzer.StrategyAnalyzer):
    """
        交易详情
    """

    def __init__(self, strategy):
        super(Transaction, self).__init__()
        self.__resultInfo = DataFrame()
        self.__execInfo = None
        self.__instrument = None
        self.__price = 0.0
        self.__commission = None
        self.__quantity = None
        self.__currentDate = None
        self.__action = None

        strategy.attachAnalyzer(self)

    def getResultInfo(self):
        if not self.__resultInfo.empty:
            self.__resultInfo = self.__resultInfo.set_index('date')
        return self.__resultInfo

    def __onOrderEvent(self, broker_, orderEvent):
        # Only interested in filled or partially filled orders.
        if orderEvent.getEventType() not in (broker.OrderEvent.Type.PARTIALLY_FILLED, broker.OrderEvent.Type.FILLED):
            return
        order = orderEvent.getOrder()
        execInfo = order.getExecutionInfo()
        self.__instrument = order.getInstrument()
        action = order.getAction()
        if action in [broker.Order.Action.BUY, broker.Order.Action.BUY_TO_COVER]:
            self.__action = 'BUY'
        elif action in [broker.Order.Action.SELL, broker.Order.Action.SELL_SHORT]:
            self.__action = 'SELL'

        self.__execInfo = execInfo
        # 成交价格
        self.__price = execInfo.getPrice()
        # 手续费
        self.__commission = execInfo.getCommission()
        # 交易量
        self.__quantity = execInfo.getQuantity()
        # 交易时间
        self.__currentDate = execInfo.getDateTime()
        self.__update_resultInfo()

    def attached(self, strat):
        strat.getBroker().getOrderUpdatedEvent().subscribe(self.__onOrderEvent)

    def __update_resultInfo(self):
        info = [self.__currentDate.strftime('%Y-%m-%d'), self.__instrument, self.__action, self.__price,
                self.__quantity, self.__commission]
        temp = DataFrame([info], columns=['date', 'instrument', 'action', 'price', 'quantity', 'commission'])
        self.__resultInfo = self.__resultInfo.append(temp, ignore_index=True)








