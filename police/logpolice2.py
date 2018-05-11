# coding=utf-8

import sys
import os
from elasticsearch import Elasticsearch
import MySQLdb
import pycurl
import StringIO
import urllib
import certifi
import time
import redis
import json
import dbutil
import config

class LogPolice:
    def __init__(self, logtype, logindex, stime, intvalnum, threshold, taskid, db_unix_time, calcmethod=1, calcmodel=1, template=6, estimeout=10, matchcondit='', *logfield):

        #
        #阈值
        self.THRESHOLD = int(threshold)
        #计算模型
        self.CALCMODEL = calcmodel
        #计算方式 |1 >| 2 < |3 >= |4 <=
        self.CALCMETHOD = calcmethod
        #字段值
        self.LOGFIELD = logfield
        #logtype
        self.LOGTYPE = logtype

        round = int(float(abs(db_unix_time-stime)/intvalnum))
        self.STIME = stime + (round-1)*intvalnum
        self.ETIME = stime + round*intvalnum

        #报警模板
        self.TEMPLATE = str(template)


        #查询索引名称
        self.INDEXNAME = logindex

        #esurl
        self.ES_URL = 'http://0.0.0.0:9200'

        #estimeout
        self.ESTIMEOUT = int(estimeout)


        #过滤模板
        self.eqtemp = ',{"match": {"%(key)s": "%(value)s"}}'
        self.gttemp = ',{"range": {"%(key)s": {"%(sopt)s": "%(value)s"}}}'

        #过滤条件
        self.conditstr = ''
        if (matchcondit != '') & (matchcondit != None):
            # 过滤条件数据
            self.matchcondit = json.loads(matchcondit)
            for row in self.matchcondit:
                if row['sopt'] in ['gt', 'lt', 'gte', 'lte']:
                    self.conditstr += self.gttemp % {
                        'key': row['field'],
                        'sopt': row['sopt'],
                        'value': row['fieldnum'],
                    }
                elif row['sopt'] == 'eq':
                    self.conditstr += self.eqtemp % {
                        'key': row['field'],
                        'value': row['fieldnum'],
                    }

        #和聚合模板
        self.SUMAGGTEMP = '''
        {
        "query": {
            "bool": {
                "must": [
                    {"match": {"logtype": "%(logtype)s"}}
                    %(condit)s
                ],
                "filter": {
                    "range": {
                        "ctime": {
                            "gte": %(stime)d,
                            "lte": %(etime)d
                        }
                    }
                }
            }
        },
        "aggs": {
            "%(aggsname)s": {
                "sum": {
                    "field": "%(search_key)s"
                }
            }
        },
        "size": 0
        }
        '''

        #桶聚合模板
        self.BUCKETAGGTEMP = '''
        {
        "query": {
            "bool": {
                "must": [
                        {"match": {"logtype": "%(logtype)s"}}
                        %(condit)s
                ],
                "filter": {
                    "range": {
                        "ctime": {
                            "gte": %(stime)d,
                            "lte": %(etime)d
                        }
                    }
                }
            }
        },
        "aggs": {
            "%(aggname)s": {
                "terms": {
                    "field": "%(field)s.keyword",
                    "size": 10000000
                }
            }
        },
        "size": 0
        }
        '''


        #redis
        redis_host = '0.0.0.0'
        redis_post = 6379
        redis_auth = '????'
        self.rds = redis.StrictRedis(host=redis_host, port=redis_post, password=redis_auth, db=2)




    def curlpost(self, url, string=''):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPHEADER, ["Accept:"])
        c.setopt(pycurl.CUSTOMREQUEST, "POST")
        c.setopt(pycurl.POSTFIELDS, string)
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.perform()
        datas = b.getvalue()
        status = c.getinfo(c.HTTP_CODE)
        returndata = {"status": status, "data": datas}
        b.close()
        c.close()
        return returndata



    def waringpost(self,**params):
        keys = self.LOGTYPE+"_"+",".join(self.LOGFIELD)+"_waringtime"
        nowtime = int(time.time())

        if self.rds.get(keys) != None:
            waringtimeinterval = ",\n距离上次报警间隔："+str(nowtime-int(self.rds.get(keys)))+"秒 "
        else:
            waringtimeinterval = ",\n当前为首次报警"

        self.rds.set(keys, nowtime)

        queryperiod = ",\n查询时段："+time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(self.STIME))+"至"+time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(self.ETIME))

        police_content = "索引名称："+self.INDEXNAME
        police_content += ",\n日志类型："+self.LOGTYPE
        police_content += ",\n字段："+",".join(self.LOGFIELD)
        police_content += ",\n计算模型："+getattr(config, 'CALCMODEL_LANG')[self.CALCMODEL]
        police_content += ",\n"+params['calcname']+"阈值："+str(self.THRESHOLD)
        police_content += ",\n当前值：" + str(params['aggfield'])
        police_content += waringtimeinterval + queryperiod + " \n数据存在异常，请及时处理！\n"

        TEMPLATE_LIST = self.TEMPLATE.split("|")
        for ROW in TEMPLATE_LIST:
            request_url = 'https://xxxxxx.com/police/police_api'
            request_data = "police_id=" + str(ROW) + "&"
            request_data += "police_content=" + urllib.quote(police_content)
            print self.curlpost(request_url, request_data)



    #只做处理
    def datahandle(self):
        if self.CALCMODEL == 1:
            return self.sum_aggregations()
        elif self.CALCMODEL == 2:
            return self.bucket_aggregations()


    #和聚合
    def sum_aggregations(self):
        # 多字段
        aggfield = 0
        try:
            for row in self.LOGFIELD:
                ARGS = self.SUMAGGTEMP % {
                    "logtype": self.LOGTYPE,
                    "stime": self.STIME,
                    "etime": self.ETIME,
                    "aggsname": row,
                    "search_key": row,
                    "condit": self.conditstr
                }

                es = Elasticsearch(self.ES_URL)
                res = es.search(index=self.INDEXNAME, body=ARGS, request_timeout=self.ESTIMEOUT)

                # return res
                aggfield += int(res['aggregations'][row]['value'])
        except Exception, e:
            return "error:"+str(e)


        params = {"aggfield": aggfield, "calcname": getattr(config, 'CALCMETHOD_LANG')[self.CALCMETHOD]}
        if int(aggfield-self.THRESHOLD) >= 0:
            (self.CALCMETHOD == 1) and self.waringpost(**params)
        else:
            (self.CALCMETHOD == 2) and self.waringpost(**params)

        return "noerror,res:" + str(aggfield)


    #桶聚合
    def bucket_aggregations(self):

        try:
            logfield = self.LOGFIELD

            ARGS = self.BUCKETAGGTEMP % {
                "logtype": self.LOGTYPE,
                "stime": self.STIME,
                "etime": self.ETIME,
                "aggname": logfield[0],
                "field": logfield[0],
                "condit": self.conditstr
            }

            es = Elasticsearch(self.ES_URL)
            res = es.search(index=self.INDEXNAME, body=ARGS, request_timeout=self.ESTIMEOUT)
        except Exception, e:
            return "error:" + str(e)

        buckets = res['aggregations'][logfield[0]]['buckets']
        buckets_len = len(buckets)

        doc_count = 0
        if self.CALCMETHOD in [5, 6]:
            # 桶分类
            params = {"aggfield": buckets_len, "calcname": getattr(config, 'CALCMETHOD_LANG')[self.CALCMETHOD]}
            doc_count = buckets_len
            if buckets_len-self.THRESHOLD >= 0:
                (self.CALCMETHOD == 5) and self.waringpost(**params)
            else:
                (self.CALCMETHOD == 6) and self.waringpost(**params)

        elif self.CALCMETHOD in [3, 4]:
            # 桶容积
            for row in buckets:
                params = {"aggfield": row['doc_count'], "calcname": getattr(config, 'CALCMETHOD_LANG')[self.CALCMETHOD]}
                doc_count = row['doc_count']
                if row['doc_count'] - self.THRESHOLD >= 0:
                    (self.CALCMETHOD == 3) and self.waringpost(**params)
                    break
                else:
                    (self.CALCMETHOD == 4) and self.waringpost(**params)
                    break


        return "noerror,doc_count:" + str(doc_count)




if __name__ == "__main__":

    logfield = ('BaseGet', 'OtherGet')
    logtype = "AntiTgPick"
    logindex = "gamelog-20104-boluanaly"
    stime = 1521190800
    intvalnum = 3600
    threshold = 1
    taskid = 10
    db_unix_time = int(time.time())
    calcmethod = 1
    calcmodel = 1
    template = 5
    estimeout = 20
    matchcondit = None


    lp = LogPolice(logtype, logindex, stime, intvalnum, threshold, taskid, db_unix_time, calcmethod, calcmodel, template, estimeout, matchcondit, *logfield)
    res = lp.datahandle()
    print res

    ##  读表------->可执行线程------>执行------>报警
