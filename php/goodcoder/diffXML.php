<?php
/**
 * @file diffXML.php
 * @author lijingtao
 * @date 2016/04/01 10:09:38
 * @brief 对json文件进行差异比较
 *
 **/

class DiffXML extends BaseDiff{


    /**
     * @brief 构造函数
     * @params xml file $xmlFileLeft
     * @params xml file $xmlFileRight
     * @return none
     **/
    public function DIffXML($xmlFileLeft, $xmlFileRight){

        $tmpLeft   = file_get_contents($xmlFileLeft);
        $tmpRight  = file_get_contents($xmlFileRight);
        $this->_fileLeft = json_decode(json_encode(simplexml_load_string($tmpLeft)), true);
        $this->_fileRight = json_decode(json_encode(simplexml_load_string($tmpRight)), true);
    }


    /*
     * @breif 比较两个XML文件的差异之处
     * @param file $xmlFileLeft
     * @param file $xmlFileRight
     * @return bool
     **/
    public function diff() {

        if (!empty($this->_fileLeft) && !empty($this->_fileRight)){
            if ($this->_fileLeft == $this->_fileRight){
                return true;
            }
            $this->_res[] = self::doDiff($this->_fileLeft, $this->_fileRight);
        }else if(empty($this->_fileLeft) || empty($this->_fileRight)){
            echo "json decode error\n";
        }
        return true;
    }


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
            //var_dump($arrInter);
            foreach($arrInter as $key){
                $retDiff = self::doDiff($arrLeft[$key], $arrRight[$key]);
                //var_dump($retDiff);
                if (false === $retDiff){
                    $res[$key] = array(
                        "left"  => $arrLeft[$key],
                        "right" => $arrRight[$key],
                    );
                }else if(is_array($retDiff)){
                    $res[$key] = $retDiff;
                }
            }
            //var_dump($res);
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


    /*
     * @breif 打印两个XML文件的差异之处
     * @param none
     * @return none
     **/
    public function printf() {
        var_dump($this->_res);
    }
}
