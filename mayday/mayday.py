#coding:utf-8
import threading
import Queue
import os
import sys
import urllib2
import socket
from bs4 import BeautifulSoup
import re
import time

url_head = "http://73nj.com"
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
headers = {'User-Agent': user_agent}
base_path = "./threadsource/"
timeouts = 60

class threadDownload(threading.Thread):
    def __init__(self, que, no):
        threading.Thread.__init__(self)
        self.que = que
        self.no = no

    def run(self):
        while True:
            if not self.que.empty():
                saveImg(self.que.get(), 'os' + str(self.no) + '.jpg')
            else:
                break

#页面列表----->[图片路径数->开启线程数（控制线程 线程数为1时即只剩下主线程->进入下一次列表循环）]----->结束
def saveToFile(FileName, srcList):
    a = 0
    FileName = base_path + FileName.strip()
    res = os.mkdir(FileName)
    if res == False:
        return False

    os.chdir(FileName)
    que = Queue.Queue()
    for sl in srcList:
        que.put(sl)
    for a in range(0, srcList.__len__()):
        threadD = threadDownload(que, a)
        threadD.start()

    while threading.active_count() != 0:
        if threading.active_count() == 1:
            print FileName + "  is Done"
            os.chdir("../../")
            time.sleep(2)
            return True
        time.sleep(2)


def saveImg(imgUrl, fileName):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
    headers = {'User-Agent': user_agent}
    try:
        req = urllib2.Request(imgUrl, headers=headers)
        res = urllib2.urlopen(req, timeout=timeouts)
        data = res.read()
    except socket.timeout as e:
        print "saveImgTimeOut"
        return False
    f = open(fileName, 'wb')
    f.write(data)
    f.close()


#-------------------------------------------------------------


proxy_cont=open("proxy_avi.txt").read()
##proxy_avi是经过测试可用的代理服务器
proxy_list = proxy_cont.split('\n')

proxy = {"http": "http://"+str(proxy_list[0])}
print proxy

try:
    start = time.time()
    #proxy_support = urllib2.ProxyHandler(proxy) 
    #opener = urllib2.build_opener(proxy_support)
    #urllib2.install_opener(opener)
    url_list = "http://73nj.com/html/part/22_15.html"
    request2 = urllib2.Request(url_list, headers=headers)
    response2 = urllib2.urlopen(request2, timeout=timeouts)
    spend = time.time() - start
    #print spend
except Exception, e:
    print e
    sys.exit()


#sys.exit()


starttime = time.time()

for i in range(2, 50):

    url_list = "http://73nj.com/html/part/22_"+str(i)+".html"
    try:
        content2 = response2.read()
        soup2 = BeautifulSoup(content2, "html.parser")

        tables = soup2.findAll('table', {"class": "listt"})

        for i in range(len(tables)):
            articletag = tables[i].findAll("a", href=re.compile("/html/article"))

            if articletag:
                articlehref = articletag[0].get("href")
                articletitle = articletag[0].get("title")
                href = url_head + articlehref
                url = href

                try:
                    request = urllib2.Request(url, headers=headers)
                    response = urllib2.urlopen(request, timeout=timeouts)
                    content = response.read()
                    soup = BeautifulSoup(content, "html.parser")
                    imgs = soup.findAll('img')
                    srcList = []
                    url_arr = url.split("/")
                    FileName = url_arr[len(url_arr) - 1].split(".")[0]
                    for s in range(len(imgs)):
                        srcList.append(imgs[s].get('src'))

                    print FileName
                    print srcList

                    ###
                    saveToFile(FileName, srcList)

                except Exception, e:
                    print e
    except Exception, e:
        print e

    time.sleep(1)


endtime = time.time()
spendtime = endtime - starttime

print spendtime

'''
            for i in range(len(imgs)):
            # print imgs[i]
            srcs = imgs[i].get('src')
            print srcs
            if srcs:
                # print srcs
                imgnames = srcs.split("/")
                try:
                    imgname = imgnames[len(imgnames) - 1]
                except Exception, e:
                    imgname = str(int(time.time())) + ".jpg"

                #print dirs + "/" + imgname.encode('gbk')
                #sys.exit()

                if str(imgname.split(".")[1]) != "gif":
                    imgcontent = urllib2.Request(srcs, headers=headers)
                    imgcontents = cStringIO.StringIO(urllib2.urlopen(imgcontent, timeout=10).read())
                    im = Image.open(imgcontents)
                    im.save(dirs + "/" + imgname.encode('gbk'), 'PNG')

            else:
                pass
'''


