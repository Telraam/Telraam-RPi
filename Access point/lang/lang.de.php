<?php
	$language['welcome_title'] = "Willkommen bei deinem Telraam!";
	$language["welcome_txt"] = "Notiere dir die <b>einmalige Seriennummer deines Telraams</b>. Du benötigst diese Nummer, um den Registrierungsprozess abzuschließen und um deine eigenen Verkehrsdaten einzusehen.";
	$language["livestream_title"] = "Livestream des Sensors";
	$language["livestream_txt"] = "Richte die Kamera aus, indem du sie leicht neigst, so dass die Straße im Bild <b>zentriert</b> ist.";
	$language['serial_number'] = "Seriennummer";
	$language['your_serial_number'] = "Ihre Seriennummer";
	$language["connect_title"] = "Verbinde dein Telraam mit dem Internet";
	$language["connect_txt"] = "Dadurch kann dein Telraam über dein <b>Wi-Fi-Netzwerk</b> eine Verbindung zum Internet herstellen. Bitte achte darauf, daß du Schreibfehler vermeidest.";
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
	$language["service_not_running"]="telraam_ap_control_service nicht gefunden";
	$language["interrupt_sent"]="Verbindung wird hergestellt";
	$language["connect_now"]="Jetzt verbinden";
	$language["save_and_connect"] = "Speichern und verbinden";
	$language["connection_error"] = "Verbindung zum TELRAAM-Hotspot verloren";
	$language["making_the_connection_title"] = "Verbinden mit Ihrem Wifi";
	$language["making_the_connection_info"] = "Wir prüfen, ob die Verbindung mit den von Ihnen eingegebenen WLAN-Zugangsdaten erfolgreich ist. Dies dauert etwa zwei Minuten.";
	$language["making_the_connection_btn"] = "Verbinden Sie sich erneut mit dem TELRAAM-Hotspot und versuchen Sie es erneut mit neuen WLAN-Daten.";
	$language["progress_note_ok"] = "Die Wifi-Anmeldedaten scheinen in Ordnung zu sein! Die Installation ist abgeschlossen.";
	$language["progress_note_nok"] = "Wir konnten keine Wi-Fi-Verbindung herstellen. Es ist möglich, dass die Verbindung erfolgreich war. Sie können dies bei den weiteren Installationsschritten im Dashboard überprüfen.";
	$language["wifi_network_loading"] = "Wir sehen uns an, welche Wifi-Netzwerke verfügbar sind. Warten Sie...";
	$language["wifi_network_loading_short"] = "Suche nach WiFi-Netzwerken";
	$language["connection_active"] = "Die Verbindung mit dem TELRAAM Hotspot ist aktiv";
	
	$language["tab_camera_image"] = "Positionierung";
	$language["tab_wifi"] = "Wifi-Verbindung";
	$language["go_to_telraam"] = "telraam.net";
	$language["edit-password"] = "Kennwort anpassen";

?>
