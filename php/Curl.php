<?php
/***************************************************************************
 *
 * Copyright (c) 2010 Baidu.com, Inc. All Rights Reserved
 * $Id$
 *
 **************************************************************************/

/**
 * @file
 * @author
 *          wangtao04@baidu.com mod from bae
 * @date 2012/08/06 18:44:24
 * @version $Revision$
 * @brief  Fetch Url
 *
 **/

class Orp_FetchUrl {
    const SUCCESS = 0;              //成功
    const errUrlInvalid = 1;        //非法url
    const errServiceInvalid = 2;    //对端服务不正常
    const errHttpTimeout = 3;       //交互超时，包括连接超时
    const errTooManyRedirects = 4;  //重定向次数过多
    const errTooLargeResponse = 5;  //响应内容过大
    const errResponseErrorPage = 6; //返回错误页面
    const errNoResponse = 7;        //没有响应包
    const errNoResponseBody = 8;    //响应包中没有body内容
    const errOtherEror = 9;         //其余错误
    const MAX_REDIRS_CONS = 8;  //max_redirs次数限制
    const errWrongCurlOptions = 10; //响应包中没有body内容

    const MAX_RETRY_NUMS = 100;

    protected $curl;
    protected $curl_info;
    protected $curl_options = null; //curl options

    protected $max_response_size;   //max response body size

    protected $http_code = null;
    protected $header;
    protected $headers;
    protected $body_len;
    protected $body;
    protected $errno;
    protected $errmsg;

    protected $useable_proxy_host = null;
    protected $current_proxy_host = null;
    protected $direct_curl_opts = array();

    protected $up_stream = null;
    protected $up_stream_size = null;
    protected $up_stream_function = null;

    private static $instance = null;


    protected function __construct($options = null)
    {
        $user_agent = isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] :
            'Orp_FetchUrl v1.0';
        $referer = isset($_SERVER['HTTP_HOST']) ? "http://".$_SERVER['HTTP_HOST'].$_SERVER['REQUEST_URI'] : "";


        $this->reset();

        $this->curl_options = array(
                'follow_location' => true,
                'max_redirs' => 3,
                'conn_retry' => 3,
                'conn_timeout' => 1000,
                'timeout' => 3000,
                'user_agent' => $user_agent,
                'referer' => $referer,
                'encoding' => '',
                'max_response_size' => 512000,  //default is 500k
        );

        $this->setOptions($options);
    }


    public static function getInstance($options = null)
    {
        if( self::$instance === null )
        {
            self::$instance = new Orp_FetchUrl($options);
        }
        else
        {
            self::$instance->setOptions($options);
        }
        return self::$instance;
    }

    public static function onResponseHeader($curl, $header)
    {
        $proxy = Orp_FetchUrl::getInstance();
        $proxy->header .= $header;

        $trimmed = trim($header);
        $pos = strpos($trimmed, ":");
        if ( $pos ) {
            $key = trim(substr($trimmed, 0, $pos));
            $value = trim(substr($trimmed, $pos + 1));
            if ($key == "Set-Cookie") {
                if (array_key_exists($key, $proxy->headers)) {
                    array_push($proxy->headers[$key], $value);
                } else {
                    $proxy->headers[$key] = array($value);
                }
            } else {
                if (strcasecmp("Content-Length", $key) == 0) {
                    $content_length = intVal($value);
                    if( $content_length > $proxy->max_response_size )
                    {
                        $proxy->body_len = $content_length;
                        return 0;
                    }
                }
                $proxy->headers[$key] = $value;
            }
        }

        return strlen($header);
    }

    public static function onResponseData($curl, $data)
    {
        $proxy = Orp_FetchUrl::getInstance();

        $chunck_len = strlen($data);
        $proxy->body .= $data;
        $proxy->body_len += $chunck_len;

        if( $proxy->body_len <= $proxy->max_response_size )
        {
            return $chunck_len;
        }
        else
        {
            return 0;
        }
    }

    public function setOptions($options)
    {
        if( is_array($options) )
        {
            //$options + $default_options results in an assoc array with overlaps
            //deferring to the value in $options
            if (isset($options['max_redirs']) && $options['max_redirs'] >  self::MAX_REDIRS_CONS) {
                $options['max_redirs'] = self::MAX_REDIRS_CONS;
            }
            $this->curl_options = $options + $this->curl_options;
        }

        $this->max_response_size = $this->curl_options['max_response_size'];
    }

    private function isForbidenCall()
    {
        $conf = Bd_Conf::getConf('/orp/fetchurl');
        if( empty($conf['forbiden']['addr'] ) || empty($conf['forbiden']['domain']) )
            return false;
        if( !isset($_SERVER['DOCUMENT_ROOT']))
            return false;

        foreach ($conf['forbiden']['domain'] as $_v) {
            $proxyForbidenDomain[] = $_v;
        }
        $root = $_SERVER['DOCUMENT_ROOT'];
        $host = trim(substr($root,1+strrpos($root,'/',-2)),'/');
        if( !empty($host) )
        {
            if ( in_array(trim($host), $proxyForbidenDomain))
            {
                return true;
            }
        }
        return false;

    }
    private function reset_useable_proxy_host($https = false)
    {
        $conf = Bd_Conf::getConf('/orp/fetchurl');
        if ($conf  === false) {
            trigger_error("orp.conf err!",E_USER_ERROR);
            exit(0);
        }
        if (empty($conf['proxy'])) {
            trigger_error("orp.conf [proxy] empty.",E_USER_ERROR);
            exit(0);
        }
        //proxy forbiden init
        $proxyForbidenAddr = array();
        if (isset($conf['forbiden']['addr'])) {
            foreach ($conf['forbiden']['addr'] as $_v) {
                $proxyForbidenAddr[$_v['host']] = $_v['weight'];
            }
        }
        //https proxy  init
        $proxyHttpsAddr = array();
        if (isset($conf['https']['addr'])) {
            foreach ($conf['https']['addr'] as $_v) {
                $proxyHttpsAddr[$_v['host']] = $_v['weight'];
            }
        }

        //proxy  init
        $proxyAddr = array();
        if (isset($conf['proxy'])) {
            foreach ($conf['proxy']['addr'] as $_v) {
                $proxyAddr[$_v['host']] = $_v['weight'];
            }
        }

        if ($https) {
            $this->useable_proxy_host  = $proxyHttpsAddr;
        } else if ($this->isForbidenCall()){
            $this->useable_proxy_host  = $proxyForbidenAddr;
        }else{
            $this->useable_proxy_host = $proxyAddr;
        }
    }

    private function has_useable_proxy()
    {
        if(!empty($this->useable_proxy_host))
        {
            foreach($this->useable_proxy_host as $host => $weight)
            {
                if ( $weight > 0) return true;
            }
        }
        return false;
    }
    public function get_proxy_addr($https=false) {
        $this->reset_useable_proxy_host($https);
        $ret = array();
        foreach( $this->useable_proxy_host as $h => $w) {
            $ret[] = $h;
        }
        return $ret;
    }
    private function get_useable_proxy()
    {
        $proxy = '';
        if ( count($this->useable_proxy_host) > 0)
        {
            $all = array();
            foreach($this->useable_proxy_host as $host => $weight)
            {
                for($i = 0; $i < $weight;$i++)
                {
                    $all[] = $host;
                }
            }
            if( count($all)> 0)
            {
                $cnt = count($all);
                $pos = rand(0, $cnt-1);
                $proxy = $all[$pos];
                return $proxy;
            }
        }
        return $proxy;

    }
    private function mask_current_proxy()
    {
        if( !empty($this->current_proxy_host) && isset($this->useable_proxy_host[$this->current_proxy_host]))
        {
            unset($this->useable_proxy_host[$this->current_proxy_host]);
        }

    }
    public function setProxy(&$curl) {
        $proxy = '';
        $proxy = $this->get_useable_proxy();

        if (!empty($proxy)) {
            curl_setopt($curl, CURLOPT_PROXY, $proxy);
            $this->current_proxy_host = $proxy;
        }else{
            trigger_error('cant get usable proxy',E_USER_WARNING);
        }
    }
    public function get($url, $headers = array(), $cookie = array())
    {
        $https = stripos($url, 'https://') === 0 ? true : false;
        if ($https) {
            $url = str_replace('https://', '', $url);
        }
        $this->reset_useable_proxy_host($https);

        $ret = '';
        $retry = 0;
        while($retry++< self::MAX_RETRY_NUMS){
            $this->reset();
            $ret = $this->single_get($url, $headers, $cookie );
            if ( false === $ret && $this->errno() == self::errServiceInvalid)
            {
                $this->mask_current_proxy();

                if ( $this->has_useable_proxy()){
                    continue;
                }else{
                    break;
                }
            }else{
                break;
            }
        }
        return $ret;
    }


    private function single_get($url, $headers = array(), $cookie = array())
    {

        extract($this->curl_options);

        $headers[] = "x_bd_logid:" . Bd_Log::genLogID();

        $curl = curl_init();
        if( $max_redirs < 1 )
        {
            $max_redirs = 1;
        }
        $this->setProxy($curl);
        $curl_opts = array( CURLOPT_URL => $url,
                CURLOPT_USERAGENT => $user_agent,
                CURLOPT_REFERER => $referer,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_HEADER => false,
                //CURLOPT_SSL_VERIFYPEER => false,
                //CURLOPT_SSL_VERIFYHOST => false,
//              CURLINFO_HEADER_OUT => true, // for debug
                CURLOPT_HTTPHEADER => $headers,
                CURLOPT_FOLLOWLOCATION => $follow_location,
                CURLOPT_MAXREDIRS => $max_redirs,
                CURLOPT_ENCODING => $encoding,
                CURLOPT_WRITEFUNCTION => 'Orp_FetchUrl::onResponseData',
                CURLOPT_HEADERFUNCTION => 'Orp_FetchUrl::onResponseHeader'
                );

        //mod 20100106: 修复低版本CURL不支持CURLOPT_TIMEOUT_MS的bug;
        if ( defined('CURLOPT_TIMEOUT_MS') && defined('CURLOPT_CONNECTTIMEOUT_MS') ) {
            $curl_opts[CURLOPT_TIMEOUT_MS] = max($timeout,1);
            $curl_opts[CURLOPT_CONNECTTIMEOUT_MS] = max($conn_timeout,1);
            $curl_opts[CURLOPT_NOSIGNAL] = true;
        }else {
            $curl_opts[CURLOPT_TIMEOUT] = max($timeout/1000,1);
            $curl_opts[CURLOPT_CONNECTTIMEOUT] = max($conn_timeout/1000,1);
        }

        if( is_array($cookie) && count($cookie) > 0 )
        {
            $cookie_str = '';
            foreach( $cookie as $key => $value )
            {
                $cookie_str .= "$key=$value; ";
            }
            $curl_opts[CURLOPT_COOKIE] = $cookie_str;
        }

        $this->merge_curl_opts($curl_opts);
        curl_setopt_array($curl, $curl_opts);

        curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
        curl_exec($curl);

        $errno = curl_errno($curl);
        $errmsg = curl_error($curl);
        $this->curl_info = curl_getinfo($curl);
        curl_close($curl);

        if( $this->check_http_response($url, $errno, $errmsg) )
        {
            return $this->body;
        }

        return false;
    }

    public function set_read_stream($stream,$size) {
            $this->up_stream = $stream;
            $this->up_stream_size = $size;
    }
    public function get_up_stream_size()
    {
        return $this->up_stream_size;
    }
    public function get_up_stream()
    {
        return $this->up_stream;
    }
    public function set_read_function($function_name)
    {
            $this->up_read_function = $function_name;
    }
    public function put($url, $params = null, $headers = array(), $cookie = array())
    {
        $this->reset_useable_proxy_host();
        $ret = '';
        $retry = 0;
        while($retry++< self::MAX_RETRY_NUMS){
            $this->reset();
            $ret = $this->single_put($url,$params,$headers, $cookie );
            if ( false === $ret && $this->errno() == self::errServiceInvalid)
            {
                $this->mask_current_proxy();

                if ( $this->has_useable_proxy()){
                    continue;
                }else{
                    break;
                }
            }else{
                break;
            }
        }
        return $ret;
    }

    private function single_put($url, $params=null ,$headers = array(), $cookie = array())
    {

        extract($this->curl_options);
        $headers[] = "x_bd_logid:" . Bd_Log::genLogID();

        $curl = curl_init();
        if( $max_redirs < 1 )
        {
            $max_redirs = 1;
        }
        $this->setProxy($curl);
        $curl_opts = array( CURLOPT_URL => $url,
                CURLOPT_CUSTOMREQUEST=> 'PUT',
                CURLOPT_USERAGENT => $user_agent,
                CURLOPT_REFERER => $referer,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_HEADER => false,
                //              CURLINFO_HEADER_OUT => true, // for debug
                CURLOPT_HTTPHEADER => $headers,
                CURLOPT_FOLLOWLOCATION => $follow_location,
                CURLOPT_MAXREDIRS => $max_redirs,
                CURLOPT_ENCODING => $encoding,
                CURLOPT_WRITEFUNCTION => 'Orp_FetchUrl::onResponseData',
                CURLOPT_HEADERFUNCTION => 'Orp_FetchUrl::onResponseHeader'
                );

        if ( is_resource($this->up_stream) )
        {
            curl_setopt ( $curl, CURLOPT_INFILE, $this->up_stream);
            curl_setopt ( $curl, CURLOPT_INFILESIZE, $this->up_stream_size);
            curl_setopt ( $curl, CURLOPT_UPLOAD, true );
            if ($this->up_stream_function !== null)
                curl_setopt ( $curl, CURLOPT_READFUNCTION, $this->up_stream_function);
        }
        if(!empty($params)){
            if ( is_string($params) ) {
                $post_str = $params;
            }else if( is_array($params)){
                $post_str = http_build_query($params);
            }else{
                trigger_error("post params format error! it should be array or string",E_USER_ERROR);
                exit(0);
            }
            $rr = curl_setopt ( $curl, CURLOPT_POSTFIELDS, $post_str);
        }

        //mod 20100106: 修复低版本CURL不支持CURLOPT_TIMEOUT_MS的bug;
        if ( defined('CURLOPT_TIMEOUT_MS') && defined('CURLOPT_CONNECTTIMEOUT_MS') ) {
            $curl_opts[CURLOPT_TIMEOUT_MS] = max($timeout,1);
            $curl_opts[CURLOPT_CONNECTTIMEOUT_MS] = max($conn_timeout,1);
            $curl_opts[CURLOPT_NOSIGNAL] = true;
        }else {
            $curl_opts[CURLOPT_TIMEOUT] = max($timeout/1000,1);
            $curl_opts[CURLOPT_CONNECTTIMEOUT] = max($conn_timeout/1000,1);
        }

        if( is_array($cookie) && count($cookie) > 0 )
        {
            $cookie_str = '';
            foreach( $cookie as $key => $value )
            {
                $cookie_str .= "$key=$value; ";
            }
            $curl_opts[CURLOPT_COOKIE] = $cookie_str;
        }

        $this->merge_curl_opts($curl_opts);
        curl_setopt_array($curl, $curl_opts);

        curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
        curl_exec($curl);

        $errno = curl_errno($curl);
        $errmsg = curl_error($curl);
        $this->curl_info = curl_getinfo($curl);
        curl_close($curl);

        if( $this->check_http_response($url, $errno, $errmsg) )
        {
            return $this->body;
        }

        return false;
    }
    public function delete($url, $headers = array(), $cookie = array())
    {
        $this->reset_useable_proxy_host();
        $ret = '';
        $retry = 0;
        while($retry++< self::MAX_RETRY_NUMS){
            $this->reset();
            $ret = $this->single_delete($url, $headers, $cookie );
            if ( false === $ret && $this->errno() == self::errServiceInvalid)
            {
                $this->mask_current_proxy();

                if ( $this->has_useable_proxy()){
                    continue;
                }else{
                    break;
                }
            }else{
                break;
            }
        }
        return $ret;
    }
    private function single_delete($url, $headers = array(), $cookie = array())
    {

        extract($this->curl_options);
        $headers[] = "x_bd_logid:" . Bd_Log::genLogID();

        $curl = curl_init();
        if( $max_redirs < 1 )
        {
            $max_redirs = 1;
        }
        $this->setProxy($curl);
        $curl_opts = array( CURLOPT_URL => $url,
                CURLOPT_CUSTOMREQUEST=> 'DELETE',
                CURLOPT_USERAGENT => $user_agent,
                CURLOPT_REFERER => $referer,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_HEADER => false,
//              CURLINFO_HEADER_OUT => true, // for debug
                CURLOPT_HTTPHEADER => $headers,
                CURLOPT_FOLLOWLOCATION => $follow_location,
                CURLOPT_MAXREDIRS => $max_redirs,
                CURLOPT_ENCODING => $encoding,
                CURLOPT_WRITEFUNCTION => 'Orp_FetchUrl::onResponseData',
                CURLOPT_HEADERFUNCTION => 'Orp_FetchUrl::onResponseHeader'
                );

        //mod 20100106: 修复低版本CURL不支持CURLOPT_TIMEOUT_MS的bug;
        if ( defined('CURLOPT_TIMEOUT_MS') && defined('CURLOPT_CONNECTTIMEOUT_MS') ) {
            $curl_opts[CURLOPT_TIMEOUT_MS] = max($timeout,1);
            $curl_opts[CURLOPT_CONNECTTIMEOUT_MS] = max($conn_timeout,1);
            $curl_opts[CURLOPT_NOSIGNAL] = true;
        }else {
            $curl_opts[CURLOPT_TIMEOUT] = max($timeout/1000,1);
            $curl_opts[CURLOPT_CONNECTTIMEOUT] = max($conn_timeout/1000,1);
        }

        if( is_array($cookie) && count($cookie) > 0 )
        {
            $cookie_str = '';
            foreach( $cookie as $key => $value )
            {
                $cookie_str .= "$key=$value; ";
            }
            $curl_opts[CURLOPT_COOKIE] = $cookie_str;
        }

        $this->merge_curl_opts($curl_opts);
        curl_setopt_array($curl, $curl_opts);

        curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
        curl_exec($curl);

        $errno = curl_errno($curl);
        $errmsg = curl_error($curl);
        $this->curl_info = curl_getinfo($curl);
        curl_close($curl);

        if( $this->check_http_response($url, $errno, $errmsg) )
        {
            return $this->body;
        }

        return false;
    }


    public function post($url, $params, $headers = array(), $cookie = array())
    {
        $https = stripos($url, 'https://') === 0 ? true : false;
        if ($https) {
            $url = str_replace('https://', '', $url);
        }
        $this->reset_useable_proxy_host($https);
        $ret = '';
        $retry = 0;
        while($retry++< self::MAX_RETRY_NUMS){
            $this->reset();
            $ret = $this->single_post($url,$params,$headers, $cookie );
            if ( false === $ret && $this->errno() == self::errServiceInvalid)
            {
                $this->mask_current_proxy();

                if ( $this->has_useable_proxy()){
                    continue;
                }else{
                    break;
                }
            }else{
                break;
            }
        }
        return $ret;
    }
    public function direct_set_curl_options(Array $optarray)
    {
        if ( ! is_array($optarray))
        {
            trigger_error(" optarray must be array");
        }
        $curl = curl_init();
        if( false === curl_setopt_array($curl,$optarray))
        {
            $this->errno = self::errWrongCurlOptions;
            $this->errmsg = "Wrong curl options in direct setting";
            return false;
        }
        $this->direct_curl_opts = $optarray;
    }
    private function merge_curl_opts(&$opts)
    {
        if ( empty($this->direct_curl_opts))
            return $opts;
        foreach($this->direct_curl_opts as $k=>$v)
        {
            if ( isset($opts[$k]))
                continue;
            $opts[$k] = $v;
        }
        return $opts;
    }
    private function single_post($url, $params, $headers = array(), $cookie = array())
    {

        extract($this->curl_options);
        $headers[] = "x_bd_logid:" . Bd_Log::genLogID();

        $curl = curl_init();
        if( $max_redirs < 1 )
        {
            $max_redirs = 1;
        }

        $this->setProxy($curl);
        $curl_opts = array( CURLOPT_URL => $url,
                CURLOPT_USERAGENT => $user_agent,
                CURLOPT_REFERER => $referer,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_HEADER => false,
                CURLOPT_HTTPHEADER => $headers,
                CURLOPT_ENCODING => $encoding,
                CURLOPT_WRITEFUNCTION => 'Orp_FetchUrl::onResponseData',
                CURLOPT_HEADERFUNCTION => 'Orp_FetchUrl::onResponseHeader'
                );

        //mod 20100106: 修复低版本CURL不支持CURLOPT_TIMEOUT_MS的bug;
        if ( defined('CURLOPT_TIMEOUT_MS') && defined('CURLOPT_CONNECTTIMEOUT_MS') ) {
            $curl_opts[CURLOPT_TIMEOUT_MS] = max($timeout,1);
            $curl_opts[CURLOPT_CONNECTTIMEOUT_MS] = max($conn_timeout,1);
            $curl_opts[CURLOPT_NOSIGNAL] = true;
        }else {
            $curl_opts[CURLOPT_TIMEOUT] = max($timeout/1000,1);
            $curl_opts[CURLOPT_CONNECTTIMEOUT] = max($conn_timeout/1000,1);
        }

        if( is_array($cookie) && count($cookie) > 0 )
        {
            $cookie_str = '';
            foreach( $cookie as $key => $value )
            {
                $cookie_str .= "$key=$value; ";
            }
            $curl_opts[CURLOPT_COOKIE] = $cookie_str;
        }
        $this->merge_curl_opts($curl_opts);
        curl_setopt_array($curl, $curl_opts);

        $last_url   = $url;
        $redirects  = 0;
        $retries    = 0;

        if ( is_string($params) ) {
            $post_str = $params;
        }else if( is_array($params)){
            $post_str = http_build_query($params);
        }else{
            trigger_error("post params format error! it should be array or string",E_USER_ERROR);
        }

        if( $max_redirs == 1 )
        {
            curl_setopt($curl, CURLOPT_POSTFIELDS, $post_str);
            curl_exec($curl);
            $errno = curl_errno($curl);
            $errmsg = curl_error($curl);
            $this->curl_info = curl_getinfo($curl);
        }
        else
        {
            $start_time = microtime(true);
            for( $attempt = 0; $attempt < $max_redirs; $attempt++ )
            {
                curl_setopt($curl, CURLOPT_POSTFIELDS, $post_str);
                curl_exec($curl);
                $errno = curl_errno($curl);
                $errmsg = curl_error($curl);
                $this->curl_info = curl_getinfo($curl);

                //Remove any HTTP 100 headers
                if( ($this->curl_info['http_code'] == 301 ||
                            $this->curl_info['http_code'] == 302 ||
                            $this->curl_info['http_code'] == 307) &&
                        preg_match('/Location: ([^\r\n]+)\r\n/si', $this->header, $matches) )
                {
                    $new_url = $matches[1];

                    //if $new_url is relative path, prefix with domain name
                    if( !preg_match('/^http(|s):\/\//', $new_url) &&
                            preg_match('/^(http(?:|s):\/\/.*?)\//', $url, $matches) )
                            {
                                $new_url = $matches[1] . '/' . $new_url;
                            }
                    $last_url = $new_url;
                    curl_setopt($curl, CURLOPT_URL, $new_url);

                    //reduce the timeout, but keep it at least 1 or we wind up with an infinite timeout

                    if ( defined('CURLOPT_TIMEOUT_MS') ) {
                        curl_setopt($curl, CURLOPT_TIMEOUT_MS, max($start_time + $timeout - microtime(true), 1));
                    }else {
                        curl_setopt($curl, CURLOPT_TIMEOUT, max(($start_time + $timeout - microtime(true))/1000, 1));
                    }
                    ++$redirects;
                }
                elseif( $conn_retry && strlen($this->header) == 0 )
                {
                    //probably a connection failure...if we have time, try again...
                    $time_left = $start_time + $timeout - microtime(true);
                    if( $time_left < 1 )
                    {
                        break;
                    }
                    // ok, we've got some time, let's retry
                    curl_setopt($curl, CURLOPT_URL, $last_url);
                    if ( defined('CURLOPT_TIMEOUT_MS') ) {
                        curl_setopt($curl, CURLOPT_TIMEOUT_MS, max($time_left,1));
                    }else {
                        curl_setopt($curl, CURLOPT_TIMEOUT, max($time_left/1000,1));
                    }
                    ++$retries;
                }
                else
                {
                    break; // we have a good response here
                }
            }
        }

        curl_close($curl);

        if( $this->check_http_response($url, $errno, $errmsg) )
        {
            return $this->body;
        }

        return false;
    }

    public function content_type()
    {
        //take content-type field into account first

        if(empty($this->curl_info['content_type'])) {
            return false;
        }
        $str = $this->curl_info['content_type'];
        $ret = strpos($str, ';');
        if ($ret === false) {
            return $str;
        }
        return substr($str, 0, $ret);
    }

    public function body()
    {
        return $this->body;
    }

    public function cookie()
    {
        if( empty($this->headers['Set-Cookie']) )
        {
            return array();
        }

        return $this->headers['Set-Cookie'];
    }

    public function http_code()
    {
        return $this->http_code;
    }

    public function errno()
    {
        return $this->errno;
    }

    public function errmsg()
    {
        return $this->errmsg;
    }

    public function header()
    {
        return $this->header;
    }

    public function headers()
    {
        return $this->headers;
    }

    public function curl_info()
    {
        return $this->curl_info;
    }

    private function check_http_response($url, $errno, $errmsg)
    {
        $url = htmlspecialchars($url, ENT_QUOTES);

        $http_code = $this->curl_info['http_code'];

        if( $errno == CURLE_URL_MALFORMAT ||
                $errno == CURLE_COULDNT_RESOLVE_HOST )
        {
            $this->errno = self::errUrlInvalid;
            $this->errmsg = "The URL $url is not valid.";
        }
        elseif( $errno == CURLE_COULDNT_CONNECT )
        {
            $this->errno = self::errServiceInvalid;
            $this->errmsg = "Service for URL[$url] is invalid now, errno[$errno] errmsg[$errmsg]";
        }
        elseif( $errno == 28/*CURLE_OPERATION_TIMEDOUT*/ )
        {
            $this->errno = self::errHttpTimeout;
            $this->errmsg = "Request for $url timeout: $errmsg";
        }
        elseif($errno == CURLE_TOO_MANY_REDIRECTS &&  ($http_code == 301 || $http_code == 302 || $http_code == 307 ))
        {
            //$errno == CURLE_OK can only indicate that the response is received, but it may
            //also be an error page or empty page, so we also need more checking when $errno == CURLE_OK
            $this->errno = self::errTooManyRedirects;
            $this->errmsg = "Request for $url caused too many redirections.";
        }
        elseif( $http_code >= 400 )
        {
            $this->errno = self::errResponseErrorPage;
            $this->errmsg = "Received HTTP error code $http_code while loading $url";
        }
        elseif( $this->body_len > $this->max_response_size )
        {
            $this->errno = self::errTooLargeResponse;
            $this->errmsg = "Response body for $url has at least {$this->body_len} bytes, " .
                "which has exceed the max response size[{$this->max_response_size}]";
        }
        elseif( $errno != CURLE_OK )
        {
            if( $this->body_len == 0 )
            {
                if( $http_code )
                {
                    $this->errno = self::errNoResponseBody;
                    $this->errmsg = "Request for $url returns HTTP code $http_code and no data.";
                }
                else
                {
                    $this->errno = self::errNoResponse;
                    $this->errmsg = "The URL $url has no response.";
                }
            }
            else
            {
                $this->errno = self::errOtherEror;
                $this->errmsg = "Request for $url failed, errno[$errno] errmsg[$errmsg]";
            }
        }
        else
        {
            $this->errno = self::SUCCESS;
            $this->errmsg = '';
            $this->http_code = $http_code;
            return true;
        }

        return false;
    }

    private function reset()
    {
        $this->errno = self::SUCCESS;
        $this->errmsg = '';
        $this->header = '';
        $this->headers = array();
        $this->body = '';
        $this->body_len = 0;
        $this->http_code = null;

    }
}


/* vim: set ts=4 sw=4 sts=4 tw=100 noet: */
?>
