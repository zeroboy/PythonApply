#coding=utf-8
'''
tep1.采集基本数据

除了距地铁距离，

其他都可以按Html标签名提取命名。

step2.获取小区经纬度

根据小区名获取地理坐标（经纬度）

step3.存储数据

可以选择存储为CSV或MongoDB，

采用其他数据库的小伙伴可以自便。

step4.发送邮件

将某区域或小区的增量房产信息发送邮件提醒自己

'''

import os
import sys
from bs4 import BeautifulSoup
import urllib2
import time
import re
import hashlib
import json
import csv



#url = "http://bj.58.com/ershoufang/?PGTID=0d100000-0000-105b-e7ef-5d41fdea2768&ClickID=1"
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
headers = {'User-Agent': user_agent}
outfile = "csv_" + str(int(time.time())) + ".csv"
# 表头
list = ["标题", "布局", "面积", "方向", "层数", "详细地址", "经纪人公司", "经纪人", "平米价格", "总价", "地理位置", "经度", "纬度", ]
out = open(outfile, 'ab+')
csv_writer = csv.writer(out)
csv_writer.writerow(list)
out.close()


def geocodeN(address, city):

    requesturl = "http://restapi.amap.com/v3/geocode/geo?"

    appkey = "76c4bec7989d4787fe17f761d1ae4af8"
    privatekey = "c1ef9c9ffbcd7c5682dc1ecb53a01c44"
    batch = False
    output = "JSON"

    args = ""
    args += "address="+str(address)
    args += "&batch="+str(batch)
    args += "&city="+str(city)
    args += "&key="+str(appkey)
    args += "&output="+str(output)
    args += privatekey
    sig = hashlib.md5(args).hexdigest()

    args2 = ""
    args2 += "address="+str(address)
    args2 += "&batch="+str(batch)
    args2 += "&city="+str(city)
    args2 += "&key="+str(appkey)
    args2 += "&output="+str(output)
    args2 += "&sig="+str(sig)

    requesturl += args2
    #print requesturl
    urllib2.Request(url=requesturl, headers=headers)
    rpn = urllib2.urlopen(url=requesturl, timeout=30)
    result = rpn.read()
    return result

def iplocation():
    requesturl = "http://restapi.amap.com/v3/ip?"
    appkey = "76c4bec7989d4787fe17f761d1ae4af8"
    privatekey = "c1ef9c9ffbcd7c5682dc1ecb53a01c44"
    output = "JSON"

    args = ""
    args += "key="+str(appkey)
    args += "&output="+str(output)
    args += privatekey
    sig = hashlib.md5(args).hexdigest()

    args2 = ""
    args2 += "key=" + str(appkey)
    args2 += "&output="+str(output)
    args2 += "&sig=" + str(sig)

    requesturl += args2
    urllib2.Request(url=requesturl, headers=headers)
    rpn = urllib2.urlopen(url=requesturl, timeout=30)
    result = json.loads(rpn.read())
    return (result['province']).encode("utf8")




#http://bj.58.com/ershoufang/pn2/?PGTID=0d300000-0000-076a-f62e-eebba2250537&ClickID=1


def grabcontents(url):
    urllib2.Request(url=url, headers=headers)
    reponese = urllib2.urlopen(url=url, timeout=30)
    res = reponese.read()

    soup2 = BeautifulSoup(res, "html.parser")
    listinfo = soup2.findAll('li')
    # print listinfo

    for x in range(len(listinfo)):
        try:
            if listinfo[x].has_attr('logr'):
                # print listinfo[x].has_attr('logr')
                # print listinfo[x]
                title = listinfo[x].find("h2").find("a").contents[0].encode("utf8")
                # print title
                baseinfo = listinfo[x].findAll("p", {"class": "baseinfo"})
                # print baseinfo

                spans1 = baseinfo[0].findAll("span")
                spans2 = baseinfo[1].findAll("span")
                spans2inner = spans2[0].findAll()
                layout = re.sub("\s", "", spans1[0].contents[0].encode("utf8"))
                area = spans1[1].contents[0].encode("utf8").strip("")
                direction = spans1[2].contents[0].encode("utf8").strip("")
                high = spans1[3].contents[0].encode("utf8").strip("")

                addrinfo = ""
                for s in range(len(spans2inner)):
                    # print spans2inner[x].contents[0].encode("utf8").strip("")
                    addrinfo += spans2inner[s].contents[0].encode("utf8") + "-"
                addrinfo = re.sub('\s', '', addrinfo.rstrip("-"))
                jjrinfo = listinfo[x].findAll("div", {"class": "jjrinfo"})
                jjraddr = re.sub('\s', '', re.sub('－', '', jjrinfo[0].contents[0].encode("utf8")))
                jjrnameouter = listinfo[x].findAll("span", {"class": "jjrname-outer"})[0].contents[0].encode("utf8")

                price = listinfo[x].findAll("div", {"class": "price"})
                pricesums = listinfo[x].findAll("div", {"class": "price"})[0].findAll("p", {"class": "sum"})[0].contents
                pricesum = ""
                for f in range(len(pricesums)):
                    pricesum += pricesums[f].encode("utf8")
                pricesum = re.sub("\n", "", re.sub("</b>", "", re.sub("<b>", "", pricesum)))

                priceunit = \
                listinfo[x].findAll("div", {"class": "price"})[0].findAll("p", {"class": "unit"})[0].contents[
                    0].encode("utf8")

                city = iplocation() + addrinfo.split("-")[1]
                address = iplocation() + addrinfo.split("-")[1] + addrinfo.split("-")[0]
                locationinfo = json.loads(geocodeN(address, city))

                try:
                    formatted_address = locationinfo['geocodes'][0]['formatted_address'].encode("utf8")
                    longitude = locationinfo['geocodes'][0]['location'].split(",")[0]
                    latitude = locationinfo['geocodes'][0]['location'].split(",")[1]
                except Exception, e:
                    formatted_address = ""
                    longitude = 0
                    latitude = 0

                print title
                print layout
                print area
                print direction
                print high
                print addrinfo
                print jjraddr
                print jjrnameouter
                print priceunit
                print pricesum
                print formatted_address
                print longitude
                print latitude

                print "***********************************************************"

                list = [title, layout, area, direction, high, addrinfo, jjraddr, jjrnameouter, priceunit, pricesum,
                        formatted_address, longitude, latitude, ]
                out = open(outfile, 'ab+')
                csv_writer = csv.writer(out)
                csv_writer.writerow(list)
                out.close()
        except Exception, e:
            print e
            continue






def main():
    for i in range(1, 200):
        baseurl = "http://bj.58.com/ershoufang/"
        if i == 1:
            pn = ""
        else:
            pn = "pn" + str(i) + "/"
        baseurl += pn
        baseurl += "?PGTID=0d100000-0000-105b-e7ef-5d41fdea2768"
        baseurl += "&ClickID=1"

        print baseurl
        grabcontents(baseurl)
        time.sleep(1)


if __name__ == '__main__':
    main()









































