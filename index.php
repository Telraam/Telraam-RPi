<html>
	<head>
		<title>Welkom bij je Telraam!</title>
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<style>
			body {
				font-family: Arial;
				text-align: center;
			}
			h1, h2 {
				text-align: center;
				border: 0;
				letter-spacing: 2px;
				color: #a5acb9;
				margin: 0 0 30px 0;
			}
			h1 {
				font-size: 40px;
				line-height: 42px;
			}
			h2 {
				text-align: center;
				border: 0;
				font-size: 20px;
				line-height: 25px;
				letter-spacing: 2px;
				color: #a5acb9;
				margin: 50px 0 30px 0;
			}
			.box {
				margin: 50px 15px;
				background: #FFF;
				-webkit-box-shadow: 0px 5px 26px -2px #dce5ec;
				box-shadow: 0px 5px 26px -2px #dce5ec;
				border-radius: 10px;
				padding: 20px 20px 30px 20px;
			}
			.number {
				background: #e2eff1 ;
				border-radius: 20px;
				font-size: 25px;
				line-height: 25px;
				color: #69afb7;
				font-weight: bold;
				letter-spacing: 3px;
				padding: 20px;
				text-align:center;
			}
			input {
				margin: 0em;
				outline: none;
				-webkit-appearance: none;
				tap-highlight-color: #eeeeee;
				line-height: 1.21428571em;
				min-height: 3.75em;
				padding: 1em;
				font-size: 1em;
				background: #FFFFFF;
				border: 1px solid #eeeeee;
				color: rgba(0, 0, 0, 0.87);
				border-radius: 0.28571429rem;
				padding: 20px;
			}
			input[type="submit"], input[type="Submit"] {
				background-color: #69afb7;
				color: #FFFFFF;
			}
			hr {
				border: 0;
				clear: both;
				display: block;
				margin: 20px auto;
				text-align: center;
				width: 100%;
				background: rgba(1, 15, 30, 0.1);
				height: 1px;
				overflow: hidden;
				position: relative;
			}
			hr::before {
				animation-duration: 2s;
				animation-timing-function: ease;
				animation-iteration-count: infinite;
				animation-name: progress;
				background: #111;
				content: "";
				display: block;
				height: 1px;
				position: absolute;
				width: 80px;
			}
			.error {
				color: red;
			}
			@keyframes progress {
				0% {
					transform: translateX(0px);
				}
				100% {
					transform: translateX(1440px);
				}
			}
		</style>
	</head>
	<body>
		<div class="box">
			<h1>Welkom bij je Telraam!</h1>
			<p>Schrijf het volgende <b>uniek serienummer</b> op want je hebt het nodig om je Telraam data te bekijken op onze website:</p>
			<?php
				$macAddressHex = exec('cat /sys/class/net/wlan0/address');
				$macAddressDec = base_convert($macAddressHex, 16,10);
				$readableMACAddressDec = trim(chunk_split($macAddressDec, 4, '-'), '-');
				echo "<p><br /><div class='number'>&nbsp;&nbsp;&nbsp;&nbsp;" . $readableMACAddressDec . "</div></p>";
			?>

			<br />
			<hr />

			<h2>Live stream van de camera</h2>
			<p>Richt de camera zodanig dat de weg mooi <b>centraal</b> in beeld is:<p>
			<?php
				echo "<img src=\"http://192.168.254.1:8000/stream.mjpg\" width=\"100%\" heigth=\"500\"/>";
			?>

			<br />
			<br />
			<hr />

			<h2>Verbind je Telraam met het internet</h2>
			<p>Vul de volgende velden in zodat je Telraam zich via <b>je wifi netwerk</b> met het internet kan verbinden:</p>
			<br />
			<form name="conn_form" method="POST" action="index.php">
				<input type="TEXT" onfocus="if(this.value == 'wifi netwerk') {this.value='';}" name="wifi_ssid" value="wifi netwerk">
				<input type="TEXT" onfocus="if(this.value == 'wifi paswoord') {this.value='';}" name="wifi_pwd" value="wifi paswoord">
				<input type="Submit" name="conn_submit" value="Bewaar">
			</form>
			<p>
				<?php
					$serverName = "localhost";
					$userName = "pi";
					$password = "pi";
					$dbName = "telraam";

					$connection = new mysqli($serverName, $userName, $password, $dbName);
					if ($connection->connect_error) {
						die("<span class='error'>Er was een probleem bij het maken van de verbinding met de wifi databank op de Raspberry Pi:" . $conn->connect_error . "</span>");
					}

					// save a connection to the database & make a new connection in 10 seconds
					if (isset($_POST[conn_submit])) {
						$wifi_ssid = trim($_POST['wifi_ssid']);
					 	$wifi_pwd = trim($_POST['wifi_pwd']);

						$sqlStatement = "TRUNCATE connection;";
						$connection->query($sqlStatement);

						$sqlStatement = "INSERT INTO connection(wifi_ssid,wifi_pwd) VALUES ('". $wifi_ssid . "','" . $wifi_pwd . "');";
						$connection->query($sqlStatement);
					}

					// check for existing connections
					$sqlStatement = "SELECT wifi_ssid, wifi_pwd FROM connection;";
					$result = $connection->query($sqlStatement);

					// if it exists, connect to it after 10 minutes of uptime (this is governed by a system service, so here it is merely a countdown clock)
					if ($result->num_rows > 0) {
						// show save connections
						echo "<h2>Huidige wifi setup</h2>";
						echo "<h3>Hieronder vind je de opgeslagen wifi gegevens</h3>";
						while ($row = $result->fetch_assoc()) {
							echo "SSID (naam van je wifi netwerk): "  .$row["wifi_ssid"]. "<br>Paswoord: ***<br>";
						}

						// set the uptime as
						$upIime = explode(" ",exec('cat /proc/uptime'));
						$upTimeRest = (60 * 10) - $upIime[0] % (60 * 10);
						echo "<p id='count_down_up_time'></p>";
					}
				?>
			</p>
		</div> <!-- end box -->
		<script>
			var seconds = "<?php echo $upTimeRest;?>";
			var minutes = Math.floor(seconds / 60);
			seconds = seconds % 60;

			// update the countdown every 1 second
			var dummy = setInterval(function() {

				// display the result in the element with id="demo"
				if (minutes < 1) {
					document.getElementById("count_down_up_time").innerHTML = "Je telraam zal over <b>" + seconds + "</b> seconden een verbinding maken met het ingestelde wifi netwerk...";
				}
				else if (minutes == 1) {
					document.getElementById("count_down_up_time").innerHTML = "Je telraam zal over <b>" + minutes + "</b> minuut en <b>" + seconds + "</b> seconden een verbinding maken met het ingestelde wifi netwerk...";
				}
				else {
					document.getElementById("count_down_up_time").innerHTML = "Je telraam zal over <b>" + minutes + "</b> minuten en  <b>" + seconds + "</b> seconden een verbinding maken met het ingestelde wifi netwerk...";
				}

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
		</script>
	</body>
</html>
