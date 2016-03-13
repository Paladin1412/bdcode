#!/home/work/python/bin/python
# -*- coding:utf-8 -*-
'''
监控脚本，监控地名天气阿拉丁在CMS的redis中是否为第一位候选，并立即短信报警
不是第一位的话立即短信报警
依赖库：
    1. urllib
    2. urllib2
    3. json
	4. ConfigParser
	5. unittest
	6. os

作者：lijingtao@baidu.com
时间：2015-12-18

'''
import urllib
import urllib2
import json
import ConfigParser
import unittest
import os

from send_sms import cms_monitor

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

def setUp():
    config = ConfigParser.ConfigParser()
    config_dir = os.path.join(os.path.dirname(__file__), "conf.ini")
    config.read(config_dir)
    targetUrl = config.get("cms2redis", "targetUrl")
    return targetUrl

def is_top(targetUrl, list_data):
    """检查redis中天气阿拉丁词条异常"""
    resp = execute_request(targetUrl+"/list", list_data)
    try:
        if len(resp['data']) == 0:
            return False
        arr_word = resp['data'][0] 
        if arr_word['comment'] != 'weather aladin' or arr_word['is_cache'] == 1 or arr_word['is_learn'] == 1 or arr_word['type'] != 2 or arr_word['is_top'] != 1 or arr_word['is_righttop'] != 1:
            return False
        return True
    except Exception as e:
        return False


def main():
    """测试case1：检查地名在redis中的候选，天气阿拉丁词条一定是第一位，并检查aladdin的策略是否正确"""
    list_data = {
            "pron":"",
            "device_type":0
            }
    arr_err_pron = []
    targetUrl = setUp()
    with open(os.getcwd() + "/place", 'r') as fopen:
        for line in fopen:
            pron = line.strip()
            list_data['pron'] = pron
            list_data['device_type'] = 1
            flag1 = is_top(targetUrl, list_data)
            list_data['device_type'] = 2
            flag2 = is_top(targetUrl, list_data)
            if False == flag1:
                arr_err_pron.append("(%s,%d)" % (pron, 1))
            if False == flag2:
                arr_err_pron.append("(%s,%d)" % (pron, 2))
        if len(arr_err_pron) != 0:
            errs = ",".join(arr_err_pron)
            cms_monitor(u"CMSredis中天气阿拉丁词条异常[{}]".format(errs.decode('utf-8')))

if __name__=='__main__':
    main()
    exit(0)
