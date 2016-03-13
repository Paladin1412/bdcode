#!/usr/bin/python
# -*- coding:utf-8 -*-
# Author : lizeyang01@baidu.com

import time
import json
import urllib
import urllib2
import hashlib

class Monitor():
    def __init__(self):
        self.remote_server = "http://monitor.baidu.com:8088/monitor/apiproxy"
        # 参数根据业务线来定
        self.configId = "901"
        self.uname = "nbg_international_japanese_input_method"
        self.sk = "nbg_international_japanese_input_method"

    def data_to_monitor(self,msg,deadlink,seq):
        self.msg = msg
        self.deadlink = deadlink
        self.seq = seq

        self.timestamp = int(time.time())
        self.param =  self.uname + str(self.timestamp) + self.sk
        self.accessToken = hashlib.md5(self.param.encode('utf-8')).hexdigest()

        self.data = {
            "uname":self.uname,
            "timeStamp":self.timestamp,
            "accessToken":self.accessToken,
            "monitorType":10,
            "op":7,
            "sk":self.sk,
            "configId":self.configId,
            "alarmContent[alarmMessage]":"API_Monitor alarm message:" + self.msg + " sequence:" + self.seq,
            "alarmContent[alarmReceiver]":"lijingtao",
            "alarmContent[monitorLevel]":2,
            "alarmContent[pageUrl]":self.deadlink
            }
        self.params = urllib.urlencode(self.data)
        self.requestUrl = self.remote_server + "?" + self.params
        self.req = urllib2.Request(self.requestUrl)
        self.res_data = urllib2.urlopen(self.req)
        self.res = self.res_data.read()
        #print self.res
