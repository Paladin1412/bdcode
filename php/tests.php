<?php
 
function iterTree($data) {
 $retData = array();
 $data = json_decode($data, true);
 if (!is_array($data) && empty($data)) {
 echo 'error !' ."n"; 
 } else {
 $queue = array();
 foreach ($data as $field => $value) {
 $queue[] = $field; 
}
 $head = 0;
 $tail = count($queue);
 while ($head < $tail) {
 $field = $queue[$head++];
 $path = explode("/", $field);
 $tmpData = &$data; 
 foreach ($path as $key => $ph) {
 $tmpData = &$tmpData[$ph];
}
 if (is_array($tmpData) && !empty($tmpData)) {
 $newField = $field; 
 foreach ($tmpData as $curField => $curValue) {
 $newField = $field . '/' . $curField;
 $queue[$tail++] = $newField;
}
 } else {
 $retData[] = $field; 
}
}
}
 return $retData;
}
 
//测试数据
$data = file_get_contents("http://restapi.ele.me/v1/restaurants?extras%5B%5D=food_activity&extras%5B%5D=restaurant_activity&extras%5B%5D=certification&fields%5B%5D=id&fields%5B%5D=name&fields%5B%5D=phone&fields%5B%5D=promotion_info&fields%5B%5D=name_for_url&fields%5B%5D=flavors&fields%5B%5D=is_time_ensure&fields%5B%5D=is_premium&fields%5B%5D=image_path&fields%5B%5D=rating&fields%5B%5D=is_free_delivery&fields%5B%5D=minimum_order_amount&fields%5B%5D=order_lead_time&fields%5B%5D=is_support_invoice&fields%5B%5D=is_new&fields%5B%5D=is_third_party_delivery&fields%5B%5D=is_in_book_time&fields%5B%5D=rating_count&fields%5B%5D=address&fields%5B%5D=month_sales&fields%5B%5D=delivery_fee&fields%5B%5D=minimum_free_delivery_amount&fields%5B%5D=minimum_order_description&fields%5B%5D=minimum_invoice_amount&fields%5B%5D=opening_hours&fields%5B%5D=is_online_payment&fields%5B%5D=status&fields%5B%5D=supports&fields%5B%5D=in_delivery_area&geohash=wx4g07j0w1v7&is_premium=0&limit=1000&offset=24&type=geohash");
 
$ret = iterTree($data);
print_r($ret);
