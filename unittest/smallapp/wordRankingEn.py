#!/home/work/.jumbo/bin/python
# -*- coding:utf-8 -*-
'''

依赖库：
    1. urllib
    2. urllib2
    3. json
    4. logging

作者：lijingtao@baidu.com
时间：2015-12-18

'''
import os
import urllib
import urllib2
import json
import logging
import ConfigParser
import unittest
import MySQLdb

def execute_request(url='',data={},method='post'):
    if method=='post':
        req = urllib2.Request(url=url,data=urllib.urlencode(data))
    else:
        req = urllib2.Request(url=url)
    try:
        req_data = urllib2.urlopen(req)
        res = json.loads(req_data.read())
    except Exception as e:
        #print e
        res = {'errno':'xxx','errmsg':'failed'}
    return res


def queryDB(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    ret = cur.fetchall()
    cur.close()
    conn.commit()

def dup_one_page(words, t):
    flag = True
    dd = {}
    for word in words:
        key = word['hira']+word['word']
        if word['type'] != t or key in dd:
            flag = False
        dd[key] = 1
    return flag

def dup_two_page(fpage, spage, t):
    flag = True
    for word1 in fpage:
        key1 = word1['hira']+word1['word']
        if t != word1['type']:
            print word1
            flag = False
        for word2 in spage:
            key2 = word2['hira']+word2['word']
            if t != word2['type']:
                print word2
                flag = False
            if key1 == key2:
                print key1, key2
                flag = False
    return flag


class wordRankingEnTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = ConfigParser.ConfigParser()
        config_dir = os.path.join(os.path.dirname(__file__), "conf.ini")
        config.read(config_dir)
        self._targetUrl = config.get("rankingEn_offline", "targetUrl")
        self._host = config.get("rankingEn_offline", "host")
        self._port = config.get("rankingEn_offline", "port")
        self.conn=MySQLdb.connect(host=self._host,user="root",passwd="baidu@123",db="db_simeji_ranking",charset="utf8",port=int(self._port))
        print self._targetUrl
        print "connection begin..."

    @classmethod
    def tearDownClass(self):
        self.conn.close()
        print "connection destroy...."

    
    def testcase_list_0(self):
        "测试用例1：list接口，emoji ranking列表"
        list_data = {}
        list_data["emoji"] = 1
        list_data["page"] = 1
        list_data["device"] = "android"
        list_data["system_version"] = "5.5"
        list_data["app_version"] = "9.2"
        ret = execute_request(self._targetUrl+"/getWordList", list_data)
        print ret
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'], 'success')
        flag = dup_one_page(ret['data'], 1)
        list_data['page'] = 2
        ret2 = execute_request(self._targetUrl+"/getWordList", list_data)
        self.assertEqual(ret2['errno'], 0)
        self.assertEqual(ret2['errmsg'], 'success')
        if ret2['data']:
            ff = dup_two_page(ret['data'], ret2['data'], 1)

    def testcase_list_1(self):
        "测试用例2：list接口，kaomoji ranking列表"
        list_data = {}
        list_data["kaomoji"] = 1
        list_data["page"] = 1
        list_data["device"] = "android"
        list_data["system_version"] = "5.5"
        list_data["app_version"] = "9.2"
        ret = execute_request(self._targetUrl+"/getWordList", list_data)
        print ret
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'], 'success')
        flag = dup_one_page(ret['data'], 0)
        list_data['page'] = 2
        ret2 = execute_request(self._targetUrl+"'getWordList", list_data)
        self.assertEqual(ret2['errno'], 0)
        self.assertEqual(ret2['errmsg'], 'success')
        if ret2['data']:
            ff = dup_two_page(ret['data'], ret2['data'], 0)

if __name__=="__main__":
    unittest.main()
if __name__=="__main__":
    unittest.main()
