#!/usr/bin/env python
# -*- encofing:utf-8 -*-

import pickle
import os
import sys

base_dir = "/home/work/lijingtao/inTimeUU/android_log"
uuid_dict_file = "%s/uuid.pkl"%(base_dir)
pkl_file = open(uuid_dict_file, 'rb')
uuid_dict = pickle.load(pkl_file)
with open(sys.argv[1]) as fopen:
    for line in fopen:
        line = line.strip()
        if uuid_dict.has_key("{%s"%line):
            res = uuid_dict["{%s"%line]
            if "9.2.2" in res:
                print line + " " + res
