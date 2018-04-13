# -*- coding:utf-8 -*-

# @Time    : '2017/10/30 '
# @Author  : '橄榄树'


class Strategytemplate(object):
    def load(self):
        """
        加载数据
        :return:
        """
        pass

    def execute(self):
        """
        执行算法
        :return:
        """
        pass

    def figure(self):
        """
        计算指标
        :return:
        """
        pass

    def run(self):
        self.load()
        self.execute()
        self.figure()



