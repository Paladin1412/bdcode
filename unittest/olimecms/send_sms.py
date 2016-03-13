#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os

sms_host_list = ['tc-sys-monitor00.tc:15003', 'tc-sys-monitor01.tc:15003']
def send(phone, unicode_txt):
    cmd = '{}/gsmsend -s {} -s {} {}@{}'.format(
        os.getcwd(),
        sms_host_list[0],
        sms_host_list[1],
        phone,
        unicode_txt.encode("gb18030"),
    )
    os.popen(cmd)


def cms_monitor(content):
    phone_dict = {
        #'xiaorixin': '18511870711',
        #'lizeyang': '18600962328',
       	#'bahuafeng': '13760218910',
        #'xiongwei': '18576776851',
        'lijingtao': '18476731655'
    }

    # content = u'测试一下'

    for user, phone in phone_dict.items():
        send(phone, content)

if __name__ == '__main__':
    cms_monitor(u"[CMS监控]请求安卓云输入失败!")

