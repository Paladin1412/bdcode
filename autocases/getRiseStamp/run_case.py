#! /usr/bin/evn python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
@authors    :   lijingtao<lijingtao@baidu.com>
@copyright  :   baidu
@date       :   2015-08-19
@version    :   1.1.0

"""
import unittest
import json
import urllib2
import urllib
import ConfigParser
import os

class Params(object):
    """
    被测对象类定义
    """
    # 基础参数
    _app_version     = ['2.0', 'thisisaworngcase']
    _device          = ['ios', 'android', 'thisisaworngcase']
    _system_version  = ['ios8.2', 'android10', 'thisisaworngcase']
    _bduss           = ""
    _action           = 'list_rise'
    _from             = 'home'
    _page             = [1,2,3,4,0,-1]
    _targetURL       = ''

    def build_param(self):
        config = ConfigParser.ConfigParser()
        conf_dir = os.path.join(os.path.dirname(__file__),'conf.ini')
        print conf_dir
        config.read(conf_dir)
        self._targetURL = config.get("server", "target_url")
        print self._targetURL

    def set_bduss(self, bduss):
        """
        根据暗绑返回值设置bduss
        """
        self._bduss = bduss

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

def diffStampArray(arrStampPage1, arrStampPage2):
    flag = True
    for i in xrange(len(arrStampPage1)):
        for j in xrange(len(arrStampPage2)):
            if arrStampPage1[i]['id']==arrStampPage2[j]['id']:
                flag = False
                break
    return flag

class getNewStampListTestCase(unittest.TestCase):
    """
    测试类定义
    """

    @classmethod
    def setUpClass(self):
        """执行所有用例开始时执行一次"""
        self.man = Params()
        self.man.build_param()
        print 'create_connection()....'

    @classmethod
    def tearDownClass(self):
        """执行所有用例后执行一次"""
        print 'connection_destroy()...'

    def setUp(self):
        """用例初始化：每执行一个用例都先执行"""
        print "initing..."

    def tearDown(self):
        """用例环境清理：每执行完一个用例后执行"""
        self.man = None

    def testcase_getRiseStampList1_1(self):
        """测试用例1：缺少基础参数app_version"""
        data = {
            'device':self.man._device[0],
            'system_version':self.man._system_version[0],
			'action':self.man._action,
			'page':self.man._page[0],
			'from':''
        }

        ret = execute_request(self.man._targetURL,data)
        self.assertEqual(ret['errmsg'], 'Invalid params')
        self.assertEqual(ret['errno'], 3)
    
    def testcase_getRiseStampList2_1(self):
        """测试用例2：请求飙升stamp列表可以是get请求"""
        data = {
            'app_version':self.man._app_version[0],
            'system_version':self.man._system_version[0],
			'action':self.man._action,
            'device':self.man._device[0],
			'from':'',
			'page':str(self.man._page[0])
        }
        params = '' 
        for key in data.keys():
            params += key + "=" + data[key] + "&"
        ret = execute_request(self.man._targetURL+"?"+params[:-1],method='get')
        self.assertEqual(ret['errmsg'], 'success')
        self.assertEqual(ret['errno'], 0)
    
    def testcase_getRiseStampList3_2(self):
        """测试用例3：请求飙升stamp列表不用检查用户登录"""
        data = {
				'app_version':self.man._app_version[0],
				'system_version':self.man._system_version[0],
				'action':self.man._action,
				'device':self.man._device[0],
				'page':self.man._page[1],
				'from':'',
				'bduss': 'xx112'
				}
        ret = execute_request(url=self.man._targetURL,data=data)
        self.assertEqual(ret['errmsg'], 'success')
        self.assertEqual(ret['errno'], 0)

    def testcase_getRiseStampList4_1(self):
        """测试用例4：page参数不合法。默认返回首页，成功"""
        data = {
            'app_version':self.man._app_version[0],
            'system_version':self.man._system_version[0],
			'action':self.man._action,
            'device':self.man._device[0],
			'page':-1,
			'from':''
        }
        ret = execute_request(self.man._targetURL,data)
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'],'success')
        #self.assertLessEqual(len(ret['data']),28)
        data['page']=1
        ret1 = execute_request(self.man._targetURL,data)
        self.assertEqual(ret['errno'],0)
        self.assertEqual(len(ret['data']),len(ret1['data']))
        flag = True
        for stamp1,stamp2 in zip(ret['data'],ret1['data']):
            if stamp1['id']!=stamp2['id']:
                print stamp1['id'],stamp2['id']
                flag = False
        self.assertEqual(flag,True)
	
    def testcase_getRiseStampList5_0(self):
        """测试用例5：from参数为home，page参数不起作用，返回不多与8个stamp的列表"""
        data = {
            'app_version':self.man._app_version[0],
            'system_version':self.man._system_version[0],
			'action':self.man._action,
            'device':self.man._device[0],
			'from':'home'
        }
        ret = execute_request(self.man._targetURL,data)
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'],'success')
        self.assertLessEqual(len(ret['data']),16)
	
    def testcase_getRiseStampList6_0(self):
        """测试用例6：参数合法"""
        data = {
            'app_version':self.man._app_version[0],
            'system_version':self.man._system_version[0],
			'action':self.man._action,
            'device':self.man._device[0],
			'from':'',
			'page':self.man._page[0]
        }
        ret = execute_request(self.man._targetURL,data)
        self.assertEqual(ret['errno'], 0)
        self.assertEqual(ret['errmsg'],'success')
        self.assertLessEqual(len(ret['data']),28)
        
        baseURL = self.man._targetURL[0:self.man._targetURL.index("passport")-1]
        cmsURL = "%s/passport/stamp/cms/listStamp?view_type=8&workplace=7&page_plex=1"%("http://simeji.baidu.com")
        cmsRet = execute_request(cmsURL)
        flag = True
        #print ret['data'], cmsRet["data"]
        for stamp1,stamp2 in zip(ret['data'], cmsRet['data']['list']):
            if stamp1["id"] != "%s_%s"%(stamp2['tid'], stamp2['sid']):
                flag = False
                break
        self.assertEqual(flag, True)
        self.assertEqual(len(ret['data']), len(cmsRet['data']['list']))

if __name__ == "__main__":
    unittest.main()
