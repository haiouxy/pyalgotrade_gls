# -*- coding: utf-8 -*-
# @Time    : 2017/7/29 17:37
# @Author  : 橄榄树

import pandas.io.sql as pandas_sql
from sqlalchemy.schema import MetaData
import sqlalchemy

from trade.db.db_config import engine

"""
数据库操作类，所有关于数据库的操作都应该写在次文件中
"""


class Client(object):
    def __init__(self):
        self.engine = engine
        self.session = pandas_sql
        self.meta = MetaData(self.engine, schema=None)

    def read_sql(self, trade_sql, index_col=None, coerce_float=True, params=None, parse_dates=None, columns=None,
                 chunksize=None):
        return self.session.read_sql(trade_sql, self.engine, index_col, coerce_float, params, parse_dates, columns,
                                     chunksize)

    def execute(self, trade_sql, params=None, cur=None, ):
        return self.session.execute(trade_sql, self.engine, cur, params)

    def isexistforcode(self, table_name):
        try:
            self.meta.reflect(only=[table_name], views=True)
        except sqlalchemy.exc.InvalidRequestError:
            raise ValueError("表 %s 不存在" % table_name)
        return True

client = Client()






