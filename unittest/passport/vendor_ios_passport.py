#!/home/work/.jumbo/bin/python
# -*- coding:utf-8 -*-
'''
高级云服务接口监控(自定义报警接入monitor)
本代码是自定义监控接入noah，报警使用monitor的一个监控脚本

依赖库：
    1. urllib
    2. urllib2
    3. json
    4. Monitor(python重构)
    5. logging

作者：lizeyang01@baidu.com
时间：2015-07-09

'''
import os
import urllib
import urllib2
import json
#import Monitor
import logging
import ConfigParser
import unittest

logging.basicConfig(
    level=logging.INFO,
    format=('%(asctime)s %(filename)s[line:%(lineno)d] ' 
        '%(levelname)s %(message)s'),
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='/home/work/rd.bak/ljt/unittest/passport/vendor.log',
    filemode='a'
)

#monitor = Monitor.Monitor()

class Param(object):
    #基础参数
    _targetUrl = ""
    _vendorID  = ""
    _vmd5 = ""
    _passportUrl = ""
    _token = ""
    _user_portrait = ""
    _current_ad_end = 0

    def buildParam(self):
        config = ConfigParser.ConfigParser()
        config_dir = os.path.join(os.path.dirname(__file__), "conf.ini")
        config.read(config_dir)
        self._targetUrl = config.get("vendor", "targetUrl")
        self._vendorID = config.get("vendor", "vendorID")
        self._vmd5 = config.get("vendor", "vmd5")
        self._passportUrl = config.get("vendor", "passportUrl")
        print self._targetUrl
        self._user_portrait = config.get("passport", "user_portrait")
        self._token = config.get("passport", "token")


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


class vendorTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.man = Param()
        self.man.buildParam()
        bind_data = {}
        bind_data["type"] = "vendor"
        bind_data["device"] = "ios"
        bind_data["app_version"] = "4.3"
        bind_data["system_version"] = "9.1"
        bind_data["vendor_id"] = self.man._vendorID
        bind_data["vmd5"] = self.man._vmd5
        bind_data["is_pro"] = "1"

        ret = execute_request(self.man._targetUrl, bind_data)
        #print ret
        self.man._current_ad_end = ret['data']['vip']['current_ad_vip_end']
        print "connection begin..."

    @classmethod
    def tearDownClass(self):
        print "connection destroy...."

    def verifyVIP(self, data, strDesc):
        print strDesc
        flag1 = True if 'current_ad_vip_start' in data.keys() else False
        flag2 = True if 'current_ad_vip_end' in data.keys() else False
        flag3 = True if 'current_vip_start' in data.keys() else False
        flag4 = True if 'current_vip_end' in data.keys() else False
        print flag1, flag2, flag3, flag4
        self.assertEqual(flag1 and flag2 and flag3 and flag4, True)

    def testcase_fetch1_0(self):
        "测试用例1：fetch接口，参数合法，vendor id匿名登录成功，使用高级云服务"
        fetch_data = {}
        fetch_data["vendor_id"] = self.man._vendorID
        fetch_data["action"] = "fetch"
        fetch_data["device"] = "ios"
        fetch_data["system_version"] = "9.1"
        fetch_data["app_version"] = "4.2"
        fetch_data["mask"] = "1"
        fetch_data["is_pro"] = "1"
        fetch_data["vmd5"] = self.man._vmd5
        #sum = ""
        #for key in fetch_data.keys():
        #    sum += key + "=" + fetch_data[key] + "&"
        #fetchUrl = self.man._passportUrl+"?"+sum[:-1]
        ret = execute_request(self.man._passportUrl+"/user", fetch_data)
        #print ret
        self.assertEqual(ret["errno"], 0)

    def testcase_fetch2_0(self):
        "测试用例2：fetch接口，参数不合法，vendor id不合法，匿名登录失败"
        fetch_data = {}
        fetch_data["vendor_id"] = self.man._vendorID+"NOTVALID"
        fetch_data["action"] = "fetch"
        fetch_data["device"] = "ios"
        fetch_data["system_version"] = "9.1"
        fetch_data["app_version"] = "4.2"
        fetch_data["vmd5"] = "4b4dc157c230098a76a3ec635df2fa9c"
        fetch_data["mask"] = "1"
        fetch_data["is_pro"] = "1"
        #sum = ""
        #for key in fetch_data.keys():
        #    sum += key + "=" + fetch_data[key] + "&"
        #fetchUrl = self.man._passportUrl+"?"+sum[:-1]
        ret = execute_request(self.man._passportUrl+"/user", fetch_data)
        print ret
        self.assertEqual(ret["errno"], 95)


    def testcase_push1_0(self):
        "测试用例3：push接口，参数合法，利用vendor id进行匿名登录使用高级云服务"
        push_data = {}
        push_data["vendor_id"] = self.man._vendorID
        push_data["action"] = "push"
        push_data["is_pro"] = "1"
        push_data["device"] = "ios"
        push_data["system_version"] = "9.1"
        push_data["app_version"] = "4.2"
        push_data["field"] = "u"
        push_data["vmd5"] = self.man._vmd5
        push_data["conf"] = "{'dict_9':-1,}"
        #sum = ""
        #for key in fetch_data.keys():
        #    sum += key + "=" + fetch_data[key] + "&"
        #fetchUrl = self.man._passportUrl+"?"+sum[:-1]
        ret = execute_request(self.man._passportUrl+"/user", push_data)
        #print ret
        self.assertEqual(ret["errno"], 0)

        fetch_data = {}
        fetch_data["vendor_id"] = self.man._vendorID
        fetch_data["action"] = "fetch"
        fetch_data["device"] = "ios"
        fetch_data["system_version"] = "9.1"
        fetch_data["app_version"] = "4.2"
        fetch_data["mask"] = "1"
        fetch_data["is_pro"] = "1"
        fetch_data["vmd5"] = self.man._vmd5
        fetch_ret = execute_request(self.man._passportUrl+"/user", fetch_data)
        #self.assertEqual(fetch_ret["data"]["u"]["conf"]["dict_9"], 0)

    
    def testcase_list1_0(self):
        "测试用例4：list接口，参数合法，利用vendor id进行匿名登录使用高级云服务下载"
        list_data = {}
        list_data["vendor_id"] = self.man._vendorID
        list_data["is_pro"] = "1"
        list_data["action"] = "wlist"
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.2"
        list_data["vmd5"] = self.man._vmd5
        ret = execute_request(self.man._passportUrl+"/user", list_data)
        #print ret
        self.assertEqual(ret["errno"], 0)

    def testcase_bill1_0(self):
        "测试用例5：bill接口，参数合法，利用vendor id进行购买后讲数据同步到simeji服务器"
        bill_data = {}
        bill_data["vendor_id"] = self.man._vendorID
        bill_data["action"] = "bill"
        bill_data["is_pro"] = "bill"
        bill_data["device"] = "ios"
        bill_data["system_version"] = "9.1"
        bill_data["app_version"] = "4.2"
        bill_data["vmd5"] = self.man._vmd5
        bill_data["data"] = ""
        with open(os.path.join(os.path.dirname(__file__), "receipt.txt"))as fopen:
            bill_data['data'] = fopen.readline()
        ret = execute_request(self.man._passportUrl+"/user", bill_data)
        #print ret
        self.assertEqual(ret["errno"], 0)

    def testcase_vip1_0(self):
        """测试用例6：vip接口，参数合法，利用vendor id获取vip时间，判断是否过期"""
        vip_data = {}
        vip_data["vendor_id"] = self.man._vendorID
        vip_data["is_pro"] = "1"
        vip_data["action"] = "vip"
        vip_data["device"] = "ios"
        vip_data["system_version"] = "9.1"
        vip_data["app_version"] = "4.2"
        vip_data["vmd5"] = self.man._vmd5
        ret = execute_request(self.man._passportUrl+"/user", vip_data)
        #print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")
        self.verifyVIP(ret['data'], "测试用例6：获取vip信息")

    def testcase_vendorOrderCopy1_0(self):
        """测试用例7：vendor id匿名购买后，利用手机号登录，将购买的vip时间赋予给第三方帐号"""
        login_data = {}
        login_data["device"] = "ios"
        login_data["app_version"] = "3.1"
        login_data["system_version"] = "9.1"
        login_data["action"] = "login"
        login_data["country"] = "cn"
        login_data["mobile"] = "15626471657"
        login_data["type"] = "mobile"
        login_data["pwd"] = "372083da28d90a0c8a5c9392f17eed6e"
        login_data["vendor_id"] = self.man._vendorID
        login_data["vmd5"] = self.man._vmd5
        login_data["is_pro"] = "1"
        ret = execute_request(self.man._passportUrl+"/mobile", login_data)

        print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")
        login_data['bduss'] = ret['data']['bduss']
        login_data['action'] = 'logout'
        ret1 = execute_request(self.man._passportUrl+"/mobile", login_data)

        self.assertEqual(self.man._current_ad_end, ret['data']['vip']['current_ad_vip_end'])

    def testcase_vendorOrderCopy2_0(self):
        """测试用例8：vendor ID 匿名购买后，利用第三方帐号登录，将购买的vip时间赋予给第三方帐号"""
        bind_data = {}
        bind_data["type"] = "facebook"
        bind_data["device"] = "ios"
        bind_data["app_version"] = "4.3"
        bind_data["system_version"] = "9.1"
        bind_data["osid"] = "1421131934858850"
        bind_data["token"] = self.man._token
        bind_data["user_name"] = "Gibbon Zhuo"
        bind_data["tmd5"] = "805bc2d55c1d9bb7bfe386d7df9fe671"
        bind_data["user_portrait"] = self.man._user_portrait
        bind_data["vmd5"] = self.man._vmd5
        bind_data["is_pro"] = "1"
        bind_data["vendor_id"] = self.man._vendorID

        ret = execute_request(self.man._passportUrl+"/sectbind", bind_data)
        print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")
if __name__=="__main__":
    unittest.main()
