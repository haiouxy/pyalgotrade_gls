# -*- coding: utf-8 -*-
# @Time    : 2017/7/9 18:16
# @Author  : 橄榄树


import time
import traceback
from pandas import DataFrame

from trade.db.db_client import client
from trade.utils import utils


class Proxy(object):

    def __init__(self, job_id):
        self._job_id = job_id
        self._job_frame = DataFrame()

    def _get_instance(self, jobid):
        # 根据jobid 获取job其他信息
        # job = self._job_frame[self._job_frame['jobid'].isin([jobid])]
        config = get_job(self._job_id)
        obj = utils.instance(config['pyth'], config['class'])
        return obj

    def _insert_log(self, status, msg):
        values = [self._job_id]
        date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        values.append(date)
        count_sql = 'select jobid from joblog where jobid=%s and date = %s'
        insert_sql = 'INSERT INTO joblog (jobid, date, jobstatus,msg, createtime) VALUES (%s, %s, %s,%s,%s)'
        update_sql = 'update joblog set jobstatus= %s,msg=%s,updatetime=%s where jobid=%s and date=%s'
        count = client.execute(count_sql, values).fetchall()
        if len(count) < 1:
            # 插入
            values.append(status)
            values.append(msg)
            values.append(nowtime)
            client.execute(insert_sql, values)
        else:
            # 更新
            updatevalue = list()
            updatevalue.append(status)
            updatevalue.append(msg)
            updatevalue.append(nowtime)
            updatevalue.append(self._job_id)
            updatevalue.append(date)
            client.execute(update_sql, updatevalue)

    def run(self):
        error_msg = ''
        status = 'S'
        try:
            obj = self._get_instance(self._job_id)
            instance = obj()
            instance.run()
        except Exception, e:
            status = 'F'
            error_msg = e[0:200]
            traceback.print_exc()
        finally:
            self._insert_log(status, error_msg)


def get_job(jobid):
    config = dict()
    sql = "select jobid,path,class from jobconfig where jobtype ='python' and jobid=%s"
    ret = client.execute(sql, [jobid]).fetchall()
    if len(ret) < 1:
        raise Exception('配置信息不存在')
    else:
        data = ret[0]
        config['jobid'] = str(data[0]).encode('utf-8')
        config['pyth'] = str(data[1]).encode('utf-8')
        config['class'] = str(data[2]).encode('utf-8')
    return config


if __name__ == "__main__":

    proxy = Proxy('Job005')
    proxy.run()
    #proxy = Proxy('Job005')
    #proxy.run()
