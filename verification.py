# /usr/bin/python
# encoding:utf8

# 验证代理IP的可行性

import socks
import time
import socket
from threading import Thread
import signal

_ip = ''
_port = 0
_mode = None

_tld_info = {
    'cn': {'domain': 'baidu.cn', 'whois_addr': '218.241.97.14', 'true_info': 'Domain Name: baidu.cn' },
    # 'com_A': {'domain': 'baidu.com', 'whois_addr': 'whois.verisign-grs.com', 'true_info': 'BAIDU.COM.CN' },
    # 'com_B': {'domain': 'baidu.com', 'whois_addr': 'whois.crsnic.net', 'true_info': 'BAIDU.COM.CN'},
    # 'cross': {'domain': 'registry.google', 'whois_addr': 'domain-registry-whois.l.google.com', 'true_info': 'Domain Name: registry.google' },
}

class TimeoutException(Exception):
    pass
 
ThreadStop = Thread._Thread__stop # 获取私有函数
 
def timelimited(timeout):
    def decorator(function):
        def decorator2(*args,**kwargs):
            class TimeLimited(Thread):
                def __init__(self,_error= None,):
                    Thread.__init__(self)
                    self._error =  _error
                     
                def run(self):
                    try:
                        self.result = function(*args,**kwargs)
                    except Exception,e:
                        self._error =e
 
                def _stop(self):
                    if self.isAlive():
                        ThreadStop(self)
 
            t = TimeLimited()
            t.setDaemon(True) # 守护线程
            t.start()
            t.join(timeout)

            if isinstance(t._error,TimeoutException):
                t._stop()
                raise TimeoutException('timeout for %s' % (repr(function)))
 
            if t.isAlive():
                t._stop()
                raise TimeoutException('timeout for %s' % (repr(function)))
 
            if t._error is None:
                return t.result
 
        return decorator2
    return decorator


# 验证
# @param ip
# @param port
# @param mode socks 方式(4 or 5)
# return speed_cn, speed_com, speed_cross
def verification(ip, port, mode):

    __set(ip, port, mode)
    # print '验证 ', ip, ' ', port
    speed_cn = get_speed('cn')
    # speed_com_A = get_speed('com_A')
    # speed_com_B = get_speed('com_B')
    # speed_cross = get_speed('cross')
    # print 'speed_cn : ', speed_cn
    return speed_cn, -1, -1, -1

def get_speed(tld):
    global _tld_info
    
    domain = _tld_info[tld]['domain']
    whois_addr = _tld_info[tld]['whois_addr']
    true_info = _tld_info[tld]['true_info']
    
    recv_date = None
    return_speed = -1
    for i in range(2):
        tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if return_speed != -1:
            tcpCliSock.close()
            break
        begin_time = time.time()
        try:
            recv_date = get_recv_info(domain, whois_addr, tcpCliSock)
        except Exception, e:
            recv_date = None
        speed = time.time() - begin_time

        if recv_date != None and recv_date.find(true_info) != -1:
            return_speed = speed
        tcpCliSock.close()

    return return_speed


def __set(ip, port, mode):
    global _ip, _port, _mode
    _ip = ip
    _port = port
    _mode = socks.PROXY_TYPE_SOCKS4 if mode == 4 else socks.PROXY_TYPE_SOCKS5


# 与whois服务连接获取whois信息
@timelimited(20)
def get_recv_info(domain, whois_addr, tcpCliSock):
    # global _ip, _port, _mode

    HOST = whois_addr
    data_result = ""
    PORT = 43           # 端口
    BUFSIZ = 1024       # 每次返回数据大小
    ADDR = (HOST, PORT)
    EOF = "\r\n"
    data_send = domain + EOF
    socks.setdefaultproxy(proxytype = _mode, addr = _ip, port = _port)
    socket.socket = socks.socksocket
    try:
        tcpCliSock.connect(ADDR)
        tcpCliSock.send(data_send)
    except socket.error, e:
        return
        # if str(e).find("time out") != -1: #连接超时
        #     return "ERROR -1"
        # elif str(e).find("Temporary failure in name resolution") != -1:
        #     return "ERROR -2"
        # else:
        #     return 'ERROR other'

    while True:
        try:
            data_rcv = tcpCliSock.recv(BUFSIZ)
        except socket.error, e:
            return
        if not len(data_rcv):
            return data_result  # 返回查询结果
        data_result = data_result + data_rcv  # 每次返回结果组合


if __name__ == '__main__':
    # tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print get_recv_info('baidu.cn', '218.241.97.14', tcpCliSock)
    print verification(ip = '121.40.102.199', port = 1080, mode = 4)
