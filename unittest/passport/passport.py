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
        self._device = config.get("passport", "device")
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


class passportTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.man = Param()
        self.man.buildParam()
        bind_data = {}
        bind_data["type"] = "facebook"
        bind_data["device"] = self.man._device
        bind_data["app_version"] = "4.3"
        bind_data["system_version"] = "9.1"
        bind_data["osid"] = "1421131934858850"
        bind_data["token"] = self.man._token
        bind_data["user_name"] = "Gibbon Zhuo"
        bind_data["tmd5"] = "805bc2d55c1d9bb7bfe386d7df9fe671"
        bind_data["user_portrait"] = self.man._user_portrait

        #print "\n".join(bind_data.values())
        ret = execute_request(self.man._targetUrl+"/sectbind", bind_data)
        #self.assertEqual(ret["errno"], 0)
        print ret
        self.man.setBduss(ret["data"]["bduss"])
        print "connection begin..."

    @classmethod
    def tearDownClass(self):
        logout_data = {}
        logout_data["type"] = "facebook"
        logout_data["device"] = self.man._device
        logout_data["app_version"] = "4.3"
        logout_data["system_version"] = "9.1"
        logout_data["bduss"] = self.man._bduss
        ret = execute_request(self.man._targetUrl+"/logout", logout_data)
        #self.assertEqual(ret["errno"], 0)
        #self.assertEqual(ret["data"]["bduss"], self.man._bduss)
        print ret
        print "connection destroy...."


    def testcase_fetch1_0(self):
        "测试用例1：fetch接口，参数合法，利用bduss使用高级云服务"
        fetch_data = {}
        fetch_data["bduss"] = self.man._bduss
        fetch_data["action"] = "fetch"
        fetch_data["device"] = self.man._device
        fetch_data["system_version"] = "9.1"
        fetch_data["app_version"] = "4.2"
        fetch_data["mask"] = "1"
        ret = execute_request(self.man._targetUrl+"/user", fetch_data)
        self.assertEqual(ret["errno"], 0)
        self.tearDownClass()
        ret = execute_request(self.man._targetUrl+"/user", fetch_data)
        self.assertEqual(ret["errno"], 0)

    def testcase_push1_0(self):
        "测试用例3：push接口，参数合法，利用bduss使用高级云服务"
        push_data = {}
        push_data["bduss"] = self.man._bduss
        push_data["action"] = "push"
        push_data["device"] = self.man._device
        push_data["system_version"] = "9.1"
        push_data["app_version"] = "4.2"
        push_data["field"] = "u"
        push_data["conf"] = '{"dict_9":1, "dict_10":1}'
        ret = execute_request(self.man._targetUrl+"/user", push_data)
        #print ret
        self.assertEqual(ret["errno"], 0)

        fetch_data = {}
        fetch_data["bduss"] = self.man._bduss
        fetch_data["action"] = "fetch"
        fetch_data["device"] = self.man._device
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
        list_data["device"] = self.man._device
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
        vip_data["device"] = self.man._device
        vip_data["system_version"] = "9.1"
        vip_data["app_version"] = "4.2"
        ret = execute_request(self.man._targetUrl+"/user", vip_data)
        print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")

    def testcase_trailBill_5(self):
        """测试用例6：tbill接口，参数合法，高级会员免费使用"""
        tbill_data = {}
        tbill_data['device'] = self.man._device
        tbill_data['bduss'] = self.man._bduss
        tbill_data["system_version"] = "9.1"
        tbill_data["app_version"] = "4.2"
        tbill_data['bill_type'] = "consume"
        tbill_data['pid'] = "android.trail14day"
        tbill_data['source'] = "popup_20151217"
        tbill_data['action'] = "tbill"
        #ret = execute_request(self.man._targetUrl+"/user",tbill_data)
        #print ret
        #self.assertEqual(ret['errno'], 0)
        #self.assertEqual(ret['errmsg'], 'success')
if __name__=="__main__":
    unittest.main()
