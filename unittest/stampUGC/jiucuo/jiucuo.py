#!/usr/bin/python
# -*- coding:utf-8 -*-
# Author : lijingtao@baidu.com



'''
该脚本主要是对日志上报服务是否正常

依赖库：
    1. urllib
    2. urllib2
    3. json
    4. ConfigParser
    5. logging
    6. sys
    7. monitor
作者：lijingtao@baidu.com
时间：2015-08-12

'''
import random
import sys
import urllib
import urllib2
import json
import ConfigParser
import logging
import Monitor
import os
import time

logging.basicConfig(
    level=logging.INFO,
    format=('%(asctime)s %(filename)s[line:%(lineno)d] ' 
        '%(levelname)s %(message)s'),
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='/home/work/lijingtao/monitor_script/online_monitor/jiucuo/monitor.log',
    filemode='a'
)


tmp_file ='/home/work/lijingtao/monitor_script/online_monitor/jiucuo/test.file'
def wget(ip, log_path):
    cmd = "wget --limit-rate=25M -O %s ftp://%s%s"%(tmp_file, ip, log_path)
    ls_cmd = "ls -lah %s |awk '{print $5}'"%tmp_file
    ret = os.popen(cmd).readlines()
    ret1 = os.popen(ls_cmd).readlines()
    print ret1[-1].strip()
    flag = True
    if "0" == ret1[-1].strip():
        flag = False
        return flag
    else:
        cmd = "rm -r %s"%tmp_file
        os.popen(cmd)
        return flag
              
   

def main():
    #str_time = "2015-09-26"
    str_time = time.strftime("%Y-%m-%d")
    config = ConfigParser.ConfigParser()
    conf_dir = os.path.join(os.path.dirname(__file__),'conf.ini')
    config.read(conf_dir)

    ips                 = config.get("log", 'ips')
    jiucuo_android_path = config.get("log", 'jc_android_path')
    jiucuo_ios_path     = config.get('log', 'jc_ios_path')
    wordLog_ios_path    = config.get('log', 'wl_ios_path')
  
    msg    = ""
    arr_ip = ips.split("||")

    for ip in arr_ip:
        flag = wget(ip, jiucuo_android_path+str_time+'.log')

        if False == flag:
            msg += "%s : %s.log  no such file \n"%(ip, jiucuo_android_path+str_time)
  
        flag = wget(ip, jiucuo_ios_path+str_time+'.log')

        if False == flag:
            msg += "%s : %s.log  no such file \n"%(ip, jiucuo_ios_path+str_time)
        
        flag = wget(ip, wordLog_ios_path+str_time+'.log')

        if False == flag:
            msg += "%s : %s.log  no such file \n"%(ip, wordLog_ios_path+str_time)
        
    monitor = Monitor.Monitor() 
    if msg:
        monitor.data_to_monitor(msg, '', '')
    else:
        logging.info('logsession is ok')

if __name__=='__main__':
    main()
