<?php
	# get the epoch date from the url and set the date on the telraam with that date -> ontherwise the https online ping can fail because the certificate might be invalid

	$t=$_GET["t"];
	
	if($t!=null and is_numeric($t)){
		$t=$t/1000;					#convert to epoch in seconds
		
		exec('sudo date -s "@'.$t.'"', $output);
	}

	#return only the location
	header('Content-Type: application/json');
	echo json_encode(array('location'=>'telraam'));
	
?>
