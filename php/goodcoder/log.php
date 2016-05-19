<?php
/**
 * @file log.php
 * @author lijingtao
 * @date 2016/04/01 10:09:38
 * @brief 基础日志类
 *
 **/
date_default_timezone_set("Asia/Chongqing");
class Log{

    //正常日志路径
    const INFO_LOG_FILE = './diff.log';

    //异常日志路径
    const ERROR_LOG_FILE = './diff.log.wf';


    /**
     * @breif 打印正常日志
     * @param string $strLog 需要打印的内容
     * @return none
     **/
    public static function info($strLog){
        $strTime = self::getTime();
        $strLog  = sprintf("%s %s", $strTime, $strLog);
        $ret = file_put_contents(self::INFO_LOG_FILE, $strLog, FILE_APPEND);
    }

    /**
     * @brief 获取当前时间
     * @param none
     * @return string $strTime
     **/
    public static function getTime(){

        return date("Y-m-d H:i:s");
    }

    /**
     * @breif 打印两个文件的差异之处
     * @param string $strLog 需要打印的异常日志
     * @return int $intLine 出现异常的行数
     * @return none
     **/
    public static function warning($strErr, $intLine){
        $strTime = self::getTime();
        $strLog  = sprintf("%s line:%d %s", $strTime, $intLine, $strErr);
        file_put_contents(self::ERROR_LOG_FILE, $strLog, FILE_APPEND);
    }

}
