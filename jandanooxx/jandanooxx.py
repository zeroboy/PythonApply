# coding:utf-8
####################################################
#//E:/wamp/www/application/pycharm/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe  E:/wamp/www/application/pycharm/project1/Rendering.js 354 

import sys
import re
import urllib
import urllib2
from bs4 import BeautifulSoup
from PIL import Image
import cStringIO
import os
import random
import sys
import time


pages = 376



command = '''
E:/wamp/www/application/pycharm/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe --disk-cache=yes  --ignore-ssl-errors=true --config=E:/wamp/www/application/pycharm/project1/config.json E:/wamp/www/application/pycharm/project1/Rendering.js  %(page)d
'''
command = command % {"page": pages}

user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64)'
headers = {'User-Agent': user_agent}

try:
    #time1 = time.time()
    result = os.popen(command)
    res = result.read()

    #time2 = time.time()
    #print time2-time1

    soup = BeautifulSoup(str(res), "html.parser")
    imgs = soup.findAll('img')


    for i in range(len(imgs)):
        #print imgs[i].get("src")
        if imgs[i].get("org_src") != None:
            #pass
            picurl = imgs[i].get("org_src")
            picurl_arr = picurl.split("/")
            imgname = picurl_arr[len(picurl_arr)-1]
            print imgname
            urllib.urlretrieve(picurl, './jandan/'+str(imgname))
        else:
            srcs = imgs[i].get("src")
            srcs_arr = srcs.split("/")
            imgname2 = srcs_arr[len(srcs_arr) - 1]
            print imgname2
            imgcontent = urllib2.Request(srcs, headers=headers)
            imgcontents = cStringIO.StringIO(urllib2.urlopen(imgcontent, timeout=30).read())
            im = Image.open(imgcontents)
            im.save('./jandan/' + "/" + imgname2, 'PNG')

    sys.exit()

except Exception, e:
    print e


