#!/home/work/python/bin/python
# -*- coding:utf-8 -*-
'''
配置文件可以配置新的测试环境
inbox 消息推送

依赖库：
    1. urllib
    2. urllib2
    3. json
    4. ConfigParser
    5. logging
    6. sys
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
import unittest
import os
import MySQLdb
import time
import hashlib
'''
logging.basicConfig(
    level=logging.INFO,
    format=('%(asctime)s %(filename)s[line:%(lineno)d] ' 
        '%(levelname)s %(message)s'),
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='/home/work/lijingtao/regression_test/rtest.log',
    filemode='a'
)
'''

class Params(object):
    """
    被测对象类定义
    """
    # 基础参数
    _app_version     = ''
    _system_version  = ''
    _targetUrl       = ''
    _mobile          = ''
    _country         = ''
    _pwd             = ''
    _action          = ''
    _type            = ''
    _device          = ''
    _bduss           = ''
    _username        = ''
    _sql_host        = ''
    _sql_port        = ''
    _sql_pwd         = ''
    _sql_db_name     = ''
    _sql_table       = ''
    _sql_user        = ''

    def setUserInfo(self, bduss, username):
        """
        设置bduss, username
        """
        self._bduss = bduss
        self._username = username
    def buildParams(self):
        """
        读取conf.ini 初始化参数
        """
        config = ConfigParser.ConfigParser()
        conf_dir = os.path.join(os.path.dirname(__file__),'conf.ini')
        print conf_dir
        config.read(conf_dir)
        self._targetUrl = config.get('params','target_url')
        self._app_version = config.get('params','app_version')
        self._system_version = config.get('params','system_version')
        self._pwd = config.get('params','pwd') 
        self._country = config.get('params','country')
        self._mobile = config.get('params','mobile')
        self._type = config.get('params','type')
        self._device = config.get('params','device')
        self._sql_table = config.get('params','sql_table')
        self._sql_host = config.get('params','sql_host')
        self._sql_port = int(config.get('params','sql_port'))
        self._sql_pwd = config.get('params','sql_pwd')
        self._sql_db_name = config.get('params','sql_db_name')
        self._sql_user = config.get('params','sql_user') 
def execute_request(url='',data={},method='post'):
	if method=='post':
		req = urllib2.Request(url=url,data=urllib.urlencode(data))
	else:
		req = urllib2.Request(url=url)
	try:
		req_data = urllib2.urlopen(req)
		res = json.loads(req_data.read())
	except Exception,e:
		res = {'errno':'xxx','errmsg':'failed'}
	return res

class inboxTestCase(unittest.TestCase):
    """
    测试类定义
    """
    @classmethod
    def setUpClass(self):
        """执行所有用例开始时执行一次"""
        self.man = Params()
        self.man.buildParams()
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['device'] = self.man._device
        login_data['type'] = self.man._type
        login_data['action'] = 'login'
        login_data['mobile'] = self.man._mobile
        login_data['country'] = self.man._country
        login_data['pwd'] = self.man._pwd
        ret = execute_request(self.man._targetUrl+'/mobile',data=login_data, method='post')
        #print ret
        self.man.setUserInfo(ret['data']['bduss'],ret['data']['user_name']) 
        print 'create_connection()....'

    @classmethod
    def tearDownClass(self):
        """执行所有用例后执行一次"""
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['device'] = self.man._device
        login_data['action'] = 'logout'
        login_data['country'] = self.man._country
        login_data['bduss'] = self.man._bduss
        
        ret = execute_request(self.man._targetUrl+'/mobile',data=login_data, method='post')
        print 'connection_destroy()...'

    def setUp(self):
        """用例初始化：每执行一个用例都先执行"""
        print "initing..."

    def tearDown(self):
        """用例环境清理：每执行完一个用例后执行"""
        self.man = None

    def testcase_delMsg1_0(self):
        """测试用例1：删除消息"""
        sql = "select msg_id from msg_box_4 where user_id='1449151043' and status='0' "
        db_ret = self.db_work(sql)
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['msg_id'] = db_ret[0]
        login_data['bduss'] = self.man._bduss
        ret = execute_request(self.man._targetUrl+'/inbox/delmsg', data=login_data, method='post')
        #self.assertEqual(ret['errno'],0)
        print ret['errmsg']
        self.assertEqual(ret['errno'],0)
         
        db = MySQLdb.connect(host=self.man._sql_host,port=self.man._sql_port,user=self.man._sql_user,passwd=self.man._sql_pwd,db=self.man._sql_db_name)
        cursor = db.cursor()
        select_sql = "select status from %s where msg_id='%s'"%(self.man._sql_table, login_data['msg_id'])
        cursor.execute(select_sql)
        data = cursor.fetchone()
        self.assertEqual(data[0], 1)
        db.close()
        self.addMsg()

    def db_work(self, sql):
        db = MySQLdb.connect(host=self.man._sql_host,port=self.man._sql_port,user=self.man._sql_user,passwd=self.man._sql_pwd,db=self.man._sql_db_name)
        cursor = db.cursor()
        #select_sql = "select status from %s where msg_id='%s'"%(self.man._sql_table, login_data['msg_id'])
        cursor.execute(sql)
        data = cursor.fetchone()
        db.close()
        return data

    def addMsg(self):      
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['tid'] = random.randint(1, 20)
        login_data['sid'] = random.randint(1, 20)
        login_data['debug'] = 1
        login_data['bduss'] = self.man._bduss
        ret = execute_request(self.man._targetUrl+'/inbox/list', data=login_data, method='post')
        ret1 = execute_request(self.man._targetUrl+'/inbox/list', data=login_data, method='post')
        #self.assertEqual(ret['errno'],0)
        m = hashlib.md5()
        m.update('1449151043'+'1'+str(login_data['tid'])+str(login_data['sid']))
        ukey = m.hexdigest()
        sql = "select count(1) from msg_box_4 where uniq_key='%s' "%(ukey)
        db_ret = self.db_work(sql)
        print db_ret[0],ukey
        self.assertEqual('1', str(db_ret[0]))
         
    def testcase_getMsgList1_0(self):
        """测试用例2：获取消息列表,参数合法"""
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['type'] = '1'
        login_data['bduss'] = self.man._bduss
        ret = execute_request(self.man._targetUrl+'/inbox/list', data=login_data, method='post')
        #self.assertEqual(ret['errno'],0)
        self.assertEqual(ret['errmsg'],'success')
        self.assertEqual(ret['errno'],0)
        db = MySQLdb.connect(host=self.man._sql_host,port=self.man._sql_port,user=self.man._sql_user,passwd=self.man._sql_pwd,db=self.man._sql_db_name)
        cursor = db.cursor()
        select_sql = "select * from %s where status='0' and msg_type='%s' order by msg_id desc"%(self.man._sql_table, login_data['type'])
        cursor.execute(select_sql)
        data = cursor.fetchall()
        #print data
        flag = True
        for msg1,msg2 in zip(ret['data'],data):
            if msg1['uniq_key'] != msg2[3]:
                #print msg1,msg2[1],msg2[2],str(msg2[3]),msg2[4],str(msg2[5])
                flag = False
                break
        self.assertEqual(flag, True)
        db.close()
        
    def testcase_setMsgRead1_0(self):
        """测试用例3：标记消息已读,参数合法"""
        sql = "select msg_id from msg_box_4 where is_read='%d' and status='%d' "%(0,0)
        db_ret = self.db_work(sql)
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['msg_id'] = db_ret[0] 
        login_data['bduss'] = self.man._bduss
        ret = execute_request(self.man._targetUrl+'/inbox/read', data=login_data, method='post')
        #self.assertEqual(ret['errno'],0)
        self.assertEqual(ret['errmsg'],'success')
        self.assertEqual(ret['errno'],0)
        sql = "select status from msg_box_4 where msg_id='%s' "%db_ret[0]
        db_ret1 = self.db_work(sql)
        self.assertEqual('1',str(db_ret1[0]))
        self.addMsg()
   
    def testcase_popMsg1_0(self):
        """测试用例4：用户是否有未读消息,参数合法"""
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['bduss'] = self.man._bduss
        ret = execute_request(self.man._targetUrl+'/inbox/pop', data=login_data, method='post')
        #self.assertEqual(ret['errno'],0)
        self.assertEqual(ret['errmsg'],'success')
        self.assertEqual(ret['errno'],0)
        
        db = MySQLdb.connect(host=self.man._sql_host,port=self.man._sql_port,user=self.man._sql_user,passwd=self.man._sql_pwd,db=self.man._sql_db_name)
        cursor = db.cursor()
        select_sql = "select count(*) from %s where is_read='%s' and  status='%s' and user_id='%s' "%(self.man._sql_table, '0','0','1449151043')
        cursor.execute(select_sql)
        data = cursor.fetchone()
        self.assertEqual(ret['data'], data[0])


if __name__=='__main__':
    unittest.main()
