# -*- coding: utf-8 -*-
# @Time    : 2017/8/2 22:02
# @Author  : 橄榄树

import datetime

from trade.db.db_client import client


def insert_stock_basics_db(data):

        del_sql = "delete from stock"
        client.execute(del_sql)
        insert_sql = "insert into stock(code, name, industry, area, updatetime)values(%s, %s, %s, %s,%s)"
        nowdate = datetime.datetime.now()

        for index in data.index:
            temp = data.ix[index]
            values = [str(index), str(temp['name']), str(temp['industry']), str(temp['area']), nowdate]
            client.execute(insert_sql, values)


def insert_stock_index_db(data):

        del_sql = "delete from stock_index"
        client.execute(del_sql)
        insert_sql = "insert into stock_index(code, name, industry, area, updatetime)values(%s, %s,%s,%s,%s)"
        nowdate = datetime.datetime.now()

        for index in data.index:
            temp = data.ix[index]
            values = [str(temp['code']), str(temp['name']), '指数', '指数',nowdate]
            client.execute(insert_sql, values)


def insert_stock_element_db(element_type, data):
    del_sql = "delete from stock_element"
    client.execute(del_sql)
    insert_sql = "insert into stock_element(type, code, name, weight, createtime)values(%s, %s,%s,%s,%s)"
    nowdate = datetime.datetime.now()

    for index in data.index:
        temp = data.ix[index]
        if element_type == "50":
            values = [element_type, str(temp['code']), temp['name'], 0.00, nowdate]
        else:
            values = [element_type, str(temp['code']), temp['name'], str(temp['weight']), nowdate]
        client.execute(insert_sql, values)

