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
    public function DIffXML($xmlFileLeft, $xmlFileRight, $outFile, $encoding){
        
        $this->_outFile   = $outFile;
        $this->_encoding  = $encoding;
        $this->_nameLeft  = $xmlFileLeft;
        $this->_nameRight = $xmlFileRight;
        $this->_fileLeft  = self::xml2array($xmlFileLeft);
        $this->_fileRight = self::xml2array($xmlFileRight);
    }


    /**
     * @brief 将xml转换成数组
     * param string $strInputFile
     * @return array $arrData
     **/
    public static function xml2array($strInput){

        $tmpString  = file_get_contents($strInput);
        $tmpArr     = json_decode(json_encode(simplexml_load_string($tmpString)), true);
        $arrExplode = explode("<", $tmpString);
        $arrCh = array(' ', '\n');
        $rootTag    = substr(str_replace($arrCh, '', $arrExplode[1]), 0, -2);
        if (is_array($tmpArr)){
            $arrData = array(
                $rootTag  => array(),
            );
            foreach($tmpArr as $key => $value){
                $arrData[$rootTag][] = array(
                    $key  => $value,
                );
            }
            return $arrData;
        }
        return false;
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


    /*
     * @breif 打印两个XML文件的差异之处
     * @param none
     * @return none
     **/
    public function printf() {

        if (empty($this->_res)){
            $strSummary = printf("there is no diff between %s and %si. \n", $this->_nameLeft, $this->_nameRight);
            //echo $strSummary;
            //Log::info($strSummary);
        }else{
            //$strSummary = sprintf("there are %d diff[s], next is the detail differences.\n", count($this->_res[0]));
            //echo $strSummary;
            //Log::info($strSummary);
            $result = $this->_res[0];
            var_dump($result);
        }
    }
}
