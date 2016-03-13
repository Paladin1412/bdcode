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
    _bduss  = ""
    _token = ""
    _user_portrait = ""

    def buildParam(self):
        config = ConfigParser.ConfigParser()
        config_dir = os.path.join(os.path.dirname(__file__), "conf.ini")
        config.read(config_dir)
        self._targetUrl = config.get("inbox", "targetUrl")
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


class inboxTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.man = Param()
        self.man.buildParam()
        bind_data = {}
        bind_data["type"] = "mobile"
        bind_data["device"] = "ios"
        bind_data["app_version"] = "4.3"
        bind_data["system_version"] = "9.1"
        bind_data["country"] = "cn"
        bind_data["mobile"] = "15626471657"
        bind_data["action"] = "login"
        bind_data["pwd"] = "372083da28d90a0c8a5c9392f17eed6e"

        #print "\n".join(bind_data.values())
        ret = execute_request(self.man._targetUrl+"/mobile", bind_data)
        #self.assertEqual(ret["errno"], 0)
        #print ret
        self.man.setBduss(ret["data"]["bduss"])
        print "connection begin..."

    @classmethod
    def tearDownClass(self):
        logout_data = {}
        logout_data["action"] = "logout"
        logout_data["device"] = "ios"
        logout_data["app_version"] = "4.3"
        logout_data["system_version"] = "9.1"
        logout_data["bduss"] = self.man._bduss
        logout_data["country"] = "cn"
        ret = execute_request(self.man._targetUrl+"/mobile", logout_data)
        #self.assertEqual(ret["errno"], 0)
        #self.assertEqual(ret["data"]["bduss"], self.man._bduss)
        print ret
        print "connection destroy...."


    def testcase_list1_0(self):
        "测试用例1：list接口，参数合法，利用bduss获取所有消息"
        self.tearDownClass()
        list_data = {}
        list_data["bduss"] = self.man._bduss
        print self.man._bduss
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.2"
        list_data["umask"] = "33"
        ret = execute_request(self.man._targetUrl+"/inbox/list", list_data)
        #print ret
        self.assertEqual(ret["errno"], 0)
        if ret["data"]["msg"]:
            tt = ret["data"]["msg"][0]["msg_type"]
            flag1 = True if tt=="1" or tt=="2" else False
            self.assertEqual(flag1, True)

    def testcase_pop1_0(self):
        "测试用例2：pop接口，参数合法，bduss有效，用户是否未读消息"
        pop_data = {}
        self.tearDownClass()
        pop_data["bduss"] = self.man._bduss
        pop_data["action"] = "fetch"
        pop_data["device"] = "ios"
        pop_data["system_version"] = "9.1"
        pop_data["app_version"] = "4.2"
        pop_data["umask"] = "32"
        #sum = ""
        #for key in fetch_data.keys():
        #    sum += key + "=" + fetch_data[key] + "&"
        #fetchUrl = self.man._passportUrl+"?"+sum[:-1]
        ret = execute_request(self.man._targetUrl+"/inbox/pop", pop_data)
        #print ret


    def testcase_list2_0(self):
        "测试用例3：list接口，参数合法, 拉取删除类消息成功"
        list_data = {}
        self.tearDownClass()
        list_data["bduss"] = self.man._bduss
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.2"
        list_data["umask"] = "32"
        #sum = ""
        #for key in fetch_data.keys():
        #    sum += key + "=" + fetch_data[key] + "&"
        #fetchUrl = self.man._passportUrl+"?"+sum[:-1]
        ret = execute_request(self.man._targetUrl+"/inbox/listdel", list_data)
        #print ret

        if ret['data'] and ret["data"]["msg"]:
            self.assertEqual(ret["data"]["msg"][0]["msg_type"], "2")

    
    def testcase_readMsg1_0(self):
        "测试用例4：readMsg接口，参数合法，标记消息为已读"
        self.tearDownClass()
        set_data = {}
        set_data["bduss"] = self.man._bduss
        set_data["msg_ids"] = "2331"
        set_data["device"] = "ios"
        set_data["system_version"] = "9.1"
        set_data["app_version"] = "4.2"
        set_data["umask"] = "33"
        ret = execute_request(self.man._targetUrl+"/inbox/read", set_data)
        #print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")

    ''' 
    def testcase_addMsg1_0(self):
        "测试用例5：添加消息接口，参数合法，添加点赞消息后在消息列表中就可以看到"
        add_data = {}
        add_data["bduss"] = self.man._bduss
        add_data["umask"] = "33"
        add_data["device"] = "ios"
        add_data["system_version"] = "9.1"
        add_data["app_version"] = "4.2"
        add_data["content"] = random.randint(0,100)
        add_data["tid"] = 1
        add_data["sid"] = 1775
        ret = execute_request(self.man._targetUrl+"/inbox/addMsg", add_data)
        #print " 5  "
        #print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")

        #获取新添加点赞消息的msg id，然后删除该消息
        list_data = {}
        list_data["bduss"] = self.man._bduss
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.2"
        list_data["umask"] = "33"
        retList = execute_request(self.man._targetUrl+"/inbox/list", list_data)
        flag = True if retList["data"]["msg"] else False
        self.assertEqual(flag, True)
        if flag:
            msg_id = ""
            for msg in retList["data"]["msg"]:
                if "%s_%s"%(add_data["tid"], add_data["sid"]) == msg["info"]["id"]:
                    msg_id = msg["msg_id"]
                    break
            flag1 = True if msg_id else False
            self.assertEqual(flag1, True)
            #开始删除消息
            del_data = {}
            del_data["bduss"] = self.man._bduss
            del_data["app_version"] = "3.1"
            del_data["system_version"] = "8.1"
            del_data["msg_ids"] = msg_id
            del_data["device"] = "ios"
            del_data["umask"] = 32
            retDel = execute_request(self.man._targetUrl+"/inbox/delmsg", del_data)
            self.assertEqual(ret["errno"], 0)
            retList1 = execute_request(self.man._targetUrl+"/inbox/list", list_data)
            flag2 = True
            for msg in retList1["data"]["msg"]:
                if msg["msg_id"] == msg_id:
                    flag2 = False
                    break
            self.assertEqual(flag2, True)

    '''

    

if __name__=="__main__":
    unittest.main()
