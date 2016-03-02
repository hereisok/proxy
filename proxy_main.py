# /usr/bin/python
# encoding:utf8

# socket代理IP表建立
# @author wangkai
# @version 1.0
# 2015.12.13

import db_operation
import verification
import get_proxy_ip
import threading
import datetime
import time

DB = db_operation.DataBase()

# 数据更新线程
class updateThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        
        global DB
        while True:
            time.sleep(24*3600) # 每天执行一次
            proxy_ip_info_list = get_from_url('http://www.youdaili.net/Daili/Socks/list_1.html') # 获取最新的一页信息
            for proxy_ip_info in proxy_ip_info_list:
                if DB.db_select(nature = 'proxy_ip', ip = proxy_ip_info[0], port = proxy_ip_info[1]):
                    continue
                DB.db_insert(
                    nature = 'proxy_ip',
                    ip = proxy_ip_info[0],
                    port = proxy_ip_info[1],
                    mode = proxy_ip_info[2],
                    other = proxy_ip_info[3],
                    insert_time = get_now_time(),
                    verification_time = '0000-00-00 00:00:00'
                    )
                DB.db_commit() # 没上传一条commit一次

            print get_now_time() + ' 更新数据'

# 持续的数据验证, 主线程
def main_verification():
    global DB
    while True:
        query_time = get_now_time()
        # query_time = '2015-12-01 00:00:00'
        proxy_ip_info_list = get_from_db(query_time)
        while len(proxy_ip_info_list) != 0:
            for proxy_ip_info in proxy_ip_info_list:
                speed_cn, speed_com_A, speed_com_B, speed_cross = verification.verification(ip = proxy_ip_info[0], port = proxy_ip_info[1], mode = proxy_ip_info[2])
                if speed_cn + speed_com_A + speed_com_B + speed_cross == -4: # 验证失败
                    DB.db_delete(nature = 'proxy_ip', ip = proxy_ip_info[0], port = proxy_ip_info[1])

                else:
                    DB.db_update(
                        nature = 'proxy_ip',
                        ip = proxy_ip_info[0],
                        port = proxy_ip_info[1],
                        speed_cn = speed_cn,
                        speed_com_A = speed_com_A,
                        speed_com_B = speed_com_B,
                        speed_cross = speed_cross,
                        verification_time = get_now_time()
                    )

            DB.db_commit()
            proxy_ip_info_list = get_from_db(query_time)

        print get_now_time() + ' 验证数据'
        time.sleep(5*3600) # 每5个小时进行一次验证

# 主函数
def main():
    global DB
    DB.get_connect()
    # 初次获取，获取三页内容
    proxy_ip_info_list = get_from_url('http://www.youdaili.net/Daili/Socks/list_1.html')
    proxy_ip_info_list += get_from_url('http://www.youdaili.net/Daili/Socks/list_2.html')
    proxy_ip_info_list += get_from_url('http://www.youdaili.net/Daili/Socks/list_3.html')

    for proxy_ip_info in proxy_ip_info_list:
        if DB.db_select(nature = 'proxy_ip', ip = proxy_ip_info[0], port = proxy_ip_info[1]):
            continue
        DB.db_insert(
            nature = 'proxy_ip',
            ip = proxy_ip_info[0],
            port = proxy_ip_info[1],
            mode = proxy_ip_info[2],
            other = proxy_ip_info[3], 
            insert_time = get_now_time(),
            verification_time = '0000-00-00 00:00:00'
            )
        DB.db_commit() # 每上传一条commit一次

    print get_now_time() + ' 基础数据建立完成'
    update_thread = updateThread()
    update_thread.start()
    main_verification()

# 从网页获取代理IP
def get_from_url(url):
    return get_proxy_ip.get_from_url(url)

# 从数据库获取代理IP
def get_from_db(query_time):
    global DB
    # print 'query_time: ', query_time
    results = DB.db_select(nature = 'all_proxy_table', query_time = query_time)
    proxy_ip_list = []
    if results:
        for result in results:
            proxy_ip_list.append(result)

    return proxy_ip_list

# 获取统一化的时间
def get_now_time():
    return str(datetime.datetime.now()).split(".")[0]


if __name__ == '__main__':

    main()
    # DB.get_connect()
    # main_verification()
    
    # print get_from_db(get_now_time()
    # DB.db_close()

    
