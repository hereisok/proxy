# /usr/bin/python
# encoding:utf-8


# 从网页中获取代理IP

import urllib2
# import db_operation
import shelve
import re
import chardet
import socket
# import sys

# reload(sys)
# sys.setdefaultencoding('utf-8')


# 从网页中获取代理IP
# @param root_url 根网页
# return [[ip, port, mode, other], [ip, port, mode, other]]
def get_from_url(root_url):
    return_list = []
    shelve_file = shelve.open('shelve_file','c')
    if 'url_list' not in shelve_file.keys():
        shelve_file['url_list'] = []

    shelve_url_list= shelve_file['url_list']
    url_list = get_url_list(root_url)
    for url in url_list:
        if url in shelve_url_list:
            continue
        html = get_html(url)
        if not html:
            continue
        pos = html.find('<div class="cont_ad"><script type="text/javascript">BAIDU_CLB_fillSlot("625610")')
        html = html[pos:]
        pos = html.find('<p>')
        html = html[pos + 3:]
        pos = html.find('</p>')
        html = html[:pos - 1]

        for line in html.split('\n'):
            if line.find('#') == -1:
                continue
            #42.159.244.217:1080@SOCKS5#北京市 世纪互联微软云Windows Azure数据中心<br />
            line = line.replace('<br />', '')
            ip_info = line.split('#')[0]
            other = line.split('#')[1]
            ip_port = ip_info.split('@')[0]
            mode_info = ip_info.split('@')[1]
            mode = 4 if mode_info == 'SOCKS4' else 5
            # print [ip_port.split(':')[0], ip_port.split(':')[1], mode, other]

            return_list.append([ip_port.split(':')[0], ip_port.split(':')[1], mode, other])

        shelve_url_list.append(url)

    shelve_file['url_list'] = shelve_url_list
    shelve_file.close()
    return return_list

# 获取根url中提取url列表
# @param root_url 根网页
# @return 具有代理IP信息的url列表
def get_url_list(root_url):
    html = get_html(root_url)
    url_list = []
    pattern = re.compile(r'<li><a href=".+?" target="_blank"><font color=#FF7300>【Socks代理】')
    for match in pattern.findall(html):
        url_list.append(match.split('\"')[1])
    return url_list

# 获取网页源代码
def get_html(url):
    html = ''
    for i in range(1000):
        if html and chardet.detect(html)['encoding'] == 'utf-8' and html.find('请开启JavaScript并刷新该页.') == -1:
            break
        try:
            # req_header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
            # 'Accept':'text/html;q=0.9,*/*;q=0.8',
            # 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            # 'Connection':'close',}
            # req_timeout = 10
            # req = urllib2.Request(url, None, req_header)
            # resp = urllib2.urlopen(req, timeout = 10)
            resp = urllib2.urlopen(url, timeout = 10)
            html = resp.read()
            resp.close()
        except socket.timeout, e:
            pass
        except Exception, e:
            pass
            

    # print html[0:100]
    # print chardet.detect(html)
    return str(html)

if __name__ == '__main__':
    print get_from_url('http://www.youdaili.net/Daili/Socks/list_1.html')



