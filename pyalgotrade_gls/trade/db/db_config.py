# -*- coding: utf-8 -*-
# @Time    : 2017/6/18 21:48
# @Author  : 橄榄树

from sqlalchemy import create_engine

config = {
    "host": "192.168.136.128",
    "port": "3306",
    "user": "guanju",
    "password": "guanju",
    "schema": "guanju",
}

# DB_CONNECT_URL = "mysql+pymysql://guanju:guanju@192.168.136.128:3306/guanju?charset=utf8"

DB_CONNECT_URL = "mysql+pymysql://"+config['user']+":" +\
                 config['password']+"@" +\
                 config['host']+":" +\
                 config['port']+"/" +\
                 config['schema']+"?charset=utf8"
engine = create_engine(DB_CONNECT_URL, encoding='utf8', echo=True, strategy='threadlocal')

