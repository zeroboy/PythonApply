# coding=utf-8
import os
import sys
import re
import time
import json
import pycurl
import StringIO
import certifi


class turingRobot:

    def __init__(self, infos=""):
        self.requesturl = "http://www.tuling123.com/openapi/api"
        self.key = "bbacbddd2b2349519b579cc0ff63de6e"
        try:
            self.info = sys.argv[1]
        except Exception,e:
            self.info = infos
        try:
            self.userid = sys.argv[2]
        except Exception,e:
            self.userid = ""



    def curlpost(self, url, string=''):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        head = ['Content-Type:application/json;charset=utf-8']
        c.setopt(pycurl.HTTPHEADER, head)
        c.setopt(pycurl.CUSTOMREQUEST, "POST")
        c.setopt(pycurl.POSTFIELDS, string)
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.perform()
        datas = b.getvalue()
        returndata = datas
        b.close()
        c.close()
        return returndata

    def query(self, ):

        request_data = {
            "key": self.key,
            "info": self.info,
            "userid": self.userid
        }

        request_str = json.dumps(request_data)
        res = self.curlpost(self.requesturl, request_str)

        return res

if __name__ == "__main__":
    st = time.time()
    tr = turingRobot('吃饭不')
    res = tr.query()
    print res

    #sys.exit()
    data = json.loads(res)
    print data['text']
    et = time.time()
    print et-st
