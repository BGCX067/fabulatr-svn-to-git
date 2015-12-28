<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>

<title>
EC2 Fabulatr
</title>

<!-- Meta Tags -->
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="robots" content="index, follow" />
<script type="text/javascript" src="jquery.js"></script>
<link href="/favicon.ico" rel="shortcut icon" />
<link rel="stylesheet" href="/fabulatr.css" type="text/css" />


<script type="text/javascript">
//<![CDATA[

	var keysig;
	var instanceStarted = false;
	var checkStarted  = /^(.*)server is running(.*)$/;

	// url parser we stole from somewhere
	jQuery.query = function(s) {
	    var r = {};
	    if (s) {
		var q = s.substring(s.indexOf('?') + 1); // remove everything up to the ?
		q = q.replace(/\&$/, ''); // remove the trailing &
		jQuery.each(q.split('&'), function() {
		    var splitted = this.split('=');
		    var key = splitted[0];
		    var val = splitted[1];
		    // convert numbers
		    if (/^[0-9.]+$/.test(val)) val = parseFloat(val);
		    // convert booleans
		    if (val == 'true') val = true;
		    if (val == 'false') val = false;
		    // ignore empty values
		    if (typeof val == 'number' || typeof val == 'boolean' || val.length > 0) r[key] = val;
		});
	    }
	    return r;
	};

	// do an ajax call to check on the server
	function check_server() {
		update_status_var_and_form();

		if (!instanceStarted){
			$.get("/check_server_start?keysig=" + keysig, function(data){ 
				$("#starting").html(data);
			});

			setTimeout(function(){check_server();}, 10000);
		}
	}

	$(document).ready(function(){
		// get our key from the URL
		var query = $.query(location.search);
		for (var k in query) {
			if (k == 'keysig') {
				keysig = query[k];
			}
		}
		check_server();
	});

	function update_status_var_and_form(){
		var started_text = $("#starting").html();
		instanceStarted = false;
		if (checkStarted.test(started_text)){
			instanceStarted = true;

		}


	}

//]]>
</script>

</head>

<body>
<div id="container">
<h1>Fabulatr</h1>

<div style="background-color: #333333; padding: 20px; color: white;">
<div class="info" >
<h2>EC2 Fabulatr</h2>
<p>This page will update when your instance is up and runnning.  In the meantime, make sure you've saved the key I emailed you into a file called <strong>fabulatr.pem</strong>.</p>
<p>
If you want to sign up under a different email address, then please <a href="/">start over</a>.
</p>

</div>

<div style="color:white;" id="starting">

<p>Checking on instance...<br/><img src="spinner.gif"></p>

</div>

</div>
</div><!--container-->
</body>
</html>

