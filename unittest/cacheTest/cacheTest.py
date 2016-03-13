# -*- utf-8 -*-

import ConfigParser
import os
import sys
import urllib2
import urllib

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


def cacheTest(log_path, action, req_url):
    cmd = 'tail -n 100 %s | grep action=%s ' % (log_path, action)
    #lines = os.system(cmd).readlines()
    #print lines
    for i in xrange(10):
        execute_request(req_url)
    lines = os.popen(cmd).readlines()
    print '\n'.join(lines)


if __name__=='__main__':
    config = ConfigParser.ConfigParser()
    config_dir = os.path.join(os.path.dirname(__file__), "conf.ini")
    config.read(config_dir)
    req_url = config.get("cacheTest", "req_url") 
    log_path = config.get("cacheTest", "log_path") 
    action = config.get("cacheTest", "action") 
    cacheTest(log_path, action, req_url)


