#-*-coding:utf-8-*-

from elasticsearch import Elasticsearch
import time
import json
import base64
#
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import pandas as pd
import os
import datetime


class EsDataExportForCsv:
    def __init__(self, logindex, logtype, stime, etime, sidx, sord, filter=''):
        self.logindex = logindex
        self.logtype = logtype
        self.stime = stime
        self.etime = etime
        self.sidx = sidx
        self.sord = sord

        self.es_url = ["0.0.0.1","0.0.0.2","0.0.0.3"]
        self.es = Elasticsearch(self.es_url)

        self.orconditstr = ""
        self.andconditstr1 = ""
        self.andconditstr2 = ""

        if filter != '':
            self.filter = json.loads(filter)
            self.groupOp = self.filter['groupOp']
            self.rules = self.filter['rules']

            filters1 = []  # 和条件
            filters2 = {"must_not": []}
            filters = {"should": []}
            for row in self.rules:
                if self.groupOp == 'AND':

                    if row['op'] == 'eq':
                        filters1.append(
                            {
                                "match": {
                                    row['field']: row['data']
                                }
                            }
                        )
                    elif row['op'] == 'ne':
                        filters2["must_not"].append(
                            {
                                "match": {
                                    row['field']: row['data']
                                }
                            }
                        )
                    elif row['op'] == 'gt':
                        filters1.append(
                            {
                                "range": {
                                    row['field']: {
                                        "gt": row['data']
                                    }
                                }
                            }
                        )
                    elif row['op'] == 'lt':
                        filters1.append(
                            {
                                "range": {
                                    row['field']: {
                                        "lt": row['data']
                                    }
                                }
                            }
                        )
                    elif row['op'] == 'bw':
                        filters1.append(
                            {
                                "range": {
                                    row['field']: {
                                        "gte": row['data']
                                    }
                                }
                            }
                        )

                    elif row['op'] == 'bn':
                        filters1.append(
                            {
                                "range": {
                                    row['field']: {
                                        "lt": row['data']
                                    }
                                }
                            }
                        )
                    elif row['op'] == 'ew':
                        filters1.append(
                            {
                                "range": {
                                    row['field']: {
                                        "lte": row['data']
                                    }
                                }
                            }
                        )
                    elif row['op'] == 'nn':
                        filters1.append(
                            {
                                "exists": {
                                    row['field']: row['data']
                                }
                            }
                        )

                    elif row['op'] == 'nu':
                        filters2["must_not"].append(
                            {
                                "exists": {
                                    row['field']: row['data']
                                }
                            }
                        )

                    elif row['op'] == 'en':
                        filters1.append(
                            {
                                "range": {
                                    row['field']: {
                                        "gt": row['data']
                                    }
                                }
                            }
                        )
                    elif row['op'] == 'cn':
                        pass
                        filters1.append(
                            {
                                "query_string": {
                                    "default_field": row['field'],
                                    "query": row['data']
                                }
                            }
                        )
                    elif row['op'] == 'nc':
                        filters2["must_not"].append(
                            {
                                "query_string": {
                                    "gte": row['data']
                                }
                            }
                        )
                    elif row['op'] == 'in':
                        filters1.append(
                            {
                                "query_string": {
                                    "default_field": row['field'],
                                    "query": row['data']
                                }
                            }
                        )
                    elif row['op'] == 'ni':
                        filters2["must_not"].append(
                            {
                                "query_string": {
                                    "gte": row['data']
                                }
                            }
                        )

                    self.andconditstr1 = "," + json.dumps(filters1).strip("[").strip("]")
                    self.andconditstr2 = json.dumps(filters2).strip("{").strip("}") + ","

                    # print self.andconditstr1
                    # print self.andconditstr2
                    # sys.exit()



                elif self.groupOp == 'OR':

                    if row['op'] == 'eq':

                        filters["should"].append(
                            {
                                "bool": {
                                    "must": [{
                                        "match": {
                                            row['field']: row['data']
                                        }
                                    }]
                                }
                            }
                        )

                    elif row['op'] == 'ne':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must_not": [{
                                        "match": {
                                            row['field']: row['data']
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'bw':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must": [{
                                        "range": {
                                            row['field']: {
                                                "gte": row['data']
                                            }
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'bn':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must": [{
                                        "range": {
                                            row['field']: {
                                                "lt": row['data']
                                            }
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'ew':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must": [{
                                        "range": {
                                            row['field']: {
                                                "lte": row['data']
                                            }
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'nn':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must": [{
                                        "exists": {
                                            row['field']: row['data']
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'nu':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must_not": [{
                                        "exists": {
                                            row['field']: row['data']
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'en':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must": [{
                                        "range": {
                                            row['field']: {
                                                "gt": row['data']
                                            }
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'cn':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must": [{
                                        "query_string": {
                                            "default_field": row['field'],
                                            "query": row['data']
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'nc':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must_not": [{
                                        "query_string": {
                                            "gte": row['data']
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'in':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must": [{
                                        "query_string": {
                                            "default_field": row['field'],
                                            "query": row['data']
                                        }
                                    }]
                                }
                            }
                        )
                    elif row['op'] == 'ni':
                        filters["should"].append(
                            {
                                "bool": {
                                    "must_not": [{
                                        "query_string": {
                                            "gte": row['data']
                                        }
                                    }]
                                }
                            }
                        )

                    filters['minimum_should_match'] = 1

                    self.orconditstr = json.dumps(filters).strip("{").strip("}") + ","




        ####
        self.QTPL = '''
                {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "logtype": "%(logtype)s"
                                    }
                                }
                                %(andcondit1)s
                            ],
                            %(orcondit)s
                            %(andcondit2)s
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
                    "sort":[{"%(sidx)s":{"order":"%(sord)s","unmapped_type":"boolean"}}],
                    "from": %(from)d,
                    "size": %(size)d
                }
                '''





    def getHead(self):

        self.QTPL_F = self.QTPL % {
            "logtype": self.logtype,
            "stime": self.stime,
            "etime": self.etime,
            "sidx": self.sidx,
            "sord": self.sord,
            "orcondit": self.orconditstr,
            "andcondit1": self.andconditstr1,
            "andcondit2": self.andconditstr2,
            "from": 0,
            "size": 1
        }

        res = self.es.search(index=self.logindex, body=self.QTPL_F, request_timeout=1800)
        source = res['hits']['hits'][0]['_source']
        return [source.keys(), res['hits']['total']]

    def getData(self, threadnum):

        self.QTPL_F = self.QTPL % {
            "logtype": self.logtype,
            "stime": self.stime,
            "etime": self.etime,
            "sidx": self.sidx,
            "sord": self.sord,
            "orcondit": self.orconditstr,
            "andcondit1": self.andconditstr1,
            "andcondit2": self.andconditstr2,
            "from": (threadnum-1)*1000,
            "size": 1000
        }

        res = self.es.search(index=self.logindex, body=self.QTPL_F, request_timeout=1800)
        source = []

        for row in res['hits']['hits']:
            source.append(row['_source'])

        return source

    def writeFiles(self, head, body, filename, threadnum):
        data = pd.DataFrame(body)

        try:
            if os.path.exists(filename):
                data.to_csv(filename, header=False, index=False, mode='a+', encoding='utf-8', columns=head)
            else:
                data.to_csv(filename, header=head, index=False, mode='a+', encoding='utf-8', columns=head)

        except Exception, e:
            print e


def main():
  pass

if __name__ == '__main__':
    main()
    '''
    filters = {"should": []}
    filters["should"].append(
        {
            "bool": {
                "must": [{
                    "range": {
                        "CurBean": {
                            "gte": "0"
                        }
                    }
                }]
            }
        }
    )
    filters["should"].append(
        {
            'bool': {
                'must': [{
                    'match': {
                        'Add': '100'
                    }
                }]
            }
        }
    )


    filters['minimum_should_match'] = 1
    print filters
    print type(filters)
    '''
