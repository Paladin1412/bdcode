<?php
/**
 * @file diff.php
 * @author lijingtao
 * @date 2016/04/01 10:09:38
 * @brief 程序入口，接收命令行参数进行文件diff操作
 *
 **/

require_once "./baseDiff.php";
require_once "./diffJson.php";
require_once "./diffXML.php";
require_once "./log.php";

/*
 * @brief 解析命令行参数
 * @param array $arrParam
 * return array $res
 */
function checkArgv($arrParam){

    $intCount = count($arrParam);
    if ($arrParam[0] === '-v'){
        echo "php diff program by lijingtao.\nversion: 1.0\n";
        exit(0);
    }
    if ($intCount < 9 || $arrParam[0] === '-h'){
        echo "usage: php diff.php -t json -l leftFile -r rightFile -o outFile -e utf8 \n";
        exit(0);
    }
    return array(
        'type'      => $arrParam[1],
        'left'      => $arrParam[3],
        'right'     => $arrParam[5],
        'outFile'   => $arrParam[7],
        'encoding'  => empty($arrParam[9]) ? 'utf8' : $arrParam[9],
    );
}


$arrParam = array_slice($argv, 1);

$res = checkArgv($arrParam);
Log::info("diff begin...........\n");

switch ($res['type']){
    case 'json':
        $diffJson = new DiffJson($res['left'], $res['right']);
        $diffJson->diff();
        $diffJson->printf();
        Log::info("diff json end........\n");
        break;
    case 'xml':
        $diffXML = new DiffXML($res['left'], $res['right'], $res['outFile'], $res['encoding']);
        $diffXML->diff();
        $diffXML->printf();
        Log::info("diff xml end..........\n");
        break;

}
