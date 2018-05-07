import os
import sys
from bs4 import BeautifulSoup

import json
import urllib2
import MySQLdb
import dbutil
import re
import time


class xiciproxy:
    def __init__(self):

        LOGDBPARAMS = {
            'creator': MySQLdb,
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'passwd': '',
            'db': 'proxypool',
            'maxcached': 1,
            'charset': 'utf8',
        }
        self.dbobj = dbutil.DBObject(LOGDBPARAMS)

        #user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
        #user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
            'Hosts': 'hm.baidu.com',
            'Referer': 'http://www.xicidaili.com/nn',
            'Connection': 'keep-alive'
        }
        self.requesturl = "http://www.xicidaili.com/nn/1" 

    def _get(self):
        try:
            # urllib2.Request(url=self.requesturl, headers=self.headers)
            # rpn = urllib2.urlopen(url=self.requesturl, timeout=30)
            req = urllib2.Request(url=self.requesturl, headers=self.headers)
            res = urllib2.urlopen(req).read()
            soup2 = BeautifulSoup(res, "html.parser")
            listinfo = soup2.findAll('table', {"id": "ip_list"})[0]
            tr = listinfo.findAll("tr")
            for row in range(1, len(tr)):
                success_num = 0
                print '----------------------------------'
                ip = tr[row].findAll("td")[1].contents[0]
                port = tr[row].findAll("td")[2].contents[0]
                addr = tr[row].findAll("td")[3].contents[1].contents[0]
                isanonymous = tr[row].findAll("td")[4].contents[0]
                types = tr[row].findAll("td")[5].contents[0].lower()
                proxy = {types: types + "://" + str(ip)}

                print proxy
                stime = time.time()
                try:
                    for i in range(0, 10):
                        proxy_support = urllib2.ProxyHandler(proxy)
                        opener = urllib2.build_opener(proxy_support)
                        urllib2.install_opener(opener)
                        url_list = "http://73nj.com/html/part/22_15.html"
                        self.headers['Referer'] = url_list
                        request2 = urllib2.Request(url_list, headers=self.headers)
                        response2 = urllib2.urlopen(request2, timeout=30)
                        success_num = success_num + 1
                        print response2

                except Exception, e:
                    print e

                print int(time.time() - stime)
                print success_num
                print 10 - success_num
                try:
                    sql = "insert into proxypool values(null,'" + ip + "'," + str(
                        port) + ",'" + addr + "','" + isanonymous + "','" + types + "'," + str(success_num) + "," + str(
                        10 - success_num) + "," + str(int(time.time() - stime)) + ","+str(int(time.time()))+")"
                    res = self.dbobj.query(sql)
                except Exception, e:
                    sql = "update proxypool set success_req_num=" + str(success_num) + ", faild_req_num=" + str(
                        10 - success_num) + ", consume_time=" + str(
                        int(time.time() - stime)) + ", update_time=" + str(int(time.time())) + " where ip='" + ip + "';"
                    res = self.dbobj.query(sql)

                print sql
                print res
        except Exception, e:
            print e




if __name__ == '__main__':
    xc = xiciproxy()
    res = xc._get()
    #print res


        #select * from proxypool where success_req_num >0 order by success_req_num desc,consume_time asc;