# coding=utf8
import sys
import os
import time
import json
import MySQLdb
import dbutil
import threading
import ESDataExport
import base64
import datetime
import math
import json
import hashlib


class myThread(threading.Thread):
    def __init__(self, threadID, name, counter, **param):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.param = param
        self.lock = threading.Lock()

    def run(self):
        if self.lock.acquire(True):
            print "Starting " + self.name
            body = self.param['esexport'].getData(self.counter)
            head = self.param['head']
            filename = self.param['filename']
            # print body
            self.param['esexport'].writeFiles(head, body, filename, self.counter)
            print "####################################################"
            print "Exiting " + self.name
            self.lock.release()




if __name__ == '__main__':
    starttime = int(time.time())
    LOGDBPARAMS = {
        'creator': MySQLdb,
        'host': '0.0.0.0',
        'port': 3306,
        'user': 'xxxxx',
        'passwd': 'xxxxx',
        'db': 'xxxxx',
        'maxcached': 1,
        'charset': 'utf8',
    }
    dbobj = dbutil.DBObject(LOGDBPARAMS)

    postdata = sys.argv[1]
    #postdata = 'eyJnc3NpZCI6IjIwMTA0IiwibG9ndHlwZSI6ImJvbHVhbmFseSIsImxvZ2RhdGVfc3RhcnQiOiIyMDE4LTA2LTAxIDAwOjAwIiwibG9nZGF0ZV9lbmQiOiIyMDE4LTA2LTAyIDAwOjAwIiwibWFqb3Jsb2d0eXBlIjoiTWFpbFBpY2siLCJfc2VhcmNoIjpmYWxzZSwibmQiOjE1MjgzNjI3NTMwMTIsInJvd3MiOjUwLCJwYWdlIjoxLCJzaWR4IjoiY3RpbWUiLCJzb3JkIjoiZGVzYyIsInJlY29yZHMiOjk4Nn0='
    postdatas = base64.b64decode(postdata)
    postdatas_md5 = hashlib.md5(postdatas).hexdigest()[8:-8]
    param = json.loads(postdatas)
     
    try:
        filters = param['filters']
    except Exception, e:
        filters = ''

    sidx = param['sidx']
    sord = param['sord']

    logindex = 'gamelog-%(gssid)s-%(logtype)s' % {'gssid': param['gssid'], 'logtype': param['logtype']}
    logtype = param['majorlogtype']
    stime = int(time.mktime(time.strptime(param['logdate_start'], '%Y-%m-%d %H:%M')))
    etime = int(time.mktime(time.strptime(param['logdate_end'], '%Y-%m-%d %H:%M')))

    esexport = ESDataExport.EsDataExportForCsv(logindex, logtype, stime, etime, sidx, sord, filters)
    dataDetail = esexport.getHead()
    head = dataDetail[0]
    total = dataDetail[1]
    if total % 1000 > 0:
        Remainder = 1
    threadnum = Remainder + int(total/1000) + 1

    #f = open('data.csv', 'w+')
    #f.write(','.join(head) + "\n")
    nowTime_f = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    filename = './files/data_' + nowTime_f + '_' + postdatas_md5 + '.csv'

    sql = "insert into es_data_export VALUES (NULL, '" + str(postdata) + "','" + filename + "',0,0,"+str(int(threadnum-1))+",1000 )"
    lastid = dbobj.mysql_lastid(sql)

    for i in range(1, threadnum):
        params = {
            'head': head,
            'esexport': esexport,
            'filename': filename
        }

        thread1 = myThread(i, "Thread-" + str(i), i, **params)
        thread1.start()

    while True:
        if threading.activeCount() == 1:
            print threading.activeCount()
            endtime = int(time.time())
            runtime = str(int(endtime - starttime))
            sql2 = "update es_data_export set runtime="+runtime+",filestate=1 where id="+str(lastid)
            dbobj.query(sql2)
            break
        else:
            time.sleep(1)




    #print total
    #print threadnum

    #nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')


