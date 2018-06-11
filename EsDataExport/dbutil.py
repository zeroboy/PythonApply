# -*- coding: UTF-8 -*-
# File: dbutil.py
# Date: 2009-03-18
# Author: bobning

"""
数据库操作函数库
"""
import re
import DBUtils
from DBUtils.PooledDB import PooledDB
from DBUtils.PersistentDB import PersistentDB


dbo=None
__version__=DBUtils.__version__

class DBObject(object):
    """数据库连接对象"""

    def __init__(self,params,dbutype='PooledDB'):
        """初始化连接池
        
        params包含了数据库连接参数字典
        dbutype表示DBUtils的连接类型，分为PooledDB和PersistentDB两种
        """
        self.params=params
        if dbutype=='PooledDB':
            self.dbpool=PooledDB(**params)
        elif dbutype=='PersistentDB':
            self.dbpool=PersistentDB(**params)
        else:
            raise ValueError,'Not support dbutype: %s'%repr(dbutype)

    def getconn(self):
        return self.dbpool.connection()

    def query(self,sql):
        """执行查询，并返回结果集"""
        cur=None
        conn=None
        try:
            conn=self.getconn()
            cur=conn.cursor()
            cur.execute(sql)
            dataset=cur.fetchall()
            return dataset
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def update(self,sql):
        """执行更新类操作，返回作用记录数"""
        cur=None
        conn=None
        try:
            conn=self.getconn()
            cur=conn.cursor()
            nrec=cur.execute(sql)
            conn.commit()
            if nrec!=None:
                return nrec
            else:
                return cur.rowcount
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def mysql_lastid(self,sql):
        """执行MySQL的INSERT操作，并将刚插入记录的ID返回"""
        cur=None
        conn=None
        try:
            conn=self.getconn()
            cur=conn.cursor()
            nrec=cur.execute(sql)
            conn.commit()
            cur.execute('''SELECT last_insert_id()''')
            dataset=cur.fetchall()
            lastid=dataset[0][0]
            return lastid
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def pgsql_lastid(self,sql):
        """执行PostgreSQL的INSERT操作，并将插入记录的ID返回"""
        cur=None
        conn=None
        try:
            conn=self.getconn()
            cur=conn.cursor()
            nrec=cur.execute(sql)
            conn.commit()
            cur.execute('''SELECT lastval()''')
            dataset=cur.fetchall()
            lastid=dataset[0][0]
            return lastid
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

def __init__(params,dbutype='PooledDB'):
    global dbo
    dbo=DBObject(params,dbutype)

def getconn():
    return dbo.getconn()

def query(sql):
    return dbo.query(sql)

def update(sql):
    return dbo.update(sql)

def mysql_lastid(sql):
    return dbo.mysql_lastid(sql)

def pgsql_lastid(sql):
    return dbo.pgsql_lastid(sql)

def quote_buffer(buf):
    retstr=''.join(map(lambda c:'%02x'%ord(c),buf))
    retstr="x'"+retstr+"'"
    return retstr
