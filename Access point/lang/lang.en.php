<?php
	$language['welcome_title'] = "Welcome to your Telraam! ";
	$language["welcome_txt"] = "Write down the <b>unique serial number</b> of your Telraam. You will need this number, to complete the registration process and view your own traffic data. ";
	$language["livestream_title"] = "Livestream of the sensor";
	$language["livestream_txt"] = "Aim the camera by gently tilting it so that the road is <b>centred</b> in the image:";
	$language['serial_number'] = "Serial Number";
	$language['your_serial_number'] = "Your Serial Number";
	$language["connect_title"] = "Connecting your Telraam to the internet";
	$language["connect_txt"] = "Fill in the fields below. Please take care and avoid writing errors. This allows your Telraam to connect to the internet through your <b>Wi-Fi network</b>. ";
	$language["wifi_network"] = "Wi-Fi network";
	$language["wifi_pwd"] = "Wi-Fi password";
	$language["save"] = "Save";
	$language["wifi_db_error"] = "There was a problem connecting to the wifi database on the Raspberry Pi:";
	$language["current_wifi_setup"] = "Current wifi setup";
	$language["wifi_data"] = "Below you will find the stored wifi data";
	$language["wifi_ssid"] = "SSID (name of your wifi network):";
	$language["password"] = "Password:";
	$language["connection_timer"] = "Your Telraam will connect in <b>{minutes}</b> minutes and <b>{seconds}</b> seconds to the set wifi network...";
	$language["add_custom_network"] = "Add custom wifi network";
	$language["custom_network"] = "Own customised network name";
	$language["send_background"]= "I'm allowing Telraam to keep a daily picture of the view on my street, so I can easily check the camera position if necessary";
	$language["more_info"]="More info";
	$language["send_background_more_info"]="<p>If you check this box, you can check the most recent background picture of your Telraam in your own dashboard, allowing you to easily check if the camera is still pointed correctly, without having to reconnect to your Telraam. Telraam will take such a background photo once a day and stores the photo in the database for 1 month.</p><p>To guarantee the privacy of passers-by, we apply 2 techniques:<ol><li>We take a background picture for a period of 30 seconds and take the median value per pixel; this will render all moving objects invisible.</li><li>We distort the image to (extremely) low resolution using pixelation (https://en.wikipedia.org/wiki/Pixelation).</li></ol></p><p>If you don't want Telraam to store a background image, you can still check the camera image of your Telraam, by connecting manually to your Telraam device via the Telraam wifi network: https://telraam.zendesk.com/hc/nl/articles/360026468392-Camera-position-checking-images.</p>";
	$language["save_success"]="Your settings were stored successfully!";
?>
