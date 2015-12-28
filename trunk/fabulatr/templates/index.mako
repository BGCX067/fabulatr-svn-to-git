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
<link href="/favicon.ico" rel="shortcut icon" />
<link rel="stylesheet" href="/fabulatr.css" type="text/css" />
<script type="text/javascript" src="jquery.js"></script>

</head>

<script type="text/javascript">

// define this outside all
// functions so it's globally available
var errors = " ";

function validateEmail(){
	$("#errors").hide();
	// get local instances or init
	var email	= $("#Field8").attr("value");
	var validEmail  = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;

	// assume no erros
	errors = " ";


	// check if for valide email good
	if (!validEmail.test(email)){
		errors = "<p><span style=\"color:red\">Ooop!</span> That email doesn't quite look right.  Please correct it.</p>";
	}

	if (errors != " "){
		$("#errors").html( errors );
		$("#errors").show();
		return false;
	} else {
		$("#Field8").hide();
		$("#title8").hide();
		$("#saveForm").hide();
		$("#formLoading").show();
		document.sendemail.submit();
		return false;
	}
}


</script>

<body>
<div id="container">

<h1>Fabulatr</h1>

<form name="sendemail" class="wufoo topLabel" enctype="multipart/form-data" method="post" action="/done">
<div class="info">
<h2>EC2 Fabulatr</h2>
<p>Fill out the form below and I'll email you a key and some instructions telling you how to login to your very own EC2 instance.  Is this awesome or what?</p>
</div>

<ul>
<li id="fo1li0"
class="   " >

<label class="desc" id="title8" for="Field8">
Email
</label>

<div>
<input id="Field8" class="field text large" name="to_address" tabindex="3" type="text" maxlength="255" value="" /> 
</div>

</li><li class="buttons">
<input id="saveForm" class="btTxt" type="submit" tabindex="6" value="Submit" onclick="validateEmail(); return false;" />
</li>
<li id="formLoading" style="display:none;">
<p style="color:white;">Submitting Email</p> <img src="/spinner.gif">
</li>
</ul>

</form>

<div id="errors">
</div>

</div><!--container-->
</body>
</html>

