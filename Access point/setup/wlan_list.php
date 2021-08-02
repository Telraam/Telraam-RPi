<?php
	//wifi networks
	$ssidArr=array();
	exec('sudo iwlist wlan0 scan', $output);
	foreach($output as $line){
		//echo $line;
		if (preg_match('/ESSID:"(.+)"/', $line, $matches)) {
			$ssidArr[$matches[1]]=true;			//use associative array -> every ssid only 1 time in the array
		}
	}
	uksort($ssidArr, 'strcasecmp');						//sort on keys, case insensitive
	
	echo json_encode((array_keys($ssidArr)));
?>