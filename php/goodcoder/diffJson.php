<?php
/**
 * @file diffJson.php
 * @author lijingtao
 * @date 2016/04/01 10:09:38
 * @brief 对json文件进行差异比较
 *
 **/


class DiffJson extends BaseDiff{


    //左边文件的行数
    private $_intLeftLine = 0;

    //右边文件的行数
    private $_intRightLine = 0;


    /**
     * @brief 构造函数
     * @params json file $jsonFileLeft
     * @params json file $jsonFileRight
     * @return none
     **/
    public function DiffJson($jsonFileLeft, $jsonFileRight){

        $this->_fileLeft     = file($jsonFileLeft);
        $this->_intLeftLine  = count($this->_fileLeft);
        $this->_fileRight    = file($jsonFileRight);
        $this->_intRightLine = count($this->_fileRight);
    }


    /**
     * @breif 比较两个json文件的差异之处
     * @param file $jsonFileLeft
     * @param file $jsonFileRight
     * @return bool
     **/
    public function diff() {

        //逐行比较
        //左右文件同时遍历
        $intBegin = 0;
        while ($intBegin < $this->_intLeftLine || $intBegin < $this->_intRightLine){
            $leftCurrent  = self::getContentByLine('left', $intBegin);
            $rightCurrent = self::getContentByLine('right', $intBegin);
            $intBegin += 1;
            if (!empty($leftCurrent) && !empty($rightCurrent)){
                //如果同一行都不为空，转换成数组再比较
                $arrLeft  = json_decode($leftCurrent, true);
                $arrRight = json_decode($rightCurrent, true);
                if ($arrLeft == $arrRight){
                    $strMsg = sprintf("json line%d no diff", $intBegin);
                    Log::info($strMsg);
                }else if (empty($arrLeft) || empty($arrRight)){
                    //转换失败，打印日志，继续遍历下一行
                    $strLog = sprintf("json decode error line: %d [left: %s] [right: %s]", $intBegin, $leftCurrent, $rightCurrent);
                    Log::warning($strLog, __LINE__);
                }else{
                    //转换数组后进行diff比较
                    $this->_res["line".strval($intBegin)] = array(
                        'data'   => self::doDiff($arrLeft, $arrRight),
                        'diff'   => true,
                    );
                }
            }else{
                if (empty($leftCurrent)){
                    $this->_res["line".strval($intBegin)] = array(
                        'diff' => false,
                        'data' => array(
                            "left"  => "",
                            "right" => json_decode($rightCurrent, true),
                        ),
                    );
                }
                if (empty($rightCurrent)){
                    $this->_res["line".strval($intBegin)] = array(
                        'diff'  => false,
                        'data'  => array(
                            "right"  => "",
                            "left"   => json_decode($leftCurrent, true),
                        ),
                    );
                }
            }
        }
 
        return true;
    }


    /**
     * @brief 获取特定行数的内容
     * @param array $arrFile json内容的数组
     * @param int $intLine 行数
     * @return string $data
     **/
    public function getContentByLine($side, $intLine){

        $data = "";
        switch ($side){
            case 'left':
                if ($intLine >= $this->_intLeftLine){
                    $data = "";
                }else{
                    $data = $this->_fileLeft[$intLine];
                }
                break;
            case 'right':
                if ($intLine >= $this->_intRightLine){
                    $data = "";
                }else{
                    $data = $this->_fileRight[$intLine];
                }
                break;
        }
        return $data;
    }


    /**
     * @breif 打印两个json文件的差异之处
     * @param none
     * @return none
     **/
    public function printf() {

        var_dump($this->_res);
    }
}
