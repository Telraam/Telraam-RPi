<?php session_start(); ?>

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
$versionFile='/home/pi/Telraam/Scripts/telraam_version.json';

$version='';
$string = file_get_contents($versionFile);
if ($string !== false) {
    $json_a = json_decode($string, true);
	if ($json_a !== null) {
		$version=$json_a['version'];
	}
}

//DB connection
$serverName = "localhost";
$userName = "pi";
$password = "pi";
$dbName = "telraam";
$currentWifiSsid=null;
$sendBackground=true;
$dbUpdated=false;

$connection = new mysqli($serverName, $userName, $password, $dbName);
if ($connection->connect_error) {
	echo("<div class='error'>". $language["wifi_db_error"] . $conn->connect_error . "</div>");
}
else{
	// save a connection to the database & make a new connection in 10 seconds
	if (isset($_POST[conn_submit])) {
		$wifi_ssid=null;
		if(trim($_POST['wifi_ssid'])==='custom-network-selection'){			//Own custom network, not in the network list
			$wifi_ssid = trim($_POST['custom_wifi_name']);
		}
		else{
			$wifi_ssid = trim($_POST['wifi_ssid']);
		}

		$wifi_pwd = trim($_POST['wifi_pwd']);

		$sqlStatement = "TRUNCATE connection;";
		$connection->query($sqlStatement);

		$sql="INSERT INTO connection(wifi_ssid,wifi_pwd) VALUES (?,?);";
		$stmt=$connection->prepare($sql);
		$stmt->bind_param("ss", $wifi_ssid, $wifi_pwd);
		$stmt->execute();
		
		$dbUpdated=true;
	}

	// check for existing connections
	$sqlStatement = "SELECT wifi_ssid, wifi_pwd FROM connection;";
	$result = $connection->query($sqlStatement);

	if ($result->num_rows > 0) {
		$row=$result->fetch_assoc();			// fetch only the first result
		$currentWifiSsid=$row["wifi_ssid"];
	}


	// check for send_background setting
	if (isset($_POST[conn_submit])) {

		$sqlStatement=null;
		if(trim($_POST['send_background'])){			//checkbox is on
			$sqlStatement="update settings set value=true where setting='send_background'";
		}
		else{											//checkbox is off
			$sqlStatement="update settings set value=false where setting='send_background'";
		}
		$connection->query($sqlStatement);
	}

	$sqlStatement = "SELECT value FROM settings where setting='send_background';";
	$result = $connection->query($sqlStatement);

	if ($result->num_rows > 0) {
		$row=$result->fetch_assoc();			// fetch only the first result

		if($row['value']){
			$sendBackground=true;
		}
		else{
			$sendBackground=false;
		}
	}
}


// set the uptime as
$upIime = explode(" ",exec('cat /proc/uptime'));
$upTimeRest = (60 * 10) - $upIime[0] % (60 * 10);
?>


<html>
	<head>
		<title><?php echo $language["welcome_title"]; ?></title>
		<meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="../css/design.css" />
		<script src="../lib/jquery-3.5.1.min.js"></script>

	</head>
	<body>
		<?php if ($version!=='') { ?>
			<div class="version">Telraam Image: <?php echo $version; ?></div>
		<?php } ?>
        <ul class="lang-link">
            <li><a href="?lang=nl">nl</a></li>
            <li><a href="?lang=fr">fr</a></li>
            <li><a href="?lang=en">en</a></li>
            <li><a href="?lang=si">si</a></li>
            <li><a href="?lang=es">es</a></li>
            <li><a href="?lang=de">de</a></li>
        </ul>
		<div class="box">
	  <div class='success-notifcation' <?php echo ($dbUpdated==true) ? 'style="display: block"' :'style="display: none"';?>><?php echo $language["save_success"]; ?></div>


      <div class="sticky">
          <h2><?php echo $language["your_serial_number"]; ?></h2>
          <div class='number'>&nbsp;<?php echo $readableMACAddressDec . $checkModulo ?></div></p>
      </div>

			<h2><?php echo $language["livestream_title"]; ?></h2>
			<p><?php echo $language["livestream_txt"]; ?><p>
			<?php
				//echo "<img src=\"http://192.168.254.1:8000/stream.mjpg\" width=\"100%\" heigth=\"500\"/>";
			?>
			<img src="http://192.168.254.1:8000/stream.mjpg" width="100%" heigth="500"/>

			<br />
			<br />
			<hr />

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
                            <option value="no-selection" selected="selected"><?php echo $language["wifi_network"]; ?></option>
                            <option value="custom-network-selection"><?php echo $language["add_custom_network"]; ?></option>
                    </select>
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
                    <input type="TEXT" name="wifi_pwd" value="">
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
                    <input type="Submit" name="conn_submit" value="<?php echo $language["save"]; ?>">
                </div>
			</form>
            <script>
                var dropdown = document.getElementById('js-wifi-dropdown');
                dropdown.onchange = function () {
                    if(this[this.selectedIndex].value == "custom-network-selection"){
                        document.getElementById('custom-network').style.display='block';
                    }else {
                        document.getElementById('custom-network').style.display='none';
                    }
                };

				//show or hide the more info text block
				document.getElementById("more_info_u").addEventListener("click",
					function() {
						this.classList.toggle("active");
						var content = document.getElementById("more_info_txt");
						if (content.style.display === "block") {
						  content.style.display = "none";
						} else {
						  content.style.display = "block";
						}
					}
				);

				//make sure clicking more info does not toggle the checkbox
				document.querySelector('.no_toggle_checkbox').addEventListener('click', (e)=>{
				   e.preventDefault();
				}, false);

            </script>
			<p>
				<?php
					if ($currentWifiSsid!=null) {
							// show saved connection
							echo "<h2>".$language["current_wifi_setup"]."</h2>";
							echo "<h3>".$language["wifi_data"]."</h3>";
							echo $language["wifi_ssid"] . $currentWifiSsid. "<br>".$language["password"]." ***<br>";

							echo "<p id='count_down_up_time'></p>";
					}
				?>
			</p>
		</div> <!-- end box -->
		<script>
			var timer_string="<?php echo $language["connection_timer"]; ?>";
			var seconds = "<?php echo $upTimeRest;?>";
			var minutes = Math.floor(seconds / 60);
			seconds = seconds % 60;


			// update the countdown every 1 second
			var dummy = setInterval(function() {

				// display the result in the element with id="count_down_up_time"

				current_timer=timer_string.replace("{minutes}", minutes)
				current_timer=current_timer.replace("{seconds}", seconds)
				document.getElementById("count_down_up_time").innerHTML = current_timer;
				//document.getElementById("count_down_up_time").innerHTML = "Je telraam zal over <b>" + minutes + "</b> minuten en  <b>" + seconds + "</b> seconden een verbinding maken met het ingestelde wifi netwerk...";


				// update interval
				seconds = seconds - 1;

				if (seconds < 0) {
					seconds = 59;
					minutes = minutes - 1;
				}

				// reset the timer when the countdown has finished
				if (minutes < 0) {
					minutes = 9;
				}


			}, 1000);


			//get wlan list from jquery get
			$.get("wlan_list.php", function(data, status){
				var ssid_arr = JSON.parse(data);
				var select = document.getElementById("js-wifi-dropdown");
				var currentWifiSsid = "<?php echo $currentWifiSsid; ?>";

				if(currentWifiSsid!='' && !ssid_arr.includes(currentWifiSsid)){
					ssid_arr.unshift(currentWifiSsid);				//add at the top of the array
				}

				for(var i = 0; i < ssid_arr.length; i++) {
					var el = document.createElement("option");
					el.textContent = ssid_arr[i];
					el.value = ssid_arr[i];
					select.appendChild(el);

					if(currentWifiSsid==ssid_arr[i]){
						el.selected=true;
					}
				}
			});

		</script>
	</body>
</html>
