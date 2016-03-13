#!/home/work/python/bin/python
# -*- coding:utf-8 -*-
'''
监控脚本，监控星座阿拉丁词条前五是否为固定前缀
如果不是立即短信报警
依赖库：
    1. urllib
    2. urllib2
    3. json
    4. ConfigParser
    5. unittest
    6. os

作者：lijingtao@baidu.com
时间：2016-01-26

'''
import urllib
import urllib2
import json
import ConfigParser
import unittest
import os
import logging

from send_sms import cms_monitor


logging.basicConfig(
    level=logging.INFO,
    format=('%(asctime)r %(filename)s[line:%(lineno)d]'
            '%(levelname)s %(message)s'),
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename=os.getcwd() + '/monitor.log',
    filemode='a'
)

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

def is_correct(targetUrl):
    """检查云输入请求中星座阿拉丁词条是否异常"""
    resp = execute_request(targetUrl)
    try:
        if len(resp['data']) == 0:
            return False
        if u'\u904b\u52e2' not in resp['data'][0]['title']:
            return False
        arr_word = resp['data'][0]['candidates']
        if len(arr_word) < 5:
            return False
        if u'\u904b\u52e2' not in arr_word[0]['word']:
            return False
        for i in xrange(1, 5):
            if u'\u4ed5\u4e8b\u904b' not in arr_word[i]['word'] and u'\u7dcf\u5408\u904b' not in arr_word[i]['word'] and u'\u91d1\u904b' not in arr_word[i]['word'] and u'\u604b\u611b\u904b' not in arr_word[i]['word']:
                return False
        return True
    except Exception as e:
        return False

online_url="https://cloud.ime.baidu.jp/py?web=1&version=4.s&api_version=2&ol=1&section=1&switch=0"
#online_url="http://jp01-global-op01.baidu.com:8883/py?web=1&version=4.s&api_version=2&ol=1&section=1&switch=0"
def main():
    """测试特定读音下，云输入请求结果前五候选是否为星座阿拉丁词条"""
    zodiac_file = os.path.join(os.path.dirname(__file__), "zodiac")
    arr_err = []
    with open(zodiac_file) as fopen:
        for line in fopen:
            pron = line.strip()
            android_url = "%s&os=android&py=%s" % (online_url, pron)
            ios_url = "%s&os=ios&py=%s" % (online_url, pron)
            flag1 = is_correct(android_url)
            flag2 = is_correct(ios_url)
            if flag1 == False:
                arr_err.append("%s[%s]" % (pron, 'android'))
            if flag2 == False:
                arr_err.append("%s[%s]" % (pron, 'ios'))
    
    if len(arr_err) > 0:
        a = ",".join(arr_err)
        cont = "云输入星座阿拉丁词条异常[{}]".format(a)
        cms_monitor(cont.decode("utf-8"))
        logging.error(cont)
    else:
        logging.info("星座阿拉丁检查无误")
if __name__=='__main__':
    main()
    exit(0)
