<?php
/**
 * @file baseDiff.php
 * @author lijingtao
 * @date 2016/04/01 10:09:38
 * @brief diff类的基类
 *
 **/

abstract class BaseDiff{

    //左文件
    private $_fileLeft = null;

    //右文件
    private $_fileRight = null;

    //diff结果
    private $_res = array();

    /**
     * @breif 比较两个文件的差异之处
     * @param file $fileLeft
     * @param file $fileRight
     * @return bool
     **/
    abstract protected function diff();

    /**
     * @breif 打印两个文件的差异之处
     * @param none
     * @return none
     **/
    abstract protected function printf();

}
