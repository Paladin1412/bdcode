#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
作者：lijingtao@baidu.com
使用版本：python 2.7.x
时间：2015-11-26

"""
import sys
sys.path.append("..")
import os
import unittest
import re

from mini_crawler import Crawler
from mini_crawler import init_log

class MiniCrawlerTestCase(unittest.TestCase):
    """mini_crawler单元测试类

    Attributes:
    crawler: 爬虫类
    logging: 日志类
    """

    @classmethod
    def setUpClass(self):
        current_dir = os.path.dirname(__file__)
        self.logging = init_log(current_dir + "log/unittest")
        self.crawler = Crawler()
        self.crawler.build_params(current_dir + "test_conf.ini")
        self.logging.info("connection begin...")

    @classmethod
    def tearDownClass(self):
        self.logging.info("connection destroy....")

    def test_crawl_html_pass(self):
        """测试用例1：crawl_html测试爬虫爬去网页函数，url合法，抓去成功"""
        test_url = "http://www.sina.com.cn"
        res = self.crawler.crawl_html(test_url)
        self.assertNotEqual(res, "")

    def test_crawl_html_fail(self):
        """测试用例2：crawl_html测试爬虫爬去网页函数，url非法，抓取失败"""
        test_url = "http://www.sinaxxx.com.cn"
        res = self.crawler.crawl_html(test_url)
        self.assertEqual(res, "")

    def test_filter_unvisited_url_pass(self):
        """测试用例3：filter_unvisited_url 过滤已访问过的url"""
        self.crawler.visited_url["http://www.baidu.com"] = 1
        test_url_list = ["http://www.baidu.com"]
        res = self.crawler.filter_unvisited_url(test_url_list, self.crawler.visited_url)
        self.assertEqual([], res)

    def test_save_file_pass(self):
        """测试用例4：保存文件到本地文件目录，url合法，保存成功"""
        target_url = "http://pic14.nipic.com/20110522/7411759_164157418126_2.jpg"
        self.crawler.save_file(target_url)
        file_name = target_url.replace("/", "_")
        flag = os.path.exists("%s/%s" % (self.crawler.params['output_directory'], file_name))
        self.assertEqual(flag, True)

    def test_save_file_fail(self):
        """测试用例5：保存文件到本地文件目录， url非法，保存失败"""
        target_url = "http://pic14.nipic.com/20110522/7411759_164157418126_2.jpg.not.valid"
        res = self.crawler.save_file(target_url)
        self.assertEqual(res, None)

    def test_parse_html_pass(self):
        """测试用例6：解析网页内容，并返回网页中所有的url链接，和符合正则表达式的结果链接，处理相对连接和绝对连接"""
        target_url = "http://www.sina.com.cn"
        res = self.crawler.crawl_html(target_url)
        target_url = self.crawler.params['target_url']
        parse_url_set = self.crawler.parse_html(target_url, res, target_url)
        next_url = parse_url_set[0]
        js_url = parse_url_set[1]
        ret_url = parse_url_set[2]
        flag1 = True
        if next_url:
            for url in next_url:
                if url.startswith('/'):
                    flag1 = False
        flag2 = True
        if js_url:
            for url in js_url:
                if not url.endswith("js"):
                    flag2 = False
        flag3 = True
        if ret_url:
            for url in ret_url:
                m = re.match(self.crawler.params['target_url'], url)
                if not m:
                    flag3 = False
        print flag1, flag2, flag3
        self.assertEqual(flag1 and flag2 and flag3, True) 

if __name__ == "__main__":
    unittest.main()
