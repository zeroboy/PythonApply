# -*- coding:utf-8 -*-
import sys
import re
from bs4 import BeautifulSoup
import urllib2

url = "https://tieba.baidu.com/f?kw=dnf&fr=wwwt"
user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64)'
headers = {'User-Agent': user_agent}
request = urllib2.Request(url, headers=headers)
response = urllib2.urlopen(request)
content = response.read().decode('utf-8')
soup = BeautifulSoup(content,"html.parser")
#threadlist_bright j_threadlist_bright
li = soup.findAll('li', {"class": " j_thread_list clearfix"})

print li[0]
#print len(li)

for idx in li:
    #
    rep_num = idx.findAll(name='span', attrs={"class": "threadlist_rep_num center_text"})
    pattern = "<span.*?>(.*?)</span>"
    rep_nums = re.findall(pattern, str(rep_num[0]))
    #
    title = idx.findAll(name='a', attrs={"class": "j_th_tit"})
    pattern2 = "<a.*?>(.*?)</a>"
    titles = re.findall(pattern2, str(title[0]))
    #
    author = idx.findAll(name='span', attrs={"class": "tb_icon_author"})
    authors = author[0].get('title')
    #
    onlyline = idx.findAll(name='div', attrs={"class": "threadlist_abs threadlist_abs_onlyline "})
    onlyline_handle = re.sub("[\n\s]*", "", str(onlyline[0]))
    pattern3 = "<div.*>(.*)</div>"
    onlylines = re.findall(pattern3, onlyline_handle)
    #
    replyer = idx.findAll(name='span', attrs={"class": "tb_icon_author_rely j_replyer"})
    replyers = replyer[0].get('title')
    #
    reply_data = idx.findAll(name='span', attrs={"class": "threadlist_reply_date pull_right j_reply_data"})
    reply_data_name = reply_data[0].get('title')
    reply_data_handle = re.sub("[\n\s]*", "", str(reply_data[0]))
    pattern4 = "<span.*>(.*?)</span>"
    reply_datas = re.findall(pattern4, reply_data_handle)


    ### a--->b
    print '--####################################--'
    print titles[0]
    print onlylines[0]
    print authors
    print '回复：' + str(rep_nums[0])
    print replyers
    print reply_data_name,reply_datas[0]
    print '--####################################--'

