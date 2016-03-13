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
        self._targetUrl = config.get("twitter", "targetUrl")
        #self._configUrl = config.get("twitter", "configUrl")
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
    #print res
    return res


def dup_two_page(arrFirstPage, arrSecPage):
    flag = True
    for i in xrange(len(arrFirstPage)):
        for j in xrange(len(arrSecPage)):
            if arrFirstPage[i]['tweet_id'] == arrSecPage[j]['tweet_id']:
                flag = False
    return flag

def dup_one_page(arrTweet):
    dd = {}
    for i in xrange(len(arrTweet)):
        tweet_id = arrTweet[i]['tweet_id']
        if tweet_id in dd:
            return False
        else:
            dd[tweet_id] = 1
    return True

class twitterTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.man = Param()
        self.man.buildParam()
        print "connection begin..."

    @classmethod
    def tearDownClass(self):
        print "connection destroy...."

    def testcase_getTopic1_0(self):
        "测试用例1 : 获取话题，根据话题获取对应的推文，iOS"
        list_data = {}
        list_data["device"] = "ios"
        list_data["system_version"] = "9.1"
        list_data["app_version"] = "4.2"
        ret = execute_request("%s/%s/query"%(self.man._targetUrl, list_data["device"]), list_data)
        #print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")

        if ret['data']:
            #print ret
            for topic in ret['data']:
                url = "%s/%s/getTweet"%(self.man._targetUrl, list_data['device'])
                list_data['topic_id'] = topic['topic_id']
                list_data['vendor_id'] = 'auto_test'
                resTweet = execute_request(url, list_data)

                self.assertEqual(resTweet['errno'], 0)
                self.assertEqual(resTweet['errmsg'], 'success')
                self.assertLessEqual(len(resTweet['data']), 7)
                ff = dup_one_page(resTweet['data'])
                self.assertEqual(True, ff)

    def testcase_keyWord2_0(self):
        "测试用例2：获取话题，命中关键字服务，android"
        list_data = {}
        list_data["device"] = "android"
        #list_data["system_version"] = "9.1"
        #list_data["app_version"] = "4.2"
        ret = execute_request("%s/%s/query"%(self.man._targetUrl, list_data["device"]), list_data)
        #print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")
        self.assertLessEqual(len(ret['data']), 20)

    def testcase_getTopic3_0(self):
        "测试用例3：获取话题，根据话题获取推文，android"
        list_data = {}
        list_data["device"] = "android"
        list_data["system_version"] = "5.3"
        list_data["app_version"] = "9.1"
        ret = execute_request("%s/%s/query"%(self.man._targetUrl, list_data["device"]), list_data)
        #print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")

        if ret['data']:
            #print ret
            for topic in ret['data']:
                url = "%s/%s/getTweet"%(self.man._targetUrl, list_data['device'])
                list_data['topic_id'] = topic['topic_id']
                list_data['vendor_id'] = 'auto_test'
                resTweet = execute_request(url, list_data)
                self.assertEqual(resTweet['errno'], 0)
                self.assertEqual(resTweet['errmsg'], 'success')
                self.assertLessEqual(len(resTweet['data']), 7)
                ff = dup_one_page(resTweet['data'])
                self.assertEqual(True, ff)

    def testcase_getTopic4_0(self):
        "测试用例4：获取话题，根据话题获取推文，android"
        list_data = {}
        list_data["device"] = "android"
        list_data["system_version"] = "5.3"
        list_data["app_version"] = "9.1"
        ret = execute_request("%s/%s/querytopic"%(self.man._targetUrl, list_data["device"]), list_data)
        #print ret
        self.assertEqual(ret["errno"], 0)
        self.assertEqual(ret["errmsg"], "success")

        if ret['data']:
            for topic in ret['data']:
                url = "%s/%s/getTweet"%(self.man._targetUrl, list_data['device'])
                list_data['topic_id'] = topic['topic_id']
                list_data['vendor_id'] = 'auto_test'
                resTweet = execute_request(url, list_data)
                self.assertEqual(resTweet['errno'], 0)
                self.assertEqual(resTweet['errmsg'], 'success')
                #print resTweet['data']
                self.assertLessEqual(len(resTweet['data']), 7)
                ff = dup_one_page(resTweet['data'])
                self.assertEqual(True, ff)

                if resTweet['data']:
                    print topic['topic_id']
                    create_at = resTweet['data'][-1]['create_at']
                    retweet_ids = []
                    retweet_ids.append(resTweet['data'][0]['tweet_id'])
                    if len(resTweet['data']) > 1:
                        retweet_ids.append(resTweet['data'][1]['tweet_id'])
                    list_data['create_at'] = create_at
                    list_data['retweet_ids'] = ','.join(retweet_ids)
                    retSecondPage = execute_request(url, list_data)
                    self.assertEqual(0, retSecondPage['errno'])
                    self.assertEqual('success', retSecondPage['errmsg'])
                    print len(retSecondPage['data'])
                    self.assertLessEqual(len(retSecondPage['data']), 10)
                    fff =  dup_one_page(retSecondPage['data'])
                    ffff = dup_two_page(resTweet['data'], retSecondPage['data'])
                    self.assertEqual(True, fff)
                    self.assertEqual(True, ffff)
                list_data['create_at'] = ""

if __name__=="__main__":
    unittest.main()
