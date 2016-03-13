import sys
import json
import pickle

if __name__=='__main__':
    app_ver_dict = {}
    os_ver_dict  = {}
    uuid_dict    = {} 
    for line in sys.stdin:
        arr = line.split("|||")
        #print arr
        try:
            ind  = arr[0].index("{")
            uuid = arr[0][ind:-1]
            
            if uuid_dict.has_key(uuid):
               continue
            uuid_dict[uuid] = ' '.join([arr[1], arr[3], arr[7]])
 
            app_ver = arr[1].split("=")[-1]
            os_ver  = arr[3].split("=")[-1]
            if  os_ver_dict.has_key(os_ver):
                os_ver_dict[os_ver] += 1
            else:
                os_ver_dict[os_ver] = 1

            if app_ver_dict.has_key(app_ver):
                app_ver_dict[app_ver]['count'] += 1
            else:
                app_ver_dict[app_ver]          = {}
                app_ver_dict[app_ver]["count"] = 1

            if app_ver_dict[app_ver].has_key(os_ver):
                app_ver_dict[app_ver][os_ver] += 1
            else:
                app_ver_dict[app_ver][os_ver] = 1
        except Exception, e:
            continue
    oo = json.JSONEncoder().encode(os_ver_dict)
    print oo,len(os_ver_dict)
    k  = json.JSONEncoder().encode(app_ver_dict)
    print k
    base_dir = '/home/work/lijingtao/inTimeUU/android_log'
    uuid_dict_file = open("%s/uuid.pkl"%(base_dir),'wb')
    pickle.dump(uuid_dict, uuid_dict_file)
    uuid_dict_file.close()
               
