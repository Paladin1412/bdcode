#!/usr/bin/python
# -*- coding:utf-8 -*-
# Author : lijingtao@baidu.com



'''
该脚本主要是对线上stamp功能进行监控
主要有中国手机号码登录、登录、
获取我的stamp列表、获取最新stamp列表、
获取最热列表、获取上传stamp的token
配置文件可以配置不同的测试环境

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
import MySQLdb
import time

logging.basicConfig(
    level=logging.INFO,
    format=('%(asctime)s %(filename)s[line:%(lineno)d] ' 
        '%(levelname)s %(message)s'),
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='/home/work/rd.bak/ljt/unittest/stampUGC/monitor.log',
    filemode='a'
)


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

def diffStampList(arrStampPage1,arrStampPage2):
    flag = True
    for i in xrange(len(arrStampPage1)):
        for j in xrange(len(arrStampPage2)):
            if arrStampPage1[i]['id']==arrStampPage2[j]['id']:
                flag = False
                break
    return flag

monitor = Monitor.Monitor()


class userCenterTest():
    """
    测试类定义
    """
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
        '''
        pp = ''
        for key in report_data:
            pp += key+'='+login_data[key]+'&'
        '''
        ret = execute_request(self.man._targetUrl+'/mobile',data=login_data, method='post')
        if ret['errno']==0:
            logging.info('登陆成功')
        else:
            logging.error('中国手机号码登录失败')
            print ret
            monitor.data_to_monitor('中国手机号码登录失败',self.man._targetUrl+'/mobile','')
            exit(1)
        self.man.setUserInfo(ret['data']['bduss'],ret['data']['user_name']) 
        print 'create_connection()....'

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
        if ret['errno']==0:
            logging.info('登出成功')
        else:
            logging.error('中国手机号码登出失败!')
            monitor.data_to_monitor('中国手机号码登出失败',self.man._targetUrl+'/mobile','')
            exit(1)
        print 'connection_destroy()...'


    def updateUsername(self):
        """测试用例1：修改用户昵称"""
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['device'] = self.man._device
        login_data['action'] = 'name'
        login_data['name'] = 'ayue'+str(random.randrange(0,999))
        login_data['bduss'] = self.man._bduss
        ret = execute_request(self.man._targetUrl+'/user', data=login_data, method='post')
        #self.assertEqual(ret['errno'],0)
        print ret['errmsg']
        if ret['errno']==0:
            logging.info('修改用户昵称成功')
        else:
            logging.error('修改用户昵称失败')
            monitor.data_to_monitor("修改用户昵称失败",self.man._targetUrl+'/user','')
            exit(1)
        ''' 
        db = MySQLdb.connect(host=self.man._sql_host,port=self.man._sql_port,user=self.man._sql_user,passwd=self.man._sql_pwd,db=self.man._sql_db_name)
        cursor = db.cursor()
        select_sql = "select user_name from %s where user_id='%s'"%(self.man._sql_table, '1440510610')
        cursor.execute(select_sql)
        data = cursor.fetchone()
        if data[0] == login_data['name']:
            logging.info(" 修改昵称后与数据库内昵称一致 ")
        else:
            msg = " 修改昵称后对应user数据库表中昵称不一致 "
            monitor.data_to_monitor(msg,self.man._targetUrl+'/user','')
            exit(1)
        db.close() 
        db = MySQLdb.connect(host=self.man._sql_host,port=self.man._sql_port,user=self.man._sql_user,passwd=self.man._sql_pwd,db="db_simeji_skin_ugc")
        cursor = db.cursor()
        select_sql = "select uploader from %s where user_id='%s'"%("user_skin_1",'1440510610')
        cursor.execute(select_sql)
        data = cursor.fetchone()
        if data:
            if data[0] == login_data['name']:
                logging.info('修改昵称后，对应的skin详情中uploader昵称一致')
            else:
                msg = '修改昵称后，对应的skin详情中uploader昵称不一致' 
                logging.info(msg)
                monitor.data_to_monitor(msg,self.man._targetUrl+'/user','')
                exit(1)
        else:
            logging.info('该用户没有skin数据')
        db.close()
        '''
   
    def uploadAuth(self):
        """测试用例2：获取上传stamp的token"""
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['device'] = self.man._device
        login_data['action'] = 'upload_auth'
        login_data['bduss'] = self.man._bduss
        ret = execute_request(self.man._targetUrl+'/stamp/stamp', data=login_data, method='post')
        #self.assertEqual(ret['errno'],0)
        print ret['errmsg']
        if ret['errno'] == 0:
            logging.info('获取上传stamp的token成功')
        else:
            msg = '获取上传stamp的token失败'
            logging.error(msg)
            monitor.data_to_monitor(msg,self.man._targetUrl+'/stamp/stamp','')
            exit(1)

    def getNewStampList(self):
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['device'] = self.man._device
        login_data['action'] = 'list_new'
        login_data['page'] = 1

        ret1 = execute_request(self.man._targetUrl+'/stamp/stamp',data=login_data,method='post')
        if ret1['errno']==0:
            logging.info('获取最新列表首页成功')
        else:
            msg = '获取最新列表失败'
            logging.error(msg)
            monitor.data_to_monitor(msg,self.man._targetUrl+'/stamp/stamp','')
            exit(1)
        login_data['last_id'] = ret1['data'][-1]['id']
        print login_data['last_id']
        ret2 = execute_request(self.man._targetUrl+'/stamp/stamp',data=login_data,method='post')
        if ret2['errno']==0:
            logging.info('根据last_id获取最新列表第二页成功')
        else:
            msg = '根据last_id获取最新列表第二页失败'
            logging.error(msg)
            monitor.data_to_monitor(self.man._targetUrl+'/stamp/stamp',msg,'')
            exit(1)
        ff = diffStampList(ret1['data'],ret2['data'])
        if ff:
            logging.info('根据last_id标示请求最新第二页，与第一页stamp不重复')
        else:
            msg = '根据last_id标示请求最新第二页，与第一页stamp失败，last_id失效'
            logging.error(msg)
            monitor.data_to_monitor(msg, self.man._targetUrl+'/stamp/stamp','')
            exit(1)
        
    def getHotStampList(self):
        login_data = {}
        login_data['system_version'] = self.man._system_version
        login_data['app_version'] = self.man._app_version
        login_data['device'] = self.man._device
        login_data['action'] = 'list_hot'
        login_data['page'] = 1

        ret1 = execute_request(self.man._targetUrl+'/stamp/stamp',data=login_data,method='post')
        if ret1['errno']==0:
            logging.info('获取最热列表首页成功')
        else:
            msg = '获取最热列表首页失败'
            logging.info(msg)
            monitor.data_to_monitor(self.man._targetUrl+'/stamp/stamp',msg,'')
            exit(1)
        login_data['last_id'] = ret1['data'][-1]['id']
        print login_data['last_id']
        ret2 = execute_request(self.man._targetUrl+'/stamp/stamp',data=login_data,method='post')
        if ret2['errno']==0:
            logging.info('根据last_id获取最热列表第二页成功')
        else:
            msg = '根据last_id获取最热列表第二页失败'
            logging.error(msg)
            monitor.data_to_monitor(msg, self.man._targetUrl+'/stamp/stamp','')
            exit(1)
        ff = diffStampList(ret1['data'],ret2['data'])
        if ff:
            logging.info('根据last_id标示请求最热第二页，与第一页stamp不重复')
        else:
            msg = '根据last_id标示请求最热第二页，与第一页stamp失败，last_id失效'
            logging.error(msg)
            monitor.data_to_monitor(msg, self.man._targetUrl+'/stamp/stamp','')
            exit(1)

if __name__=='__main__':
    u = userCenterTest()
    logging.info('*********************')
    u.setUpClass()
    u.updateUsername()
    u.uploadAuth()
    u.getNewStampList()
    u.getHotStampList()
    u.tearDownClass()
    logging.info('-------------end------------')
