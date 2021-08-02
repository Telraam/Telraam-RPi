<html>
<head>
    <title>Telraam Install</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="css/design.css" />
</head>

<?php 
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

?>
<body class="splash">

<div class="box">

    <h1>Telraam Setup</h1>
    <div class="intro">Please select your language. You'll need to check the position of your camera, connect to the wifi and write down your serial number.</div>
    <div class="lang-box-container">
		<?php $now=time()  //add epoch time to urls to prevent caching?>
        <a href="setup/?lang=nl&t=<?php echo $now; ?>" class="lang-box">Dutch</a>
        <a href="setup/?lang=fr&t=<?php echo $now; ?>" class="lang-box">French</a>
        <a href="setup/?lang=en&t=<?php echo $now; ?>" class="lang-box">English</a>
        <a href="setup/?lang=si&t=<?php echo $now; ?>" class="lang-box">Slovenian</a>
        <a href="setup/?lang=es&t=<?php echo $now; ?>" class="lang-box">Spanish</a>
        <a href="setup/?lang=de&t=<?php echo $now; ?>" class="lang-box">German</a>
    </div>
   <div class="footer">
        <div class='number'>&nbsp;<?php echo $readableMACAddressDec . $checkModulo ?></div></p>
    </div>
 
    
</div> <!-- end box -->

</body>
</html>
