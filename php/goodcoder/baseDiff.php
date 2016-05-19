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

    //左文件名
    private $_nameLeft = '';

    //右文件名
    private $_nameRight = '';

    //右文件
    private $_fileRight = null;

    //diff结果
    private $_res = array();

    //输出结果文件
    private $_outFile = "";

    //输入结果编码
    private $_encoding = 'utf-8';


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

    /**
     * @brief 递归比较两个数组的差异之处
     * @param array $arrLeft
     * @param array $arrRight
     * @return mix
     **/
    public static function doDiff($arrLeft, $arrRight){

        $bolLeftArr  = is_array($arrLeft);
        $bolRightArr = is_array($arrRight);
        if(!$bolLeftArr && !$bolRightArr){
            return ($arrLeft == $arrRight);
        }else if($bolLeftArr !== $bolRightArr){
            return false;
        }else{
            if($arrLeft == $arrRight){
                return true;
            }
            $arrKey = array();
            $res = array();
            $arrKeyLeft  = array_keys($arrLeft);
            $arrKeyRight = array_keys($arrRight);
            //计算两个json的key差集
            $arrDiffLeft  = array_diff($arrKeyLeft, $arrKeyRight);
            $arrDiffRight = array_diff($arrKeyRight, $arrKeyLeft);
            //计算两个json的key交集
            $arrInter = array_intersect($arrKeyLeft, $arrKeyRight);
            foreach($arrInter as $key){
                $retDiff = self::doDiff($arrLeft[$key], $arrRight[$key]);
                if (false === $retDiff){
                    $res[$key] = array(
                        "left"  => $arrLeft[$key],
                        "right" => $arrRight[$key],
                    );
                }else if(is_array($retDiff)){
                    $res[$key] = $retDiff;
                }
            }
            foreach($arrDiffLeft as $key){
                $res[$key] = array(
                    "left"  => $arrLeft[$key],
                    "right" => '',
                );
            }
            foreach($arrDiffRight as $key){
                $res[$key] = array(
                    "left"  => '',
                    "eight" => $arrRight[$key],
                );
            }
            return $res;
        }
    }
}
