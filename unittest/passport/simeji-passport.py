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

import urllib
import urllib2
import json
import Monitor
import logging


logging.basicConfig(
    level=logging.INFO,
    format=('%(asctime)s %(filename)s[line:%(lineno)d] ' 
        '%(levelname)s %(message)s'),
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='/home/work/rd.bak/lizeyang/monitor_script/monitor.log',
    filemode='a'
)

monitor = Monitor.Monitor()

exit(0)

############################################
# 高级云服务sectbind接口 
############################################
sectbindUrl = "http://jp01-ime-odp02.jp01.baidu.com:8000/passport/sectbind"

sectbindData = {
    "app_version": 2,
    "system_version": "ios8.4",
    "device": "ios",
    "type": "facebook",
    "osid": "1421131934858850",
    "token": ("CAAIKt5bWDDQBAKJdwslvJXCzi4ZA8hFjGFqbQ9ZAZCy"
        "2HLtzDUWCYWmJoT6JXVnt7IsLCmc5eIrPqwFoyOSvdNNxyNsX"
        "Y5ZBcEmEYpLd0isuzxF0a1rQA1jULGmotli9ZBaxByPqO6ZCI"
        "O9S7ezs3tWvDXGrZAQpZAhaaV8cJ4t0QLpa8p0IsZAwxXl92v"
        "gXyav1M5jlF30QimRLFuiHPWVBM"),
    "user_name": "Gibbon Zhuo",
    "user_portrait": "https://graph.facebook.com/1421131934858850/picture?type=large",
    "tmd5": "805bc2d55c1d9bb7bfe386d7df9fe671"
}

req = urllib2.Request(url=sectbindUrl,data=urllib.urlencode(sectbindData))

try:
    req_data = urllib2.urlopen(req, timeout=3)
except Exception as e:
    logging.error(e)
    monitor.data_to_monitor(str(e),sectbindUrl,"no")
    exit(1)
res = json.loads(req_data.read())

if res.has_key('errmsg') and res.has_key('errno'):
    if res['errmsg'] == "success" and res['errno'] == 0:
        logging.info(res)
    else:
        logging.info(res)
        exit(1)
        monitor.data_to_monitor(str(res),sectbindUrl,"")
else:
    loggin.info(res)
    exit(1)
    monitor.data_to_monitor(str(res),sectbindUrl,"")

bduss = res['data']['bduss']



############################################
# 高级云服务push接口 
############################################
pushUrl = "https://stat.ime.baidu.jp/passport/user"

pushData = {
    "app_version": 2,
    "system_version": "ios8.4",
    "device": "ios",
    "type": "facebook",
    "bduss": bduss,
    "field": "u",
    "conf": "{'dict_1':0,'dict_2':1,'dict_3':0}",
    "action": "push"
}

req = urllib2.Request(url=pushUrl,data=urllib.urlencode(pushData))

try:
    req_data = urllib2.urlopen(req, timeout=5)
except Exception as e:
    logging.error(e)
    monitor.data_to_monitor(str(e),pushUrl,"no")
    exit(1)
res = json.loads(req_data.read())

if res.has_key('errmsg') and res.has_key('errno'):
    if res['errmsg'] == "success" and res['errno'] == 0:
        logging.info(res)
    else:
        monitor.data_to_monitor(str(res),pushUrl,"")
else:
    monitor.data_to_monitor(str(res),pushUrl,"")


############################################
# 高级云服务fetch接口 
############################################
fetchUrl = "https://stat.ime.baidu.jp/passport/user"

fetchData = {
    "app_version": 2,
    "system_version": "ios8.4",
    "device": "ios",
    "type": "facebook",
    "bduss": bduss,
    "mask": 1,
    "action": "fetch"
}

req = urllib2.Request(url=fetchUrl,data=urllib.urlencode(fetchData))

try:
    req_data = urllib2.urlopen(req, timeout=5)
except Exception as e:
    logging.error(e)
    monitor.data_to_monitor(str(e),fetchUrl,"no")
    exit(1)
res = json.loads(req_data.read())

if res.has_key('errmsg') and res.has_key('errno'):
    if res['errmsg'] == "success" and res['errno'] == 0:
        logging.info(res)
    else:
        monitor.data_to_monitor(str(res),fetchUrl,"")
else:
    monitor.data_to_monitor(str(res),fetchUrl,"")



############################################
# 高级云服务list接口 
############################################
listUrl = "https://stat.ime.baidu.jp/passport/user"

listData = {
    "device": "android",
    "app_version": 1,
    "type": "facebook",
    "system_version": 4,
    "bduss": bduss,
    "action": "wlist",
    "mask": 8
}

req = urllib2.Request(url=listUrl,data=urllib.urlencode(listData))

try:
    req_data = urllib2.urlopen(req, timeout=5)
except Exception as e:
    logging.error(e)
    monitor.data_to_monitor(str(e),listUrl,"no")
    exit(1)
res = json.loads(req_data.read())

# print res
if res.has_key('errmsg') and res.has_key('errno'):
    if res['errmsg'] == "success" and res['errno'] == 0:
        logging.info(res)
    else:
        monitor.data_to_monitor(str(res),listUrl,"")
else:
    monitor.data_to_monitor(str(res),listUrl,"")


############################################
# 高级云服务logout接口 
############################################
logoutUrl = "https://stat.ime.baidu.jp/passport/logout"
logoutData = {"bduss":bduss}
req = urllib2.Request(url=logoutUrl,data=urllib.urlencode(logoutData))
try:
    req_data = urllib2.urlopen(req, timeout=3)
except Exception as e:
    logging.error(e)
    monitor.data_to_monitor(str(e),sectbindUrl,"no")
    exit(1)

res = json.loads(req_data.read())
# print res
if res.has_key('errmsg') and res.has_key('errno'):
    if res['errmsg'] == "success" and res['errno'] == 0:
        logging.info(res)
    else:
        monitor.data_to_monitor(str(res),logoutUrl,"")
else:
    monitor.data_to_monitor(str(res),logoutUrl,"")

exit(0)
