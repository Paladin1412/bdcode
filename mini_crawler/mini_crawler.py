#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
爬虫主程序，通过线程池的线程实现多线程爬取网页

适用版本：python 2.7.6
作者: lijingtao(lijingtao@baidu.com)
开始日期: 2015/10/11 10:28:30
修改日期: 2015/12/05 10:58:23
"""

import sys
import os
import ConfigParser
import urllib2
import re
import socket
import Queue
import json

import chardet
from bs4 import BeautifulSoup

from thread_pool import ThreadPool
import log


class Crawler(object):
    """爬虫类，主要的爬虫逻辑都在这里

    Attributes:
    params: 配置文件字典
    visited_url: 已访问过的url集合
    target_visited_url: 已访问过的目标url集合
    unvisited_url: 未访问过的url集合
    count: 最大抓取的目标url数目
    AGENT: 爬虫请求头部常量
    """

    def __init__(self):
        # 初始化函数，主要是初始化爬虫一些主要参数
        self.params = {}
        self.visited_url = {}
        self.target_visited_url = {}
        self.unvisited_url = {}
        self.count = 0
        self.AGENT = ('Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.1.6)'
                      'Gecko/20091201 Firefox/3.5.6')

    def build_params(self, conf):
        """从配置文件中读取爬虫配置

        Args:
        conf: 配置文件

        Returns:
        bool True: 读取配置文件初始化爬虫参数成功
        bool False: 初始化爬虫参数失败
        """
        try:
            # 根据配置文件初始化参数
            config = ConfigParser.ConfigParser()
            config.read(conf)
            self.params['url_list_file'] = config.get("spider", "url_list_file")
            self.params['output_directory'] = config.get("spider", "output_directory")
            self.params['max_depth'] = int(config.get("spider", "max_depth"))
            self.params['crawl_interval'] = float(config.get("spider", "crawl_interval"))
            self.params['crawl_timeout'] = float(config.get("spider", "crawl_timeout"))
            self.params['target_url'] = config.get("spider", "target_url")
            self.params['thread_count'] = int(config.get("spider", "thread_count"))
            self.params['target_count'] = int(config.get("spider", "target_count"))
            logging.info("init params from %s" % conf)
            return True
        except ConfigParser.NoSectionError as e:
            logging.error(e)
            return False
        except ConfigParser.ParsingError as e:
            logging.error(e)
            return False

    def crawl_html(self, url):
        """爬取网页函数

        Args:
        url: 目标url

        Returns
        str_html: 网页内容
        """
        headers = {}
        headers['User-Agent'] = self.AGENT
        req = urllib2.Request(url, headers=headers)
        str_html = ""
        try:
            str_ret = urllib2.urlopen(req).read()
            self.visited_url[url] = 1
            logging.info("%s 抓取成功" % str(url))
        except socket.timeout as e:
            logging.warning(e)
            return str_html
        except urllib2.URLError as e:
            logging.warning(e)
            return str_html
        except ValueError as e:
            logging.warning(e)
            return str_html
        except urllib2.SSLError as e:
            logging.warning(e)
            return str_html
        # gb2312问题，利用gbk来转
        try:
            enc = chardet.detect(str_ret)["encoding"]
            if "gb" in enc:
                str_html = str_ret.decode("gb2312").encode("utf8")
            else:
                str_html = str_ret.decode(enc).encode('utf8')
        except UnicodeDecodeError as e:
            logging.warning(e)
            return ""
        except UnicodeEncodeError as e:
            logging.warning(e)
            return ""
        except TypeError as e:
            logging.warning(e)
            return ""
        return str_html

    @staticmethod
    def filter_unvisited_url(source_url, target_url):
        """过滤已经访问过的url

        Args:
        source_url：待抓取的url集合
        target_url：成员对象中的visited_url和target_visited_url

        Returns:
        arr_new_url：未访问过的url集合
        """
        arr_new_url = []
        dict_new_url = {}
        for url in source_url:
            if url in target_url.keys():
                #这里是过滤source_url中已经被抓取过的url，保证不抓取已访问过的url
                logging.info("filter success %s" % str(url))
                continue
            elif url not in dict_new_url.keys():
                #这里是过滤source_url中相同的url，保证未抓取的url不会重复抓取
                arr_new_url.append(url)
                dict_new_url[url] = 1
        return arr_new_url

    def save_file(self, url):
        """保存目标网页到本地

        Args:
        url: 目标网页地址

        Returns:
        none

        """
        headers = {}
        headers['User-Agent'] = self.AGENT
        req = urllib2.Request(url, headers=headers)
        filename = url.replace('/', '_')
        try:
            str_ret = urllib2.urlopen(req).read()
            with open("%s/%s" % (self.params['output_directory'], filename), "wb") as fout:
                fout.write(str_ret)
            self.target_visited_url[url] = 1
            logging.info("%s 保存成功" % str(url))
            self.count += 1
        except ValueError as e:
            logging.warning(e)
            return
        except socket.timeout as e:
            logging.warning(e)
            return
        except urllib2.URLError as e:
            logging.warning(e)
            return
        except IOError as e:
            logging.warning(e)
            return

    @staticmethod
    def parse_html(url, str_html, reg):
        """解析网页内容，提取下一级需要爬取的网页url和符合目标正则表达式的url

        Args:
        url: 当前url，用于处理相对url
        str_html: 网页内容
        reg: 目标正则表达式

        Returns:
        next_list: 下一级url集合
        js_list: js文件的url
        ret: 符合正则表达式的url 
        """
        if "" == str_html:
            return [[], [], []]
        soup = BeautifulSoup(str_html)
        next_list = []
        js_list = []
        img_tag = soup.find_all(src=True)
        ret = []
        for tag in img_tag:
            try:
                src = tag["src"]
                if src and src[0]=='/':
                    src = url + src
                match = re.match(reg, src)
                if match:
                    ret.append(src)
                elif 'js' == src[-2:]:
                    js_list.append(src)
                elif src.startswith("http"):
                    next_list.append(src)
            except KeyError as e:
                logging.warning(e)
                continue

        href_tag = soup.find_all(href=True)
        for tag in href_tag:
            try:
                href = tag["href"]
                if href and href[0]=='/':
                    href = url + href
                m = re.match(reg, href)
                if m:
                    ret.append(href)
                elif "js" == href[-2:]:
                    js_list.append(href)
                elif href.startswith("http"):
                    next_list.append(href)
            except KeyError as e:
                logging.warning(e)
                continue
        return [next_list, js_list, ret]

    def is_enough(self):
        """判断抓取目标网页的数量是否达到预期

        Args:
        none

        returns:
        bool True : 已经达到预期数量
        bool False : 未达到预期数量
        """
        if self.count == self.params['target_count']:
            logging.info("已抓取 %d 个目标网页，可以退出了" % self.count)
            return True
        else:
            return False

    def begin_crawl(self, conf):
        """爬虫开始的地方。。。

        Args:
        conf: 配置文件

        returns: 
        none 
        """
        ret = self.build_params(conf)
        if False == ret:
            logging.info("初始化失败，退出....")
            return False

        crawl_depth = int(self.params['max_depth'])
        #读取种子url
        arr_source_url = []
        with open(self.params['url_list_file'])as fopen:
            for line in fopen:
                arr_source_url.append(line.strip())
        if 0 == len(arr_source_url):
            logging.info("种子文件为空，请检查种子文件，我走了")
            return False

        thread_count = self.params['thread_count']
        interval = self.params['crawl_interval']
        # 设置爬虫超时时间
        socket.setdefaulttimeout(self.params['crawl_timeout'])
        for depth in xrange(crawl_depth):
            # 开始第i层的爬取，然后解析网页，提取url
            work_manager = ThreadPool(thread_count, self.crawl_html, arr_source_url, interval)
            work_manager.wait_allcomplete()
            while True:
                try:
                    logging.info("开始解析网页")
                    res = work_manager.get_result()
                    # 爬虫线程中将url和url对应的网页内容存储成json
                    res = json.loads(res)
                    origin_url, html = [res['url'], res['html']]
                    parse_url_set = Crawler.parse_html(origin_url, html, self.params['target_url'])
                    next_url = parse_url_set[0]
                    js_url = parse_url_set[1]
                    ret = parse_url_set[2]

                    # 解析js文件中的目标url和下一级未访问过的url
                    for url in js_url:
                        resp = self.crawl_html(url)
                        js_parse_url_set = Crawler.parse_html(url, resp, self.params['target_url'])
                        tmp_next_url = js_parse_url_set[0]
                        tmp_ret = js_parse_url_set[2]
                        next_url.extend(tmp_next_url)
                        ret.extend(tmp_ret)

                    arr_target_url = Crawler.filter_unvisited_url(ret, self.target_visited_url)

                    for t_url in arr_target_url:
                        self.save_file(t_url)
                        if self.is_enough():
                            return True

                    arr_source_url = Crawler.filter_unvisited_url(next_url, self.visited_url)
                except Queue.Empty as e:
                    logging.warning(e)
                    logging.info("第 %d 级抓取完毕..." % depth)
                    break

        if self.is_enough():
            return True
        else:
            return False


def init_log(log_path):
    """初始化日志类，打印日志

    Args:
    string log_path:日志路径

    Returns:
    none 
    """
    global logging
    logging = log.init_log(log_path)
    return logging

if __name__ == '__main__':

    init_log(os.path.dirname(__file__) + "log/mini_crawler")
    if "-h" == sys.argv[1]:
        str_help = []
        str_help.append(" Instruction: ")
        str_help.append("\t-h: look help for mini_crawler ")
        str_help.append("\t-v: version of mini_crawler ")
        str_help.append("\t-c: run mini_crawler.py with config file.")
        str_help.append("\t\tconfig file like:")
        str_help.append("\t\t\t[spider]")
        str_help.append("\t\t\turl_list_file=./urls;")
        str_help.append("\t\t\toutput_directory=./output ")
        str_help.append("\t\t\tmax_depth=1  ")
        str_help.append("\t\t\tcrawl_interval=1 ")
        str_help.append("\t\t\tcrawl_timeout=1 ")
        str_help.append("\t\t\ttarget_url=.*.(gif|png|jpg|bmp)$")
        str_help.append("\t\t\tthread_count=8 ")
        print '\n'.join(str_help)
        print 'exiting...'
    elif "-v" == sys.argv[1]:
        str_ver = "1.0"
        logging.info('mini crawler version %s' % str_ver)
    elif "-c" == sys.argv[1]:
        str_welcome = "Welcome to mini_crawler"
        print str_welcome
        logging.info(str_welcome)
        crawler = Crawler()
        ret = crawler.begin_crawl(sys.argv[2])
        if ret:
            logging.info("已完成目标网页数量的抓取工作")
        else:
            logging.info("未完成目标网页数量的抓取工作")
        exit(0)
    else:
        print "enter 'python min_crawler.py -h' for more information"
        exit(1)

