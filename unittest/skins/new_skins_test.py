#!/home/work/python/bin/python
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
import random 
import MySQLdb
import time

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
    return ret

def dup_one_page(words, t):
    flag = True
    dd = {}
    for word in words:
        key = word['hira']+word['word']
        if word['type'] != t or key in dd:
            flag = False
        dd[key] = 1
    return flag


class NewSkinsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = ConfigParser.ConfigParser()
        config_dir = os.path.join(os.path.dirname(__file__), "conf.ini")
        config.read(config_dir)
        self._targetUrl = config.get("new_skins_offline", "targetUrl")
        self._host = config.get("new_skins_offline", "host")
        self._port = config.get("new_skins_offline", "port")
        self.conn = MySQLdb.connect(host=self._host,user="root",passwd="baidu@123",db="db_simeji_skins",charset="utf8",port=int(self._port))
        print self._targetUrl
        print "connection begin..."

    @classmethod
    def tearDownClass(self):
        self.conn.close()
        print "connection destroy...."

    def db_test(self, sql, api_ret):
        db_ret = queryDB(self.conn, sql)
        self.assertEqual(len(db_ret), len(api_ret['data']))
        flag = True
        for ind, skin in enumerate(db_ret):
            if int(skin[0]) != int(api_ret['data'][ind]['id']):
                print skin[0], int(api_ret['data'][ind]['id'])
                flag = False
        self.assertEqual(flag, True)

    def testcase_list_new_1(self):
        "测试用例1：listSkins接口，新版皮肤商城最新皮肤列表is_pro"
        list_data = {}
        list_data["is_pro"] = 1
        list_data["new"] = 1
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.5"
        ret = execute_request(self._targetUrl, list_data)
        #print ret
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'], 'success')

        #两周内上传过的皮肤算是新皮肤
        now = int(time.time())
        start = now - 1209600
        sql = "select * from ios_skin_info WHERE is_online = 1 AND (type_mask&%d)>0 AND public_begtime>%d AND public_begtime<%d AND (public_endtime>%d OR public_endtime=0) ORDER BY `public_begtime` DESC" % (0x2, start, now, now)
        print sql
        self.db_test(sql, ret)

    def testcase_list_new_2(self):
        "测试用例2：listSkins接口，新版皮肤商城最新皮肤列表 is_ipad"
        list_data = {}
        list_data["is_ipad"] = 1
        list_data["new"] = 1
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.5"
        ret = execute_request(self._targetUrl, list_data)
        #print ret
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'], 'success')

        #两周内上传过的皮肤算是新皮肤
        now = int(time.time())
        start = now - 1209600
        sql = "select * from ios_skin_info WHERE is_online = 1 AND (type_mask&%d)>0 AND public_begtime>%d AND public_begtime<%d AND (public_endtime>%d OR public_endtime=0) ORDER BY `public_begtime` DESC" % (0x4, start, now, now)
        print sql
        self.db_test(sql, ret)
 
    def testcase_list_new_3(self):
        "测试用例3：listSkins接口，新版皮肤商城最新皮肤列表 is_pro=0 is_ipad=0"
        list_data = {}
        list_data["is_pro"] = 0
        list_data["new"] = 1
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.5"
        ret = execute_request(self._targetUrl, list_data)
        #print ret
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'], 'success')

        #两周内上传过的皮肤算是新皮肤
        now = int(time.time())
        start = now - 1209600
        sql = "select * from ios_skin_info WHERE is_online = 1 AND (type_mask&%d)>0 AND public_begtime>%d AND public_begtime<%d AND (public_endtime>%d OR public_endtime=0) ORDER BY `public_begtime` DESC" % (0x1, start, now, now)
        print sql
        self.db_test(sql, ret)

    def testcase_list_hot_4(self):
        "测试用例4：listSkins接口，新版皮肤商城最hot皮肤列表 is_pro=0 is_ipad=0"
        list_data = {}
        list_data["is_pro"] = 0
        list_data["hot"] = 1
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.5"
        ret = execute_request(self._targetUrl, list_data)
        #print ret
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'], 'success')

        #两周内上传过的皮肤算是新皮肤
        now = int(time.time())
        sql = "select * from ios_skin_info WHERE is_online = 1 AND (type_mask&%d)>0 AND public_begtime<%d AND (public_endtime>%d OR public_endtime=0) ORDER BY `preview` DESC" % (0x1, now, now)
        print sql
        self.db_test(sql, ret)

    def testcase_list_hot_5(self):
        "测试用例5：listSkins接口，新版皮肤商城分类列表 is_pro=0 is_ipad=0"
        list_data = {}
        list_data["is_pro"] = 0
        list_data["category"] = 1
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.5"
        ret = execute_request(self._targetUrl, list_data)
        #print ret
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'], 'success')

        #两周内上传过的皮肤算是新皮肤
        now = int(time.time())
        sql = "select * from ios_skin_info WHERE is_online = 1 AND `category_new` IN (1,2,3,4,5,6) AND (type_mask&%d)>0 AND public_begtime<%d AND (public_endtime>%d OR public_endtime=0) ORDER BY `order` ASC" % (0x1, now, now)
        print sql
        db_ret = queryDB(self.conn, sql)
        category = [[], [], [], [], [], []]
        for i in xrange(len(db_ret)):
            category[db_ret[i][3]-1].append(db_ret[i][0])
        flag = True
        for key in ret['data']:
            for ind, ss in enumerate(ret['data'][key]):
                if category[int(key[-1])-1][ind] != int(ss['id']):
                    flag = False
        self.assertEqual(flag, True)


if __name__=="__main__":
    unittest.main()
