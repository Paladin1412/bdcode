#!/bin/sh

start=`date +%Y-%m-%d\ %H:%M:%S `

front0="ftp://jp01-ime-front00.jp01.baidu.com"
cmd="wget --limit-rate=25M -O /home/work/lijingtao/inTimeUU/android_log/uu.txt $front0/home/work/log/demsgcode.log "
#`echo $cd_cmd`
hour=`date +%H`
pp="pwd"
`echo $pp`
`echo $cmd `
#mv demsgcode.log /home/work/lijingtao/inTimeUU/android_log
#num=$(( $hour / 2 ))
#echo $num
front1="ftp://jp01-ime-front01.jp01.baidu.com"
cmd="wget --limit-rate=25M -O /home/work/lijingtao/inTimeUU/android_log/uuu.txt $front1/home/work/log/demsgcode.log "
`echo $cmd`
#cat /home/work/lijingtao/inTimeUU/android_log/uu.txt >> /home/work/lijingtao/inTimeUU/android_log/uuu.txt
cat /home/work/lijingtao/inTimeUU/android_log/uu.txt /home/work/lijingtao/inTimeUU/android_log/uuu.txt| /home/work/.jumbo/bin/python /home/work/lijingtao/inTimeUU/script.py > /home/work/lijingtao/inTimeUU/android_log/$hour.json
end=`date +%Y-%m-%d\ %H:%M:%S `
time=$(($(date +%s -d "$end")-$(date +%s -d "$start")))
rm -r /home/work/lijingtao/inTimeUU/android_log/uuu.txt
rm -r /home/work/lijingtao/inTimeUU/android_log/uu.txt
echo $time


