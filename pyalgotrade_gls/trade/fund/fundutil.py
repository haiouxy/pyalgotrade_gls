# -*- coding:utf-8 -*-

# @Time    : '2017/10/30 '
# @Author  : '橄榄树'

import urllib2
import json
import time

from pandas import DataFrame, Series

from trade.db.db_client import client


def get_funddata(url, encoding="utf-8"):
    """
    根据url 获取json文件  对文件先进行解码，然后通过utf-8进行编码
    :param url:  文件的ur
    :param encoding:   解码编码方式
    :return: 如果下载的内容不为空返回 下载的内容否则返回None
    """
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read()
    # decode 为 Unicode编码
    content = content.decode(encoding)
    if len(content) < 100:
        return None
    else:
        return content


def fund_topic_to_frame(content):
    """
    topic 基金数据解析
    :param content:
    :return: fundData
    """

    if content is not None:
        fund_data = content.replace('var topicFundData=', '')
        # json.loads 将对象中所有的值都编码为Unicode
        fund_data = json.loads(fund_data, encoding="utf-8")
        # evel 只将最外层编码为Unicode
        # fund_data = eval(fund_data)
        fund_data = fund_data['Datas']
        fund_data = DataFrame(fund_data)
        fund_data = fund_data.drop('_id', 1).drop('TTYPE', 1).drop('REPORTDATE', 1).drop('ZJZB', 1)
        fund_data = fund_data.drop('SOURCERATE', 1).drop('RATE', 1).drop('ISSALES', 1).drop('ISBUY', 1).drop('MINSG', 1)
        insert_top_to_db(fund_data)


def insert_top_to_db(data):
    """
    基金行情插入操作
    :param data: DataFrame 类型
    :return:
    """
    del_sql = "delete from topicfund"
    if data is not None:
        client.execute(del_sql)

    for index, row in data.iterrows():
        sql_str = "insert into topicfund("
        colnames = "("
        values = []
        for col_name in data.columns:
            sql_str = sql_str + col_name + ","
            colnames = colnames + "%s ,"
            values.append(fill(row[col_name]))
        values.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        sql_str = sql_str + "updatetime)" + "values" + colnames + "%s)"
        client.execute(sql_str, values)


def fund_price_to_frame(content, fund_name, fundcode, index_code=None):
    """
    基金收益率数据解析
    :param content: 爬去的数据
    :param fund_name: 基金名称
    :param fundcode: 所获取的行情数据
    :param index_code: 指标代码
    :return: fundData
    """

    if content is not None:
        # json.loads 将对象中所有的值都编码为Unicode
        fund_price_data = json.loads(content, encoding="utf-8")
        for index in fund_price_data:
            fund_price_name = index['name']
            df = DataFrame(index['data'], columns=['date', 'price'])
            # 基金数据
            if fund_price_name == fund_name:
                insert_price_to_db(df, fundcode)
            # 同类平均
            elif unicode('同类平均'.decode('utf-8')) == fund_price_name:
                insert_price_to_db(df, fundcode+"avg")
            else:
                # 指数指标
                if index_code is not None:
                    insert_price_to_db(df, index_code)


def insert_price_to_db(df, fundcode):
    """
    dataFrame 基金收益数据入库操作
    :param df: 基金收益数据
    :param fundcode: 基金代码
    :return:
    """
    if df is not None:
        client.execute("delete from fundprice where fundcode=%s", [fundcode])
    insert_sql = "insert into fundprice(date,fundcode,price, updatetime)values(%s,%s,%s,%s)"
    for index, row in df.iterrows():
        values = list()
        values.append(stamp_time(row['date']))
        values.append(fundcode)
        values.append(repr(row['price']))
        values.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        client.execute(insert_sql, values)


def fill(value):
    """
    数据进行填充，如果数据为None时返回 0
    :param value:
    :return:
    """
    if value is None or value == "":
        return 0
    else:
        return value


def stamp_time(timestamp):
    """
    将时间戳转换为时间并格式化
    :param timestamp:
    :return:
    """
    time_local = time.localtime(timestamp/1000)
    dt = time.strftime("%Y-%m-%d", time_local)
    return dt


def get_fund_code():
    """
    获取所有前十的基金代码
    :return:
    """
    sql = "select fcode, shortname from topicfund"
    ret = client.execute(sql)
    return ret.fetchall()


def get_fund_unitprice(code, content):
    """

    :return:
    """
    start = content.find('Data_netWorthTrend')
    end = content.find(']', start)
    data = content[start:end + 1]
    data = data.replace('Data_netWorthTrend = ', '')
    df = DataFrame(json.loads(data, encoding='utf-8'))
    df = df.drop('equityReturn', 1).drop('unitMoney', 1)
    df.columns = ['date', 'unitprice']
    insert_unitprice_to_db(df, code[0])


def insert_unitprice_to_db(df, code):
    """
    基金单位净值入库
    :param df:
    :return:
    """
    del_sql ="delete from fundunitprice where fundcode = %s"
    insert_sql = "insert into fundunitprice(fundcode, date, unitprice, updatetime)values(%s, %s, %s, %s)"

    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    if df is not None:
        client.execute(del_sql, [code])
        for index, row in df.iterrows():
            values = list()
            values.append(code)
            values.append(stamp_time(row['date']))
            values.append(repr(row['unitprice']))
            values.append(nowtime)
            client.execute(insert_sql, values)



"""
if __name__ == "__main__":

    fund_topic_to_frame(topicFundData)
    # client.execute("insert into topicfund(FCODE)values(%s)",['s60000'])
"""

"""
if __name__ == "__main__":
    
    fund_price = "http://fund.eastmoney.com/api/PingZhongApi.ashx?m=0&fundcode=660010&" \
                 "indexcode=000300&type=y&_=1510150323776"
    #data = get_funddata(fund_price)
    #fund_price_to_frame(data, '农银策略精选混合', '660010', index_code='000300')

    get_fund_price()

"""

if __name__ == "__main__":
    get_fund_unitprice()





