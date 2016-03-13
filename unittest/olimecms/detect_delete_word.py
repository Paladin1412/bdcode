#!/home/work/python/bin/python
# -*- coding:utf-8 -*-
'''
监控脚本，监控数据库中一小时内被删除的词条是否成功失效
如果没有成功失效立即短信报警
依赖库：
    1. urllib
    2. urllib2
    3. json
    4. os
    5. MySQLdb
    6. time
    7. logging
    8. base64

作者：lijingtao@baidu.com
时间：2016-01-15

'''
import urllib
import urllib2
import json
import os
import MySQLdb
import time
import logging
import base64
import time

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
        res = {'errno':'xxx','errmsg':'failed', 'data':[]}
    return res

def queryDB(sql):
    str_msg = ''
    try:
        conn = MySQLdb.connect(host="10.252.29.54", port=3810, db='db_olime', user='root', passwd='baidu@123')
        cur = conn.cursor()
        cur.execute(sql)
        ret_db = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return ret_db
    except MySQLdb.Error as e:
        err_msg = "MySQLdb Error %d: %s" % (e.args[0], e.args[1])
        logging.warning(err_msg)

dict_stategy = {
    "1" : [1, 1, 0, 0],  #white 白名单
    '2' : [0, 0, 1, 1],  #aladdin 阿拉丁
    "3" : [1, 1, 0, 0],  #kaomoji 
    "4" : [1, 0, 0, 0],  #interesting有趣变换
    "5" : [0, 0, 0, 0],  #black 黑名单
    "6" : [1, 1, 0, 0],  #emoji
    "7" : [1, 1, 0, 0]   #cover 精度
    }

targetUrl = "https://cloud.ime.baidu.jp/py?web=1&version=4.4&api_version=2&ol=1&section=1&switch=0"
def is_correct(arr_word):
    str_device_type = str(arr_word[5])
    str_pron = urllib.quote(arr_word[1])
    str_word = arr_word[2]
    param = ''
    if str_device_type == "1":
        param = "&os=android&pron=%s," % str_pron
    elif str_device_type == 2:
        param = "&os=ios&pron=%s," % str_pron
    resp = execute_request(targetUrl + param, {}, 'get')
    try:
        if resp['data']:
            for word in resp['data']['candidates']:
                if base64.encodestring(word['word']) == str_word:
                    return False
        return True
    except Exception as e:
        sys.exit(1)

def main():
    int_now = int(time.time())
    sql = "select * from word_list where status=1 or end_time<%d" % int_now
    ret_db = queryDB(sql)
    logging.info("本次检查被删除的词条数：%d" % len(ret_db))

    arr_msg = []
    for word in ret_db:
        ret_correct = is_correct(word)
        if ret_correct != True:
            arr_msg.append("%d %s" % (word[0], ",".join(ret_correct)))

    if len(arr_msg) != 0 :
        logging.info("wrong num: %d" % len(arr_msg))
        str_msg = ",".join(arr_msg)
        logging.info(str_msg)
        cms_monitor(u"CMS 被删词条错误[{}]，遗留在云输入中，请立即跟进解决".format(str_msg.decode('utf-8')))


if __name__=='__main__':
    main()
    exit(0)
