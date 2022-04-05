$( document ).ready(function() {

	// ---------- tabs
	$( ".tab-link" ).click(function() {
		if (!$(this).hasClass('active')) {
			tab = $(this).attr('data-ref');
			// tabs
			$('.tab-link').removeClass('active');
			$(this).addClass('active');
			// tab content
			$('.tab-content').hide();
			$('.tab-'+tab).show();
		}
	});	
	// ----------- password
	$( ".toggle-password" ).click(function() {
		  $(this).toggleClass("closed");
		  var input = $("#pass_log_id");
		  if (input.attr("type") === "password") {
			input.attr("type", "text");
		  } else {
			input.attr("type", "password");
		  }
	});
	// ----------- edit existing password
	$( ".js-edit-password" ).click(function() {
		$('.wifi-pwd-field-exist').hide();
		$('.wifi-pwd-field').show();
	});
	
	// ----------- refresh page
	$( ".js-refresh" ).click(function() {
		location.reload();
	});
	
	// ----------- progress bar	
	function startProgressBar() {
		progressBarStarted = true;
		$(".making-the-connection").show();
		$('#progress-container').show();
		$("#progress").removeClass("done");
		$(".tab-link").addClass("disabled");
		
		 $({property:5}).animate({property: 100}, {
			duration: progressBarTimeSec,
			step: function() {
			  var percent = Math.round(this.property);
		
			  if(percent == 100) {
				  $('#progress').css('width',  '100%'); 
				  telraamIsSuccessFullConnectedOrNot()
			  }else{
				 $('#progress').show(); //show it.
				 $('#progress').css('width',  percent+"%"); //progress
			  }
			  
			  if(telraam_online===true){
                $(this).finish();
                $('#progress').css('width',  '100%'); 
              }
			},
			complete: function() {
				telraamIsSuccessFullConnectedOrNot()
			}
		});
			
	}
	
	// ----------- fade it out
	function disableEverything() {
		window.scrollTo(0, 0);
		$('body').css('cursor', 'not-allowed');
		$('.content').css('opacity', '0.4');
		
		$("input").prop('disabled', true);
		$(".tab-link").addClass("disabled");
		
		$('body').css('background', '#ddd');
		$('.sticky').css('background', '#ddd');
		$('.content').css('background', '#ddd');
	}
	
	// ----------- back to normal
	function enableEverything() {
		$("input").prop('disabled', false);
		$(".tab-link").removeClass("disabled");
		
		$('body').removeAttr("style");
		$('.sticky').removeAttr("style");
		$('.content').removeAttr("style");
	}
	
	// ----------- close modal
	$( ".js-close-connection-modal" ).click(function() {
		 $(".making-the-connection").hide();
		 $('#progress').css('width',  '0%'); 
		 $('.progress-close-button').hide();
		 $(".tab-link").removeClass("disabled");
		 $('#progress').removeClass('done');
		 $('#progress').addClass('successbar');
		 $('#progress').addClass('errorbar');
	});
	
	function telraamIsSuccessFullConnectedOrNot() {
		if (telraam_online === true) {
			$('#progress-note-ok').show();
			$('#progress').addClass('successbar');
			$('.connection-info').hide();
			$('.js-success-go-telraam').show();
		} else {
			$('#progress-note-nok').show();
			$('.js-close-connection-modal').show();
			$('#progress').addClass('errorbar');
		}
		$('#progress').css('width',  '100%'); 
		$('#progress').addClass('done');
		$('#progress').removeClass('waiting');
		$('#progress-container').hide();
	}

	// ---------- wifi	
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
	
	
	// conn_location, telraam_online and check_time should be declared before using the check_online function
	function check_online(){
		// console.log('checking online');
		let now=new Date().getTime()
		let url="http://telraam-online.s3.eu-central-1.amazonaws.com/json/online.json?t="+now;
		
		$.get(url, function(data, status){	
			conn_location=data['location'];
		})
		.fail(function() {
			conn_location='not connected';
		});
		if(check_time!==null && conn_location==='aws'){
			
			let url_api="https://telraam-api.net/v1/private/online/"+mac+"?t="+now;
			$.get(url_api, function(data, status){	
				// console.log(data);
				// console.log(data['timestamp']);
				
				if(check_time!==null && check_time<data['timestamp']){
					telraam_online=true;
					console.log('telraam is online');
					clearInterval(check_online_timer);
				}
				else{
					telraam_online=false;
				}
			})
			.fail(function() {
				console.log('Connection faled');
			});
		}
		
		// connected to internet and not clicked on the connect button -> probably lost connection to telraam hotspot
		if(conn_location!==null && (conn_location!='telraam' && check_time===null)){
			$('#connection_hotspot_error').show();
			$('#connection_hotspot_active').hide();
			disableEverything();
		} else {
			$('#connection_hotspot_error').hide();
			$('#connection_hotspot_active').show();
			enableEverything();
		}

	}
	let check_online_timer=setInterval(check_online, 5000);
	
	
	// clicked on the connect button and the progress bar has not been started allready
	if(check_time!==null && progressBarStarted!==true){
		startProgressBar();
	}	
	
	
	
	//get wlan list from jquery get  --> 
	$.get("../setup/wlan_list.php", function(data, status){
		
		var ssid_arr = JSON.parse(data);
		var select = document.getElementById("js-wifi-dropdown");
	
		for(var i = 0; i < ssid_arr.length; i++) {
			if(currentWifiSsid!=ssid_arr[i]){					// current ssid is added in setup/index.php
				var el = document.createElement("option");
				el.textContent = ssid_arr[i];
				el.value = ssid_arr[i];
				select.appendChild(el);
			}
		}
		
		$('.loading-available-networks').hide();
		
	});

});