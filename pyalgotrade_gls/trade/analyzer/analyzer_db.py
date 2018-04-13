# -*- coding: utf-8 -*-
# @Time    : 2017/9/24 0:40
# @Author  : 橄榄树

from trade.db.db_client import client
import time


def insert_analyzer(strategyid, data):
    """
    插入分析指标
    :param strategy: 策略名   不同的策略更新数据到相应的表中
    :param data: data={'instrument':'sh000001','date':'2017-09-23'}
    :return:
    """
    del_sql ="delete from analyzer where strategyid = %s"
    insert_sql = "insert into analyzer(strategyid, date, current_returns, total_returns," \
                 "LongestDrawDownDuration, MaxDrawDown, sharpe, beta,alpha, baserate, createtime)" \
                 "values(%s, %s, %s, %s,%s, %s,%s, %s, %s,%s,%s)"

    client.execute(del_sql, [strategyid])
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for index in data.index:
        temp = data.ix[index]
        values = [strategyid, index.strftime('%Y-%m-%d'), str(temp['current_returns']), str(temp['total_returns']),
                  str(temp['LongestDrawDownDuration']), str(temp['MaxDrawDown']), str(temp['sharpe']), str(temp['beta']),
                  str(temp['alpha']), str(temp['baseRet']), nowtime]
        client.execute(insert_sql, values)


def insert_transaction(strategyid, data):
    """
    插入分析指标
    :param strategy: 策略名   不同的策略更新数据到相应的表中
    :param data: data={'instrument':'sh000001','date':'2017-09-23'}
    :return:
    """
    del_sql ="delete from transaction where strategyid = %s"
    insert_sql = "insert into transaction(strategyid, date, instrument, action, price, quantity, commission, createtime)" \
                 "values(%s, %s, %s, %s,%s, %s, %s,%s)"

    client.execute(del_sql, [strategyid])
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for index in data.index:
        temp = data.ix[index]
        values = [strategyid, index, temp['instrument'], temp['action'], str(temp['price']),
                  str(temp['quantity']), str(temp['commission']), nowtime]
        client.execute(insert_sql, values)


def insert_transposition(strategyid, data):
    """
    插入分析指标
    :param strategy: 策略名   不同的策略更新数据到相应的表中
    :param data: data={'instrument':'sh000001','date':'2017-09-23'}
    :return:
    """
    del_sql ="delete from transposition where strategyid = %s"
    insert_sql = "insert into transposition(strategyid, date, instrument, cash, price, shares, " \
                 "capital, total_commission, createtime)" \
                 "values(%s, %s, %s, %s,%s, %s, %s,%s,%s)"

    client.execute(del_sql, [strategyid])
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for index in data.index:
        temp = data.ix[index]
        values = [strategyid, index, temp['instrument'], str(temp['cash']), str(temp['price']), str(temp['shares']),
                  str(temp['capital']), str(temp['total_commission']), nowtime]
        client.execute(insert_sql, values)


