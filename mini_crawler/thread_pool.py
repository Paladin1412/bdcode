#/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
线程池模块，提供线程资源

作者: lijingtao@baidu.com
适用版本: python 2.7.x
日期:    2015/10/11 10:28:30
"""
import sys
import threading
import Queue
import datetime
import time
import json
import os


class ThreadPool(object):
    """线程池类
    
    Attributes:
    work_queue: 任务队列
    result_queue: 结果队列
    interval: 爬取网页间隔时间
    threads: 爬虫线程

    """
    def __init__(self, thread_num, func, params, interval):
        """类初始化函数"""

        self.work_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.interval = interval
        self.threads = []
        self.set_work_queue(func, params)
        self.__init_thread_pool(thread_num)

    def __init_thread_pool(self, thread_num):
        """初始化线程池

        Args:
        thread_num: 线程数
        """ 

        for thread in range(thread_num):
            self.threads.append(JobWorker(self.work_queue, self.result_queue, self.interval))

    def set_work_queue(self, func, list_params):
        """设置工作队列

        Args:
        func:        工作线程需要执行的函数
        list_params: 函数所需参数
        """
        for param in list_params:
            self.add_job(func, param)

    def add_job(self, func, param):
        """添加一个工作到工作队列

        Args:
        func:   被执行函数
        param: 被执行函数的参数
        """

        self.work_queue.put((func, param))

    def get_result(self):
        """从结果队列读取一个结果

        Args:
        none
        """

        return self.result_queue.get(block=False)

    def wait_allcomplete(self):
        """等待所有的工作线程结束

        Args:
        none
        """

        for job_thread in self.threads:
            if job_thread.isAlive():
                job_thread.join()


class JobWorker(threading.Thread):
    """爬虫线程

    Attributes:
    work_queue: 任务队列
    interval: 爬虫爬取网页的时间间隔
    result_queue: 结果队列
    """

    def __init__(self, work_queue, result_queue, interval):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.interval = interval
        self.result_queue = result_queue
        self.start()

    def run(self):
        """爬虫线程的爬取逻辑
        死循环，从而让创建的线程在一定条件下关闭退出
        """

        while True:
            try:
                # 从任务队列中获取一个任务进行爬取。如果任务队列为空，则抛出队列空异常，退出爬虫线程
                do, arg = self.work_queue.get(block=False)
                res = do(arg)
                arr = {"url":arg, "html":res}
                res = json.dumps(arr)
                self.result_queue.put(res)
                # 通知系统任务完成
                self.work_queue.task_done()
                time.sleep(self.interval)
            except Queue.Empty as e:
                break
            
