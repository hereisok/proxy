#!/usr/bin/python
# encoding:utf-8

#
# 数据库操作模块
# @author 王凯
#

import MySQLdb
import sys
import datetime
import ConfigParser
import threading

reload(sys)
sys.setdefaultencoding('utf8')


class DataBase :
    # 数据库初始化
    def __init__(self):
        self.host = ''
        self.user = ''
        self.passwd = ''
        self.charset = 'utf8'
        self.db_lock = threading.Lock() # 数据库操作锁

    # 执行连接数据库操作
    def get_connect(self):
        if self.db_lock.acquire():
            try:
                self.conn = MySQLdb.Connection(
                    host = self.host, user = self.user, passwd = self.passwd, charset = self.charset)
            except MySQLdb.Error, e:
                print 'get_connect error_info: %d: %s' % (e.args[0], e.args[1])
            
            self.cursor = self.conn.cursor()
            if not self.cursor:
                raise(NameError, "Connect failure")

            # # 设置编码
            # try:
            #     self.cursor.execute('SET character_set_connection=utf8, character_set_results=utf8, character_set_client=utf8')
            # except MySQLdb.Error, e:  
            #     print str(datetime.datetime.now()).split(".")[0], "ERROR %d: %s" % (e.args[0], e.args[1])
            self.db_lock.release()

    # 关闭数据库链接
    def db_close(self):
        if self.db_lock.acquire():
            try:
                self.conn.close()
            except MySQLdb.Error, e: 
                print 'db_close error_info: %d: %s' % (e.args[0], e.args[1])
            self.db_lock.release()

    #　commit
    def db_commit(self):
        if self.db_lock.acquire():
            try:
                self.conn.commit()
            except MySQLdb.Error, e:  
                print 'db_commit error_info: %d: %s' % (e.args[0], e.args[1])
            self.db_lock.release()
    
    # 数据库数据查找
    # @param args['nature'] 查询性质
    def db_select(self, **args):

        if args['nature'] == 'proxy_ip':
            sql = """SELECT id FROM WK.proxy WHERE ip = '{ip}' and port = {port};"""\
            .format(ip = args['ip'], port = args['port'])

        elif args['nature'] == 'all_proxy_table':
            sql = """SELECT ip, port, mode FROM WK.proxy \
            WHERE UNIX_TIMESTAMP(verification_time) < UNIX_TIMESTAMP('{query_time}') LIMIT 20"""\
            .format(query_time = args['query_time'])

        
        return self.__execute__(sql) if sql else None
       
    # 数据库数据插入
    # @param args['nature'] 插入性质
    def db_insert(self, **args):

        if args['nature'] == 'proxy_ip':
            sql = """INSERT INTO WK.proxy(ip, port, mode, other, insert_time, verification_time)\
            VALUES('{ip}', {port}, {mode}, '{other}', '{insert_time}', '{verification_time}');""".format(
                ip = args['ip'], 
                port = args['port'], 
                mode = args['mode'],
                other = args['other'], 
                insert_time = args['insert_time'],
                verification_time = args['verification_time'])
            self.__execute__(sql)


    # whois数据更新
    # @param args['nature'] 更新性质
    def db_update(self, **args):

        if args['nature'] == 'proxy_ip':
            sql = """UPDATE WK.proxy SET speed_cn = {speed_cn}, speed_com_A = {speed_com_A}, \
            speed_com_B = {speed_com_B}, speed_cross = {speed_cross}, verification_time = '{verification_time}' \
            WHERE ip = '{ip}' and port = {port}""".format(
                speed_cn = args['speed_cn'],
                verification_time = args['verification_time'], 
                ip = args['ip'],
                port = args['port'],
                speed_com_A = args['speed_com_A'],
                speed_com_B = args['speed_com_B'],
                speed_cross = args['speed_cross'])
            self.__execute__(sql)

    # 删除whois记录信息
    # @param args['nature'] 删除性质
    def db_delete(self, **args):
        
        if args['nature'] == 'proxy_ip':
            sql = """DELETE FROM WK.proxy WHERE ip = '{ip}' and port = {port}""".format(ip = args['ip'], port = args['port'])
            self.__execute__(sql)

    # 执行sql语句
    # @param sql sql语句
    def __execute__(self, sql):

        result = None
        if self.db_lock.acquire():
            try:
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
            except MySQLdb.Error, e:
                if e.args[0] == 2013 or e.args[0] == 2006: # 数据库连接出错，重连
                    self.db_lock.release()
                    self.get_connect()
                    result = self.__execute__(sql) # 重新执行
                    self.db_lock.acquire()
                else:
                    print 'db_execute error_info: %d: %s' % (e.args[0], e.args[1])
            self.db_lock.release()

        return result if result else None

if __name__ == '__main__':

    DB = DataBase()
    DB.get_connect()
    DB.db_insert('proxy_ip', 
        {'ip': '123.56.100.105',
        "port": 1080,
        "mode": 5,
        'other': '北京市 阿里云BGP数据中心', 
        'insert_time': str(datetime.datetime.now()).split(".")[0]
        }
        )

    DB.db_commit()

    print DB.db_select('proxy_ip', '123.56.100.105')
    print DB.db_select('proxy_ip', '1121323')
    DB.db_delete('proxy_ip', '123.56.100.105')
    DB.db_commit()

    DB.db_close()
