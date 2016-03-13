#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
作者：lijingtao@baidu.com
使用版本：python 2.7.6
时间：2015-11-26
更新时间：2016-1-3

"""
import sys
sys.path.append("..")
import os
import unittest
import random
import threading
import time
import datetime
import Queue
import json

from thread_pool import ThreadPool
import log


def test_function(strOutput):
    """测试函数"""
    time.sleep(2)
    print threading.currentThread().getName(), strOutput
    return strOutput


class ThreadPoolTestCase(unittest.TestCase):
    """单元测试类

    Attributes:
    logging: 日志类
    """

    @classmethod
    def setUpClass(self):
        self.logging = log.init_log(os.path.dirname(__file__) + "log/unittest")
        self.logging.info("connection begin...")

    @classmethod
    def tearDownClass(self):
        self.logging.info("connection destroy....")


    def testcase_ThreadPool_set_work_queue_success(self):
        """测试用例1：初始化函数中设置工作队列成功"""
        jobs = [str(i) for i in xrange(2)]
        pool = ThreadPool(2, test_function, jobs, 0)
        while True:
            try:
                func, param = pool.work_queue.get(block=False)
                res = func(param)
                self.assertEqual(str(0), res)
            except Queue.Empty as e:
                self.logging.info(e)
                break
        pool.wait_allcomplete()

    def testcase_ThreadPool_init_thread_pool_success(self):
        """测试用例2：初始化函数中初始化线程池"""
        jobs = [str(i) for i in xrange(2)]
        pool = ThreadPool(3, test_function, jobs, 0)
        thread_count = len(pool.threads)
        self.assertEqual(3, thread_count)
        pool.wait_allcomplete()

    def testcase_ThreadPool_get_result_success(self):
        """测试用例3：get_result，所有任务执行完后结果为1"""
        jobs = [i for i in xrange(2)]
        pool = ThreadPool(3, test_function, jobs, 0)
        pool.wait_allcomplete()
        sum = 0
        while True:
            try:
                res = pool.get_result()
                arr_res = json.loads(res)
                sum += int(arr_res['url'])
            except Queue.Empty as e:
                self.logging.info(e)
                break
        self.assertEqual(1, sum)

if __name__ == "__main__":
    unittest.main()
