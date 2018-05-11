# coding=utf8
import sys
import os
import time
import json
import MySQLdb
import dbutil
import threading

import logpolice2


class myThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name, counter, **param):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.param = param

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        print "Starting " + self.name
        run_task(self.name, self.counter, 5, **self.param)
        print "Exiting " + self.name


def run_task(threadName, delay, counter, **param):
    #线程缓冲
    time.sleep(param['sleeptime'])
    print param

    #参
    logtype = param['logtype']
    stime = param['start_time']
    intvalnum = param['intervalnum']
    threshold = param['threshold']
    taskid = param['id']
    db_unix_time = param['db_unix_time']
    calcmethod = param['calcmethod']
    logfield = param['field']
    template = param['template']
    dbobj = param['dbobj']
    logindex = param['logindex']
    calcmodel = param['calcmodel']
    matchcondit = param['matchcondit']

    #更新运行时间
    sql4 = "update bolu_logfieldmonitor "
    sql4 = sql4 + "set worktime=" + str(db_unix_time)
    sql4 = sql4 + " where id=" + str(taskid) + ";"
    dbobj.query(sql4)

    ##运行监听
    lp = logpolice2.LogPolice(logtype, logindex, stime, intvalnum, threshold, taskid, db_unix_time, calcmethod, calcmodel, template, estimeout, matchcondit, *logfield)
    res = lp.datahandle()

    #监听结果
    remark = json.dumps({
        'id': taskid,
        'db_unix_time': db_unix_time,
        'res': res.replace("'", "\"")
    })

    # 更新运行时间 更新运行结果
    sql3 = "update bolu_logfieldmonitor "
    sql3 = sql3 + "set remark=concat(remark,'|" + str(remark)+"')"
    sql3 = sql3 + " where id=" + str(taskid) + ";"
    print sql3
    dbobj.query(sql3)

    print res


if __name__ == "__main__":
    #不分主从库 只区分账号 不影响速度
    LOGDBPARAMS = {
        'creator': MySQLdb,
        'host': '0.0.0.0',
        'port': 3306,
        'user': '????',
        'passwd': '????',
        'db': '????',
        'maxcached': 1,
        'charset': 'utf8',
    }
    dbobj = dbutil.DBObject(LOGDBPARAMS)

    # 数据库时间
    sql = "select unix_timestamp();"
    res = dbobj.query(sql)
    db_unix_time = res[0][0]

    #表数据
    sql2 = "select * from ???? where state =1 ;"
    res2 = dbobj.query(sql2)

    for row in res2:
        print '--------ID-'+str(row[0])+'--------'
        id = row[0]
        logfield = tuple(row[1].encode('utf8').split("|"))
        logtype = row[2]
        start_time = row[3]
        intervalnum = row[4]
        intervalunit = row[5]
        threshold = row[6]
        calcmethod = row[7]
        template = row[8]
        state = row[9]
        sleeptime = row[10]
        worktime = row[11]
        estimeout = row[12]
        createtime = row[13]
        remark = row[14]
        calcmodel = row[15]
        logindex = row[16]
        matchcondit = row[17]

        if db_unix_time >= start_time and (db_unix_time-intervalnum) > (worktime-10):
            param = {
                "id": id,
                "field": logfield,
                "logtype": logtype.encode('utf8'),
                "start_time": start_time,
                "intervalnum": intervalnum,
                "threshold": threshold,
                "calcmethod": calcmethod,
                "template": template,
                "worktime": worktime,
                "estimeout": estimeout,
                "db_unix_time": db_unix_time,
                "sleeptime": sleeptime,
                "calcmodel": calcmodel,
                "logindex": logindex.encode('utf8'),
                "matchcondit": matchcondit,
                "dbobj": dbobj
            }

            # 创建新线程
            thread1 = myThread(id, "Thread-"+str(id), id, **param)

            # 开启线程
            thread1.start()
        else:
            print '线程-id'+str(id)+'未达到启动标准'

    #sys.exit()



    #thread2 = myThread(2, "Thread-2", 2)
    #thread3 = myThread(3, "Thread-3", 3)


    #thread2.start()
    #thread3.start()




