# -*- coding:utf-8 -*- 
###########################################################
# create by lijingtao@baidu.com
# desc: webserver for inTime UU on android
#       url: http://jp01-global-op01.jp01.baidu.com:8888/index
#
###########################################################

import time
import datetime
import tornado.ioloop
import tornado.web
import tornado.websocket
import subprocess
import os
from tornado.options import define, options, parse_command_line
import paramiko
import threading
import shlex
import json
import socket
import pickle

define("port", default=8888, help="run on the given port", type=int)

dir_path = '/home/work/lijingtao/inTimeUU'

def load_json():
    hour  = time.strftime("%H")
    hour1 = '0'+str(int(hour)-1) if int(hour)-1<10 else str(int(hour)-1) 
    hour2 = '0'+str(int(hour)-2) if int(hour)-2<10 else str(int(hour)-2) 
    if os.path.isfile('%s/android_log/%s.json'%(dir_path,hour)):
        json_file = "%s/android_log/%s.json"%(dir_path, hour)
    else:
        if os.path.isfile('%s/android_log/%s.json'%(dir_path, hour1)):
            json_file = '%s/android_log/%s.json'%(dir_path, hour1)
        else:
            json_file = '%s/android_log/%s.json'%(dir_path, hour2)

    #cmd  = "ls %s"%json_file 
    
    cmd  = " ls -lah %s | awk '{print $6\" \"$7\" \"$8}'"%json_file 
    print cmd
    time_info = os.popen(cmd).readlines()
 
    ff   = open(json_file)
    ff.readline()
    data = ff.readline()
    try:
        ret = json.loads(data)
    except Exception,e:
        ret = {}
    #print ret
    return ret, time_info[-1]


os_ver_list = ['5.1.1','5.0','5.1','5.0.1','4.4.4','4.4.2','4.3','4.2.2','4.1.2','4.1.1','4.0.4','4.0.3']
class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        json_data ,str_time = load_json()
        self.render('index.html', str_time=str_time,os_ver_list=os_ver_list,app_ver_dict=json_data)

class uuHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        base_dir = "/home/work/lijingtao/inTimeUU/android_log"
        uuid_dict_file = "%s/uuid.pkl"%(base_dir)
        uuid = self.get_argument("uuid")
        print uuid_dict_file
        if os.path.exists(uuid_dict_file):
            print 'hehre'
            pkl_file = open(uuid_dict_file, 'rb')
            uuid_dict = pickle.load(pkl_file)
            print 'finish loading pkl' 
            if uuid_dict.has_key("{"+uuid):
                rs = uuid_dict["{"+uuid]
                #print rs
                self.write(rs)
                self.finish()
            else:
                self.write("no result")
                self.finish()
        else:
            self.write("no uuid data")
            self.finish()
        #self.render('log.html')

class logHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render('log.html')

class reportLogHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        ipAddr = self.get_argument("ip")
        log_path = self.get_argument("log_path")
        arr_tmp = log_path.split('/')
        print ipAddr,arr_tmp

        wget_cmd = "wget --limit-rate=25M -O %s/report_log/%s ftp://%s%s"%(dir_path,arr_tmp[-1],ipAddr,log_path)
        print wget_cmd
        ret = os.popen(wget_cmd).readlines()
        print "wget : ", ret
        rs = []
        with open("%s/report_log/%s"%(dir_path,arr_tmp[-1])) as op:
            for line in op:
                if line.strip() != '':
                    rs.append("<li>%s</li>"%line.strip())
        if rs:
            res = "<span class='label label-default'>记录数： %d</span> <br/>"%(len(rs))
            #self.write(res+'<br/>'.join(rs))
            self.write(res+'------------------------'.join(rs[::-1]))
            self.finish()
        else:
            strRet = "log file is empty</br>target machine: %s <br/>log path: %s"%(ipAddr, log_path)
            self.write(strRet)
            self.finish()
        
def execute_ab(args, obj, c_time,machine,username,pwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(machine,22,username, pwd)
    stdin,stdout,stderr = ssh.exec_command('hostname -i')
    for line in iter(stdout.readline,''):
	print line
    b_time = datetime.datetime.now().time()
    bs = b_time.hour*3600+b_time.minute*60+b_time.second
    stdin1,stdout1,stderr1 = ssh.exec_command(' '.join(args))
    '''
    for line in iter(stdout1.readline,''):
		if 'Requests per second' in line:
			obj.write_message(line)
		if 'Time per request' in line:
			obj.write_message(line)
		
	tmp = datetime.datetime.now().time()
	ttmp = tmp.hour*3600+tmp.minute*60+tmp.second
	print ttmp,bs
	if ttmp-bs > int(c_time):
		obj.write_message('time is up')
		flag = False
    ssh.close()
    '''


app = tornado.web.Application(handlers=[
    (r'/', IndexHandler),
    (r'/log', logHandler),
    (r'/findUU', uuHandler),
    (r'/reportLog', reportLogHandler)],
    template_path=os.path.join(os.path.dirname(__file__),'template'),
    static_path=os.path.join(os.path.dirname(__file__), 'static'))

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

