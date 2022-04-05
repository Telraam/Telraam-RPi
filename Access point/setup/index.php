<!-- just for testing -->
<?php error_reporting(0); ?>
<?php session_start(); ?>


<html>
	<head>
		<title id="page_title"></title>
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="stylesheet" href="../css/design.css?version=5" />
		<script src="../lib/jquery-3.5.1.min.js"></script>
	</head>

<?php
//languages
if(isset($_GET['lang']) && in_array($_GET['lang'],['nl', 'en', 'si', 'es', 'de', 'fr'])) {
	$lang = $_GET['lang'];
	$_SESSION['lang'] = $lang;
} else {
	$lang = isset($_SESSION['lang']) ? $_SESSION['lang'] : 'en';
}
require_once("../lang/lang.".$lang.".php");


//mac adress and checksum
$macAddressHex = exec('cat /sys/class/net/wlan0/address');
$macAddressDec = base_convert($macAddressHex, 16,10);
$readableMACAddressDec = trim(chunk_split($macAddressDec, 4, '-'), '-');
$convert_arr=range('A', 'Z');
	//split into 2 chunks -> max integer on 32bit system is 2147483647
	//otherwise the modulo operation does work as expected
$chunk1=substr($macAddressDec, 0, 8);
$chunk2=substr($macAddressDec, 8);
$chunk1_mod=$chunk1 % 23;		//mod 23 because there are 26 letters
$chunk2_mod=$chunk2 % 23;
$checkModulo=$convert_arr[$chunk1_mod].$convert_arr[$chunk2_mod];

//read image version file
$versionFile='/home/pi/Telraam/Scripts/json/telraam_version.json';

$version='';
$string = file_get_contents($versionFile);
if ($string !== false) {
	$json_a = json_decode($string, true);
	if ($json_a !== null) {
		$version=$json_a['version'];
	}
}


// wifi vars
$wifiFile='/home/pi/Telraam/Scripts/json/telraam_wifi.json';

$currentWifiSsid=null;
$currentWifiPwd=null;
$sendBackground=true;
$credsUpdated=false;

// save wifi credentials to json file
if (isset($_POST['conn_submit'])) {
	$wifi_ssid=null;
	if(trim($_POST['wifi_ssid'])==='custom-network-selection'){			//Own custom network, not in the network list
		$wifi_ssid = trim($_POST['custom_wifi_name']);
	}
	else{
		$wifi_ssid = trim($_POST['wifi_ssid']);
	}

	$wifi_pwd = trim($_POST['wifi_pwd']);
	if(empty($wifi_pwd)){	
		$data=json_decode(file_get_contents($wifiFile),TRUE);											//no pwd given, resubmit of old wifi network
		$wifi_pwd = $data["wifi_pwd"];
	}

	$data = array("wifi_ssid"=>$wifi_ssid, "wifi_pwd"=>$wifi_pwd);
	file_put_contents($wifiFile, json_encode($data, JSON_PRETTY_PRINT));
	
	$credsUpdated=true;
}

// check for existing wifi credentials
$data=json_decode(file_get_contents($wifiFile),TRUE);
$currentWifiSsid=$data["wifi_ssid"];
$currentWifiPwd=$data["wifi_pwd"];
$currentWifiPwdHidden=str_repeat("•", strlen($currentWifiPwd));

// check for send_background setting
$settingsFile='/home/pi/Telraam/Scripts/json/telraam_settings.json';

if (isset($_POST['conn_submit'])) {
	$data=array();
	
	if(isset($_POST['send_background'])){			//checkbox is on
		$data['send_background']=true;
	}
	else{											//checkbox is off
		$data['send_background']=false;
	}
	file_put_contents($settingsFile, json_encode($data, JSON_PRETTY_PRINT));
}

// get current send_background setting
// check for existing wifi credentials
$data=json_decode(file_get_contents($settingsFile),TRUE);
$sendBackground=$data["send_background"];




// send interrupt to telraam_ap_control_loop service and try to connect to the wifi network
$interruptSent=false;
if (isset($_POST['conn_submit'])) {
	// get this pid for the telraam_ap_control_loop service
	exec('systemctl show --property MainPID --value telraam_ap_control_loop.service', $output);
	$pid=$output[0];
	
	if($pid==0){
		echo("<div class='error'>". $language["service_not_running"]."</div>");
	}
	else{
		// send SIGUSR1 signal to the telraam_ap_control_loop service
		exec('sudo kill -SIGUSR1 '.$pid, $output);
		$interruptSent=true;
	}
}
?>

<script>
	var currentWifiSsid = "<?php echo $currentWifiSsid; ?>";
	
	var progressBarStarted = false;
	var progressBarTimeSec = 120000;
	
	let mac = "<?php echo $macAddressDec ?>";
	let conn_location=null;
	let telraam_online = null;
	
	//set check_time when the connect button was clicked
	let check_time = null;
	if("<?php echo $interruptSent; ?>"){
		check_time=new Date().getTime()/1000;									//epoch in seconds
	}
	
	//set the title after the languages are loaded
	$("#page_title").html('<?php echo $language["welcome_title"]; ?>');
</script>
<script src="../js/main.js?version=5"></script>


	<body>
		<div class="connection-sticky">
			<div class='error' id="connection_hotspot_error" style="display: none">
				<img src="../images/warning.svg" height="12" width="12">
				<?php echo $language["connection_error"]; ?>
				<span class="js-refresh refresh">Refresh</span>
			</div>
			<div class='success' id="connection_hotspot_active" style="display: block">
				<div class="green-dot"></div><?php echo $language["connection_active"]; ?></div>
		</div>

		<div class="making-the-connection" style="display:none;">
			<h2><?php echo $language["making_the_connection_title"]; ?></h2>
			<span class="connection-info"><?php echo $language["making_the_connection_info"]; ?></span><br><br>
			<div id="progress-container">
				<div id="progress" class="waiting">
					 <dt></dt>
					 <dd></dd>
				 </div>
			</div>
			<div id="progress-note-ok" class="progress-note success-notifcation no-background" style="display:none;"><?php echo $language["progress_note_ok"]; ?></div>
			<div id="progress-note-nok" class="progress-note error" style="display:none;"><?php echo $language["progress_note_nok"]; ?></div>
			<div class="progress-close-button js-close-connection-modal" style="display: none">
				<?php echo $language["making_the_connection_btn"]; ?>
			</div>
			<div class="progress-close-button js-success-go-telraam go-telraam" style="display: none">
				<a href="https://www.telraam.net"><?php echo $language["go_to_telraam"]; ?></a>
			</div>

		</div>
		
		<?php if ($version!=='') { ?>
			<div class="version">Telraam Image: <?php echo $version; ?></div>
		<?php } ?>
		<ul class="lang-link">
			<?php $now=time() //add epoch time to urls to prevent caching?>
			<li><a href="?lang=nl&t=<?php echo $now; ?>">nl</a></li>
			<li><a href="?lang=fr&t=<?php echo $now; ?>">fr</a></li>
			<li><a href="?lang=en&t=<?php echo $now; ?>">en</a></li>
			<li><a href="?lang=si&t=<?php echo $now; ?>">si</a></li>
			<li><a href="?lang=es&t=<?php echo $now; ?>">es</a></li>
			<li><a href="?lang=de&t=<?php echo $now; ?>">de</a></li>
		</ul>
		<div class="box" <?php echo ($credsUpdated==true) ? 'style="display: block"' :'style="display: none"';?>>
			 <div class='success-notifcation' <?php echo ($credsUpdated==true) ? 'style="display: block"' :'style="display: none"';?>>
				 <?php echo $language["save_success"]; ?>
			 </div>
		</div>


	    <div class="sticky">
		  	<button class="tab-link first active " data-ref="camera-images"> ① <?php echo $language["tab_camera_image"]; ?></button>
			<button class="tab-link " data-ref="wifi">② <?php echo $language["tab_wifi"]; ?></button>

		  	<h3><?php echo $language["your_serial_number"]; ?></h2>
		  	<div class='number'>&nbsp;<?php echo $readableMACAddressDec . $checkModulo ?></div></p>
	  	</div>
	  
	  	<div class="content">
		   
		   <div class="tab-content tab-camera-images">
			   <h2><?php echo $language["livestream_title"]; ?></h2>
				<p><?php echo $language["livestream_txt"]; ?><p>
				<?php
					 //echo "<img src=\"http://192.168.254.1:8000/stream.mjpg\" width=\"100%\" heigth=\"500\"/>";
				?>
				 <img src="http://192.168.254.1:8000/stream.mjpg" class="camera" width="100%" heigth="300"/>
		   
				<br />
				<br />
				
			</div>  <!-- tab-camera-images -->
		   
			<div class="tab-content tab-wifi"  style="display:none">
			  
			
				
				<div class="entering-the-connection-info">
					
					<h2><?php echo $language["connect_title"]; ?></h2>
					<p><?php echo $language["connect_txt"]; ?></p>
					<br />
					<form name="conn_form" method="POST" action="index.php">
						<!--
						<input type="TEXT" onfocus="if(this.value == 'wifi netwerk') {this.value='';}" name="wifi_ssid" value="<?php echo $language["wifi_network"]; ?>">
						-->
						<label><?php echo $language["wifi_network"]; ?>:</label>
						<div class="select-container">
							<select name="wifi_ssid" id="js-wifi-dropdown">
								<?php if ($currentWifiSsid===null) { ?>
									<option selected="selected"><?php echo $language["wifi_network_loading_short"]; ?></option>
								<?php } else { ?>
									<option selected="selected"><?php echo $currentWifiSsid; ?></option>
								<?php } ?>
									<option value="custom-network-selection"><?php echo $language["add_custom_network"]; ?></option>
							</select>
						</div>
						<div class="loading-available-networks">
							<img src="../css/loading.svg" width="14"> <?php echo $language["wifi_network_loading"]; ?>
						</div>
						<div id="custom-network" style="display:none">
							<div>
								<label><?php echo $language["custom_network"]; ?>:</label>
							</div>
							<input type="TEXT" name="custom_wifi_name" value="">
						</div>
						<div id="wifi-pwd">
							<div>
								<label><?php echo $language["wifi_pwd"]; ?>:</label>
							</div>
                            <div class="wifi-pwd-field" style="display: <?php echo ((!empty($currentWifiPwd)) ? 'none' : 'block') ?>  ">
                                <input type="password" id="pass_log_id"" name="wifi_pwd">
                                <span toggle="#password-field" class="icon-field icon-eye toggle-password">Show/Hide</span>
                            </div>
                            <?php if(!empty($currentWifiPwd)) { ?>
                                <div class="wifi-pwd-field-exist">
                                    <div class="password-dots">
                                        <input type="text" value="<?php echo $currentWifiPwdHidden ?>" readonly></div>
                                    <div class="edit-password"><a href="#" class="js-edit-password"><?php echo $language["edit-password"]; ?></a></div>
                                </div>
                            <?php } ?>


                        </div>
		
						<div class="checkboxes">
							<label for="send_background_checkbox">
								<input type="checkbox" name="send_background" id="send_background_checkbox" <?php if($sendBackground){echo 'checked';} ?>>
								<span>
									<p><?php echo $language["send_background"]; ?></p>
									<p><u id="more_info_u" class="no_toggle_checkbox"><?php echo $language["more_info"]; ?></u></p>
								</span>
							</label>
						</div>
		
		
						<div class="more_info" id="more_info_txt">
						  <p><?php echo $language["send_background_more_info"]; ?></p>
						</div>
		
						<div class="submit-container">
							<input type="Submit" name="conn_submit" value="<?php echo $language["save_and_connect"]; ?>">
						</div>
					</form>
					 
					<form name="connect_now_form" method="POST" action="index.php">
					<?php
						if ($currentWifiSsid!==null && $currentWifiSsid!=='') {
								// show saved connection
								echo "<h2>".$language["current_wifi_setup"]."</h2>";
								echo "<h3>".$language["wifi_data"]."</h3>";
								echo $language["wifi_ssid"] . $currentWifiSsid. "<br>".$language["password"]." ***<br>";
						} else {
							
						}
					?>
					</form>
						
				</div> <!-- end entering-the-connection-info -->
					
			
			</div>  <!-- tab-wifi -->


			
		</div>  <!-- content -->
	

		
	</body>

</html>
	