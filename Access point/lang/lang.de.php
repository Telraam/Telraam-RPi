<?php
	$language['welcome_title'] = "Willkommen bei deinem Telraam!";
	$language["welcome_txt"] = "Notiere dir die <b>einmalige Seriennummer deines Telraams</b>. Du benötigst diese Nummer, um den Registrierungsprozess abzuschließen und um deine eigenen Verkehrsdaten einzusehen.";
	$language["livestream_title"] = "Livestream des Sensors";
	$language["livestream_txt"] = "Richte die Kamera aus, indem du sie leicht neigst, so dass die Straße im Bild <b>zentriert</b> ist.";
	$language['serial_number'] = "Seriennummer";
	$language['your_serial_number'] = "Ihre Seriennummer";
	$language["connect_title"] = "Verbinde dein Telraam mit dem Internet";
	$language["connect_txt"] = "Fülle die untenstehenden Felder aus. Dadurch kann dein Telraam über dein <b>Wi-Fi-Netzwerk</b> eine Verbindung zum Internet herstellen. Bitte achte darauf, daß du Schreibfehler vermeidest.";
	$language["wifi_network"] = "Wi-Fi-Netzwerk";
	$language["wifi_pwd"] = "Wi-Fi-Kennwort";
	$language["save"] = "Speichern";
	$language["wifi_db_error"] = "Es gab ein Problem mit der Verbindung zur WiFi-Datenbank auf der Raspberry Pi:";
	$language["current_wifi_setup"] = "Aktuelle Wifi-Einrichtung";
	$language["wifi_data"] = "Unten finden Sie die gespeicherten wifi-Daten";
	$language["wifi_ssid"] = "SSID (Name Ihres Wifi-Netzes):";
	$language["password"] = "Kennwort:";
	$language["connection_timer"] = "Ihr Telraam wird sich in <b>{minutes}</b> Minuten und <b>{seconds}</b> Sekunden mit dem eingestellten WiFi-Netzwerk verbinden...";
	$language["add_custom_network"] = "Fügen Sie ein benutzerdefiniertes WiFi-Netzwerk hinzu";
	$language["custom_network"] = "Eigener, angepasster WiFi-Netzwerkname";
	$language["send_background"]= "Telraam darf täglich ein Bild meiner Straße aufbewahren, so dass ich die Kameraposition bei Bedarf leicht überprüfen kann";
	$language["more_info"]="Mehr Informationen";
	$language["send_background_more_info"]="<p>Wenn Sie dieses Kästchen ankreuzen, können Sie das aktuellste Hintergrundbild Ihres Telraams in Ihrem eigenen Dashboard konsultieren und Sie können leicht überprüfen, ob die Kamera noch richtig ausgerichtet ist, ohne dass Sie die Verbindung zu Ihrem Telraam erneut herstellen müssen. Telraam macht einmal täglich ein solches Hintergrundfoto und bewahrt es 1 Monat lang in der Datenbank auf.</p><p>Um die Privatsphäre der Passanten zu gewährleisten, wenden wir 2 Techniken an:<ol><li>Wir nehmen ein Hintergrundbild für einen Zeitraum von 30 Sekunden auf und nehmen den Medianwert pro Pixel; aus diesem Grund sind alle sich bewegenden Objekte nicht sichtbar.</li><li>Wir verzerren das Bild auf eine (extrem) niedrige Auflösung durch Pixelierung (https://en.wikipedia.org/wiki/Pixelation).</li></ol></p><p>Wenn Sie dies nicht wünschen, können Sie trotzdem das Kamerabild Ihres Telraams überprüfen, indem Sie sich nur manuell über das Telraam-Wifi-Netzwerk mit Ihrem Telraam-Gerät verbinden: https://telraam.zendesk.com/hc/de/articles/360026468392-Camera-position-checking-images.</p>";
	$language["save_success"]="Ihre Einstellungen wurden erfolgreich gespeichert!";
?>
