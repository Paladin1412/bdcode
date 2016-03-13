#!/home/work/.jumbo/bin/python
# -*- coding:utf-8 -*-
'''

依赖库：
    1. urllib
    2. urllib2
    3. json
    4. logging

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
import MySQLdb

logging.basicConfig(
    level=logging.INFO,
    format=('%(asctime)s %(filename)s[line:%(lineno)d] ' 
        '%(levelname)s %(message)s'),
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='/home/work/rd.bak/ljt/unittest/passport/vendor.log',
    filemode='a'
)


class Param(object):
    #基础参数
    _targetUrl = ""
    _vendorID  = ""
    _vmd5 = ""
    _passportUrl = ""
    _token = ""
    _user_portrait = ""
    _current_ad_start = 0
    _current_ad_end = 0

    def buildParam(self):
        config = ConfigParser.ConfigParser()
        config_dir = os.path.join(os.path.dirname(__file__), "conf.ini")
        config.read(config_dir)
        self._targetUrl = config.get("ad_ios", "targetUrl")
        self._vendorID = config.get("ad_ios", "vendorID")
        self._vmd5 = config.get("ad_ios", "vmd5")
        self._passportUrl = config.get("ad_ios", "passportUrl")
        self._celldictUrl = config.get("ad_ios", "celldictUrl")
        print self._targetUrl
        self._user_portrait = config.get("ad_ios", "user_portrait")
        self._token = config.get("ad_ios", "token")


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


class vendorTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.man = Param()
        self.man.buildParam()
        bind_data = {}
        bind_data["type"] = "vendor"
        bind_data["device"] = "ios"
        bind_data["app_version"] = "9.1"
        bind_data["system_version"] = "5.3"
        bind_data["vendor_id"] = self.man._vendorID
        bind_data["vmd5"] = self.man._vmd5
        bind_data["is_pro"] = "0"

        ret = execute_request(self.man._targetUrl, bind_data)
        print ret
        self.man._current_ad_start = ret['data']['vip']['current_ad_vip_start']
        self.man._current_ad_end = ret['data']['vip']['current_ad_vip_end']
        self.conn=MySQLdb.connect(host="10.252.29.54",user="root",passwd="baidu@123",db="db_simeji_passport",charset="utf8",port=3810)
        print "connection begin..."

    @classmethod
    def tearDownClass(self):
        self.conn.close()
        print "connection destroy...."

    
    def testcase_bill1_0(self):
        "测试用例1：bill接口，参数合法，利用vendor id进行购买去广告服务"
        bill_data = {}
        bill_data["vendor_id"] = self.man._vendorID
        bill_data["action"] = "bill"
        bill_data["is_pro"] = "0"
        bill_data["device"] = "ios"
        bill_data["system_version"] = "9.1"
        bill_data["app_version"] = "4.5"
        bill_data["vmd5"] = self.man._vmd5
        bill_data["signature"] = ""
        bill_data["bill_type"] = "consume"
        bill_data["data"] = ""
        with open(os.path.join(os.path.dirname(__file__), "ad_receipt.txt"))as fopen:
            bill_data['data'] = fopen.readline()
        ret = execute_request(self.man._passportUrl+"/user", bill_data)
        print ret
        #self.assertEqual(ret["errno"], 22)
    
    def testcase_vip_0(self):
        """测试用例2：vip接口，参数合法，利用vendor id获取vip时间，判断是否过期"""
        vip_data = {}
        vip_data["vendor_id"] = self.man._vendorID
        vip_data["is_pro"] = "1"
        vip_data["action"] = "vip"
        vip_data["device"] = "ios"
        vip_data["system_version"] = "9.1"
        vip_data["app_version"] = "4.5"
        vip_data["vmd5"] = self.man._vmd5
        ret = execute_request(self.man._passportUrl+"/user", vip_data)
        print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")
        flag1 = True if "current_ad_vip_start" in ret['data'].keys() else False
        flag2 = True if "current_ad_vip_end" in ret['data'].keys() else False
        self.assertEqual(flag1 and flag2, True)

    def getVip(self, req):
        ret = execute_request(self.man._passportUrl+"/user", req)
        return ret

    def testcase_vendorOrderCopy_1(self):
        #测试用例3：vendor id匿名购买后，利用手机号登录，将购买的vip时间赋予给第三方帐号
        login_data = {}
        login_data["device"] = "ios"
        login_data["app_version"] = "4.5"
        login_data["system_version"] = "9.1"
        login_data["action"] = "login"
        login_data["country"] = "cn"
        login_data["mobile"] = "18476731655"
        login_data["type"] = "mobile"
        login_data["pwd"] = "03c61a62bafe36b51a2d95ea848f5731"
        login_data["vendor_id"] = self.man._vendorID
        login_data["vmd5"] = self.man._vmd5
        login_data["is_pro"] = "0"
        ret = execute_request(self.man._passportUrl+"/mobile", login_data)
        print ret
        self.assertEqual(ret["errno"], 0)
        #self.assertEqual(ret["errmsg"], "0")
        
        sql1 = "update unsubscribe_bill set current_vip_end=%d where user_id=%d and product_type=1 limit 1"%(2, 1458879600)
        print queryDB(self.conn, sql1)
        vip_data = {}
        vip_data["bduss"] = ret['data']['bduss']
        vip_data["is_pro"] = "0"
        vip_data["action"] = "vip"
        vip_data["device"] = "ios"
        vip_data["system_version"] = "9.1"
        vip_data["app_version"] = "4.5"
        retVip = execute_request(self.man._passportUrl+"/user", vip_data)
        retVip = self.getVip(vip_data)
        #self.assertEqual(self.man._current_ad_start, retVip['data']['current_ad_vip_start'])
        self.assertEqual(86402, retVip['data']['current_ad_vip_end'])
         
        retLogin = execute_request(self.man._passportUrl+"/mobile", login_data)
        print retLogin

        retVip1 = self.getVip(vip_data)
        self.assertEqual(self.man._current_ad_end, retVip1['data']['current_ad_vip_end'])
        
    
    def testcase_vendorOrderCopy_3(self):
        #测试用例4：vendor ID 匿名购买后，利用第三方帐号登录，将购买的vip时间赋予给第三方帐号
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
        bind_data["is_pro"] = "0"
        bind_data["vendor_id"] = self.man._vendorID

        ret = execute_request(self.man._passportUrl+"/sectbind", bind_data)
        print self.man._passportUrl
        print ret
        self.assertEqual(ret["errno"],0)
        self.assertEqual(ret["errmsg"], "success")
    
        vip_data = {}
        vip_data["bduss"] = ret['data']['bduss']
        vip_data["is_pro"] = "0"
        vip_data["action"] = "vip"
        vip_data["device"] = "ios"
        vip_data["system_version"] = "9.1"
        vip_data["app_version"] = "4.5"
        retVip = execute_request(self.man._passportUrl+"/user", vip_data)
        #self.assertEqual(self.man._current_ad_start, retVip['data']['current_ad_vip_start'])
        self.assertEqual(self.man._current_ad_end, retVip['data']['current_ad_vip_end'])
    
    def testcase_celldict_5(self):
        #测试用例5：细胞词库是否命中
        ret = execute_request(self.man._celldictUrl)
        self.assertLessEqual(ret['cache'], 1)
        print ret
        if ret['data'] and ret['data'][0]['candidates']:
            for can in ret['data'][0]['candidates']:
                if can['cell_mask'] > 0:
                    self.assertEqual(can['cell_mask'], 512)
if __name__=="__main__":
    unittest.main()
