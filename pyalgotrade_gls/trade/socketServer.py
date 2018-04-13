# -*- coding: utf-8 -*-
# @Time    : 2017/7/9 18:16
# @Author  : 橄榄树

import asyncore
import socket

from trade.proxy import Proxy


class Handler(asyncore.dispatcher_with_send):

    def __init__(self, sock):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.result = {}

    def handle_read(self):
        """
        当socket有可读的数据的时候执行这个方法
        :return:
        """
        code = self.recv(48)
        if code is not None and len(code) > 0:
            proxy = Proxy(code)
            proxy.run()
            self.result['_RejCode'] = "0000"

    def handle_write(self):
        self.send(repr(self.result))
        self.result = {}

    def writable(self):
        return (not self.connected) or len(self.result)


class Server(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.result = {}
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        # 监听链接的最大数  默认为5
        self.listen(5)

    def handle_accept(self):
        """
        当客户端链接的时候
        :return:
        """
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            Handler(sock)


server = Server('localhost', 9988)
asyncore.loop()




