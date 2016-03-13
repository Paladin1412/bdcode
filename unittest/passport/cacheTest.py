#!/home/work/.jumbo/bin/python
# -*- coding:utf-8 -*-
'''

依赖库：
    1. urllib
    2. urllib2
    3. json
    4. unittest
作者：lijingtao@baidu.com
时间：2015-11-03

'''
import os
import urllib
import urllib2
import json
import ConfigParser
import unittest

class Param(object):
    #基础参数
    _targetUrl = ""
    _bduss  = ""
    _token = ""
    _user_portrait = ""

    def buildParam(self):
        config = ConfigParser.ConfigParser()
        config_dir = os.path.join(os.path.dirname(__file__), "conf.ini")
        config.read(config_dir)
        self._targetUrl = config.get("passport", "targetUrl")
        self._token = config.get("passport", "token")
        self._user_portrait = config.get("passport", "user_portrait")
        print self._targetUrl

    def setBduss(self, bduss):
        self._bduss = bduss

def execute_request(url='',data={},method='post'):
    if method=='post':
        req = urllib2.Request(url=url,data=urllib.urlencode(data))
    else:
        req = urllib2.Request(url=url)
    try:
        req_data = urllib2.urlopen(req)
        res = json.loads(req_data.read())
    except Exception as e:
        print e
        res = {'errno':'xxx','errmsg':'failed'}
    return res


class cacheTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print "connection begin..."

    @classmethod
    def tearDownClass(self):
        print ret
        print "connection destroy...."


    def testcase_cacheTest_0(self):
        "测试用例1："

    def testcase_fetch2_0(self):
        "测试用例2：fetch接口，参数不合法，bduss无效，不能使用高级云服务"
        fetch_data = {}
        fetch_data["bduss"] = self.man._bduss+"notvalid"
        fetch_data["action"] = "fetch"
        fetch_data["device"] = "ios"
        fetch_data["system_version"] = "9.1"
        fetch_data["app_version"] = "4.2"
        fetch_data["mask"] = "1"
        #sum = ""
        #for key in fetch_data.keys():
        #    sum += key + "=" + fetch_data[key] + "&"
        #fetchUrl = self.man._passportUrl+"?"+sum[:-1]
        ret = execute_request(self.man._targetUrl+"/user", fetch_data)
        #print ret
        self.assertEqual(ret["errno"], 12)


    def testcase_push1_0(self):
        "测试用例3：push接口，参数合法，利用bduss使用高级云服务"
        push_data = {}
        push_data["bduss"] = self.man._bduss
        push_data["action"] = "push"
        push_data["device"] = "ios"
        push_data["system_version"] = "9.1"
        push_data["app_version"] = "4.2"
        push_data["field"] = "u"
        push_data["conf"] = "{'dict_9':-1,}"
        #sum = ""
        #for key in fetch_data.keys():
        #    sum += key + "=" + fetch_data[key] + "&"
        #fetchUrl = self.man._passportUrl+"?"+sum[:-1]
        ret = execute_request(self.man._targetUrl+"/user", push_data)
        #print ret
        self.assertEqual(ret["errno"], 0)

        fetch_data = {}
        fetch_data["bduss"] = self.man._bduss
        fetch_data["action"] = "fetch"
        fetch_data["device"] = "ios"
        fetch_data["system_version"] = "9.1"
        fetch_data["app_version"] = "4.2"
        fetch_data["mask"] = "1"
        fetch_ret = execute_request(self.man._targetUrl+"/user", fetch_data)
        print fetch_ret
        #self.assertEqual(fetch_ret["data"]["u"]["conf"]["dict_9"], 0)

    
    def testcase_list1_0(self):
        "测试用例4：list接口，参数合法，利用bduss使用高级云服务下载"
        list_data = {}
        list_data["bduss"] = self.man._bduss
        list_data["action"] = "wlist"
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.2"
        ret = execute_request(self.man._targetUrl+"/user", list_data)
        #print ret
        self.assertEqual(ret["errno"], 0)
    
    def testcase_vip1_0(self):
        "测试用例5：vip接口，参数合法，利用bduss获取vip时间，判断是否过期"
        vip_data = {}
        vip_data["bduss"] = self.man._bduss
        vip_data["action"] = "vip"
        vip_data["device"] = "ios"
        vip_data["system_version"] = "9.1"
        vip_data["app_version"] = "4.2"
        ret = execute_request(self.man._targetUrl+"/user", vip_data)
        print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")

        

if __name__=="__main__":
    unittest.main()
