# -*- coding: utf-8 -*-
# @Time    : 2017/9/20 22:09
# @Author  : 橄榄树


"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

from pyalgotrade import stratanalyzer
from pyalgotrade import broker
from pandas import DataFrame


class TradePosition(stratanalyzer.StrategyAnalyzer):
    """
    统计每日持仓包括
    合约代码 instrument
    现价 price
    头寸 shares
    余额 cash
    账户总额capital
    手续费 commission
    """

    def __init__(self, strategy):
        super(TradePosition, self).__init__()
        self.__capital = 0
        self.__total_commission = 0
        self.__orderInfo = None
        self.__position = None
        self.__trans_position = DataFrame()
        self.__current_date = None
        self.__cash = None

        strategy.attachAnalyzer(self)

    def beforeOnBars(self, strat, bars):

        broker_ = strat.getBroker()
        self.__current_date = str(bars.getDateTime().strftime('%Y-%m-%d'))
        # 账户余额
        self.__cash = broker_.getCash()
        self.__capital = self.__cash
        self.__position = broker_.getPositions()

        # 计算累计手续费
        if self.__orderInfo is not None:
            self.__total_commission += self.__orderInfo.getCommission()

        for instrument, shares in self.__position.iteritems():
            if shares > 0:
                instrumentPrice = bars.getBar(instrument).getClose(broker_.getUseAdjustedValues())
                # 总权益= 账户余额+市值
                self.__capital += instrumentPrice * shares
                info = [self.__current_date, instrument, self.__cash, instrumentPrice, shares, self.__capital,
                        self.__total_commission]
                self.add_trans_position(info)

        if self.__orderInfo is not None and self.__orderInfo.getAction() == "SELL":
                info = [self.__current_date, self.__orderInfo.getInstrument(), self.__cash, self.__orderInfo.getPrice(),
                        0 - self.__orderInfo.getQuantity(), self.__capital,
                        self.__total_commission]
                self.add_trans_position(info)
        self.__orderInfo = None

    def add_trans_position(self, info):
        temp = DataFrame([info], columns=['date', 'instrument', 'cash', 'price', 'shares', 'capital', 'total_commission'])
        self.__trans_position = self.__trans_position.append(temp)

    def getPosition(self):
        if not self.__trans_position.empty:
            self.__trans_position = self.__trans_position.set_index('date')
        return self.__trans_position

    def __onOrderEvent(self, broker_, orderEvent):
        # Only interested in filled or partially filled orders.
        if orderEvent.getEventType() not in (broker.OrderEvent.Type.PARTIALLY_FILLED, broker.OrderEvent.Type.FILLED):
            return
        order = orderEvent.getOrder()
        execInfo = order.getExecutionInfo()
        instrument = order.getInstrument()
        action = order.getAction()
        if action in [broker.Order.Action.BUY, broker.Order.Action.BUY_TO_COVER]:
            action_ = 'BUY'
        elif action in [broker.Order.Action.SELL, broker.Order.Action.SELL_SHORT]:
            action_ = 'SELL'

        self.__orderInfo = OrderInfo(instrument, execInfo.getPrice(), execInfo.getCommission(),
                                     execInfo.getQuantity(), action_)

    def attached(self, strat):
        strat.getBroker().getOrderUpdatedEvent().subscribe(self.__onOrderEvent)


class OrderInfo(object):
    def __init__(self, instrument, price, commission, quantity, action):
        super(OrderInfo, self).__init__()
        self.__instrument = instrument
        self.__price = price
        self.__commission = commission
        self.__quantity = quantity
        self.__action = action

    def getInstrument(self):
        return self.__instrument

    def getPrice(self):
        return self.__price

    def getCommission(self):
        return self.__commission

    def getQuantity(self):
        return self.__quantity

    def getAction(self):
        return self.__action


