<?php
	$language['welcome_title'] = "Bienvenue sur votre Telraam!";
	$language["welcome_txt"] = "Notez <b>le numéro de série unique</b> de votre Telraam. Vous en aurez besoin pour compléter l'enregistrement et pour visualiser vos propres données de trafic.";
	$language["livestream_title"] = "Diffusion en direct du capteur";
	$language["livestream_txt"] = "Orientez la caméra en l'inclinant doucement pour que la route soit bien <b>centrée</b> dans l'image. ";
	$language['serial_number'] = "Numéro de série";
	$language['your_serial_number'] = "Votre numéro de série";
	$language["connect_title"] = "Connecter votre Telraam à l'internet";
	$language["connect_txt"] = "Veuillez faire attention et éviter les erreurs d'écriture. De cette manière, votre Telraam pourra se connecter à l'internet par le biais de votre <b>réseau Wi-Fi</b>.";
	$language["wifi_network"] = "Réseau Wi-Fi";
	$language["wifi_pwd"] = "Mot de passe Wi-Fi";
	$language["save"] = "Sauvegarder";
	$language["wifi_db_error"] = "Il y a eu un problème de connexion à la base de données wifi sur le Raspberry Pi:";
	$language["current_wifi_setup"] = "Configuration wifi actuelle";
	$language["wifi_data"] = "Tu trouveras ci-dessous les données wifi stockées";
	$language["wifi_ssid"] = "SSID (nom de votre réseau wifi):";
	$language["password"] = "Mot de passe:";
	$language["connection_timer"] = "Ton Telraam se connectera en <b>{minutes}</b> minutes et <b>{seconds}</b> secondes au réseau wifi installé...";
	$language["add_custom_network"] = "Ajouter un réseau wifi personnalisé";
	$language["custom_network"] = "Nom de réseau wifi personnalisé";
	$language["send_background"]= "J'autorise Telraam à garder une image quotidienne de la vue dans ma rue, ce qui me permet de vérifier facilement la position de la caméra si nécessaire";
	$language["more_info"]="Plus d'infos";
	$language["send_background_more_info"]="<p>Si vous cochez cette case, vous pouvez vérifier l'image de fond la plus récente de votre Telraam dans votre propre tableau de bord, ce qui vous permet de vérifier facilement si la caméra est toujours correctement pointée, sans avoir à vous reconnecter à votre Telraam. Le Telraam prend une telle photo de fond une fois par jour et la conserve dans la base de données pendant un mois.</p><p>Pour garantir la confidentialité des passants, nous appliquons 2 techniques :<ol><li>Nous prenons une photo d'arrière-plan pendant une période de 30 secondes et nous prenons la valeur médiane par pixel ; cela rendra tous les objets en mouvement invisibles.</li><li>Nous déformons l'image à une résolution (extrêmement) basse en utilisant la pixellisation (https://en.wikipedia.org/wiki/Pixelation).</li></ol></p></p>Si vous ne souhaitez pas que Telraam stocke une image d'arrière-plan, vous pouvez toujours vérifier l'image de la caméra de votre Telraam, en vous connectant manuellement à votre appareil Telraam via le réseau wifi Telraam : https://telraam.zendesk.com/hc/fr/articles/360026468392-Camera-position-checking-images.</p>";
	$language["save_success"]="Vos paramètres ont été enregistrés avec succès !";
	$language["service_not_running"]="telraam_ap_control_service introuvable";
	$language["interrupt_sent"]="La connexion est en cours d'établissement";
	$language["connect_now"]="Connectez maintenant";
	$language["save_and_connect"] = "Sauvegarder et connecter";
	$language["connection_error"] = "Perte de la connexion au hotspot TELRAAM";
	$language["making_the_connection_title"] = "Se connecter à votre wifi";
	$language["making_the_connection_info"] = "Nous vérifierons si la connexion est réussie avec les informations d'identification wifi que vous avez saisies. Cela prend environ deux minutes.";
	$language["making_the_connection_btn"] = "Reconnectez au hotspot TELRAAM et réessayez avec de nouvelles données wifi.";
	$language["progress_note_ok"] = "Les données wifi semblent corrects! L'installation est terminée.";
	$language["progress_note_nok"] = "Nous n'avons pas pu établir de connexion Wi-Fi. Il est possible que la connexion ait réussi. Vous pouvez le vérifier dans les étapes suivantes de l'installation dans le dashboard.";
	$language["wifi_network_loading"] = "Nous allons voir quels réseaux wifi sont disponibles. Attendez...";
	$language["wifi_network_loading_short"] = "Recherche de réseaux WiFi";
	$language["connection_active"] = "La connexion avec le hotspot TELRAAM est active";
	
	$language["tab_camera_image"] = "Positionnement";
	$language["tab_wifi"] = "Connexion Wifi";
	
	$language["go_to_telraam"] = "telraam.net";
	$language["edit-password"] = "Ajuster le mot de passe";

?>
