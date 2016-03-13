#!/home/work/python/bin/python
# -*- coding:utf-8 -*-
'''
监控脚本，监控数据库中一小时内加进来的词条策略是否正确
如果策略不对立即短信报警
依赖库：
    1. urllib
    2. urllib2
    3. json
    4. ConfigParser
    5. os
    6. MySQLdb
    7. time
    8. logging
    9. redis

作者：lijingtao@baidu.com
时间：2015-12-18

'''
import urllib
import urllib2
import json
import ConfigParser
import os
import MySQLdb
import time
import logging
import redis

logging.basicConfig(
    level=logging.INFO,
    format=('%(asctime)r %(filename)s[line:%(lineno)d]'
            '%(levelname)s %(message)s'),
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename=os.getcwd() + '/monitor.log',
    filemode='a'
)


from send_sms import cms_monitor

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

def queryRedis(key):
    #查询CMS 的redis中指定key，返回key对应的字典
    redis_conn = redis.Redis(host="10.252.82.36", port=8379)
    ret = redis_conn.get(key)
    return json.loads(ret)

def is_exist_redis(arr_word):
    #检查词条是否在CMS的redis中
    key = urllib.quote(arr_word[1]) + str(arr_word[5])
    ret_db_redis = queryRedis(key)
    word_id = arr_word[0]
    for word in ret_db_redis:
        if word['id'] == word_id:
            return True
    return False

dict_stategy = {
    #is_cache is_learn is_top is_righttop
    "0" : [0, 0, 0, 0],  #black 黑名单
    "1" : [1, 1, 0, 0],  #white 白名单
    '2' : [0, 0, 1, 1],  #aladdin 阿拉丁
    "3" : [1, 1, 0, 0],  #kaomoji 
    "4" : [1, 0, 0, 0],  #interesting有趣变换
    "5" : [0, 0, 0, 0],  #black 黑名单
    "6" : [1, 1, 0, 0],  #emoji
    "7" : [1, 1, 0, 0]   #cover 精度
    }

def is_correct(arr_word):
    str_type = str(arr_word[10])
    arr_stra = dict_stategy[str_type]
    arr_err = []
    tmp = [str(item) for item in arr_word]
    #print " ".join(tmp)
    if '0' == str_type:
        return True
    if int(arr_word[14]) != arr_stra[0]:
        arr_err.append("is_cache*strategy*wrong")
    if int(arr_word[13]) != arr_stra[1]:
        arr_err.append("is_learn*strategy*wrong")
    if int(arr_word[12]) != arr_stra[2]:
        arr_err.append("is_top*strategy*wrong")
    if int(arr_word[15]) != arr_stra[3]:
        arr_err.append("is_righttop*strategy*wrong")
    if len(arr_err) == 0:
        return True
    return arr_err

def main():
    int_now = int(time.time())
    int_start = int_now - 3600
    sql = "select * from word_list where status=0 and beg_time>%d" % int_start
    ret_db = queryDB(sql)
    logging.info("本次检查词条数：%d" % len(ret_db))

    arr_msg = []
    for word in ret_db:
        ret_correct = is_correct(word)
        if ret_correct != True:
            arr_msg.append("%d%s" % (word[0], ",".join(ret_correct)))
        bol_redis = is_exist_redis(word)
        if bol_redis != True:
            arr_msg.append("%d不在redis中" % (word[0]))

    if len(arr_msg) != 0 :
        logging.info("wrong num: %d" % len(arr_msg))
        str_msg = ",".join(arr_msg)
        logging.info(str_msg)
        #cms_monitor(u"CMS新增词条策略错误[{}]，请立即跟进解决".format(str_msg.decode('utf-8')))


if __name__=='__main__':
    main()
    exit(0)
