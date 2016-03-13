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
import random

class Param(object):
    #基础参数
    _targetUrl = ""
    _configUrl = ""
    _lp_list  = ""
    def buildParam(self):
        config = ConfigParser.ConfigParser()
        config_dir = os.path.join(os.path.dirname(__file__), "conf.ini")
        config.read(config_dir)
        self._targetUrl = config.get("lp", "targetUrl")
        self._configUrl = config.get("lp", "configUrl")
        strLp = config.get("lp", "lp_list").strip()
        self._lp_list = strLp.split(",")
        print self._targetUrl


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


class lpTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.man = Param()
        self.man.buildParam()
        print "connection begin..."

    @classmethod
    def tearDownClass(self):
        print "connection destroy...."

    def testcase_getLink1_0(self):
        "测试用例1：获取上屏词对应的链接接口，参数合法ios，返回的data与配置平台上的配置一致"
        list_data = {}
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.2"
        ret = execute_request(self.man._targetUrl+"/getLink", list_data)
        #print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")

        configUrl = "%s/simeji_%s_link"%(self.man._configUrl, list_data['device'])
        retConfig = execute_request(configUrl)
        self.assertEqual(retConfig, ret['data'])
        print retConfig['res'][0]


    def testcase_getRes2_0(self):
        "测试用例2：获取lp资源接口，参数合法ios，返回的data与配置平台上的配置一致"
        req_data = {}
        req_data["device"] = "ios"
        req_data["system_version"] = "9.1"
        req_data["app_version"] = "4.2"
        print self.man._lp_list
        for lp in self.man._lp_list:
            req_data['lp'] = lp
            ret = execute_request(self.man._targetUrl+"/getRes", req_data)
            #print ret
            self.assertEqual(ret["errno"], 0)
            self.assertEqual(ret["errmsg"], "success")

            conf_data = {"lp": lp}
            configUrl = "%s/simeji_%s_lp"%(self.man._configUrl, req_data['device'])
            retConfig = execute_request(configUrl, conf_data)
            print retConfig


if __name__=="__main__":
    unittest.main()
