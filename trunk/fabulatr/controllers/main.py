import logging
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from pylons import config
from boto.ec2.connection import EC2Connection

from fabulatr.lib.base import *

log = logging.getLogger(__name__)

class MainController(BaseController):

    def index(self):
        # Return a rendered template
        return render('/index.mako')

    def done(self):
    	try:
		to_address = request.params['to_address']
		conn = EC2Connection(config.get('aws_access_key'), config.get('aws_secret_access_key'))
		
		# create key if it doesn't exist
		found_keypair = False
		try:
			key_pair = conn.get_key_pair(to_address)	
			key_message = key_pair.material
			key_signature = key_pair.fingerprint
			found_keypair = True
		except:	
			key_pair = conn.create_key_pair(to_address)
			key_signature = key_pair.fingerprint
			key_message = key_pair.material
	except:
		return render('/ec2_error.mako')

	found_instance = False
	# check to see if we have an instance running with this keypair
	for reservation in conn.get_all_instances():
		for instance in reservation.instances:
			if to_address in instance.key_name:
				if str(instance.state) == u'running':
					found_instance = True		
					# get the instance's hostname
					fqdn = instance.dns_name

	from_name = config.get('from_name')
	from_address = "%s <%s>" % (from_name, config.get('from_address'))
	server_name = config.get('server_name')

	if found_instance and found_keypair:
		message = "Hi!\r\n\r\nYour instance is already running, and you should have an email with your keypair file in it.\r\n\r\nRemember, you'll needed to have saved the key I sent you to a file called fabulatr.pem.  If you are running Linux or OSX, you can do the following to connect to your server: \r\n\r\n'ssh -i fabulatr.pem root@%s'\r\n\r\nnCheers, \r\n\r\n%s\r\n\r\n" % (server_name, from_name)
	elif not found_instance and not found_keypair:
		message = "Hi!\r\n\r\nYour instance isn't running yet.  You can start it, and monitor its status by navigating to this page:\r\n\r\nhttp://%s/start?keysig=%s.\r\n\r\nWhile it's starting, go ahead save the attached key file in your home directory so you can get to it later.  Additionally, if you aren't using Windows, change the permissions of the file by doing a 'chmod 600 fabulatr.pem'.\r\n\r\nCheers, \r\n\r\n%s\r\n\r\n" % (server_name, key_signature, from_name)
	elif not found_instance and found_keypair:
		message = "Hi!\r\n\r\nI've already sent you a keypair to use to connect to your instance.  You can start your instance on this page: \r\n\r\nhttp://%s/start?keysig=%s\r\n\r\nYou should have another email with your keypair file in it.  You can refer to the status web page for more information.  \r\n\r\nCheers, \r\n\r\n%s\r\n\r\n" % (server_name, key_signature, from_name)

	# email them
	try:
		msg = MIMEMultipart()
		msg['From'] = from_address
		msg['To'] = to_address
		msg['Subject'] = "EC2 Server Instance"
		
		msg.attach(MIMEText(message))

		if key_message:
			part = MIMEBase('application', "octet_stream")
			part.set_payload(key_message)
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename="fabulatr.pem"')
			msg.attach(part)

		servername = config.get('smtp_server')
		server = smtplib.SMTP(servername)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login(config.get('smtp_login'), config.get('smtp_password'))
		server_fqdn = "foobar.com"
		server.sendmail(from_address, to_address, msg.as_string())
		server.quit()

	except:	
		# 
	 	return render('/error.mako')


	return render('/done.mako')

    def start(self):
	try:
		keysig = request.environ['QUERY_STRING'].split('=')[1]
		conn = EC2Connection(config.get('aws_access_key'), config.get('aws_secret_access_key'))
	except:
		return render('/error_start.mako')


	found_keypair = False
	# find the signature's key name 
	for keypair in conn.get_all_key_pairs():
		keyname = str(keypair).split(':')[1]
		key_pair = conn.get_key_pair(keyname)
		if key_pair.fingerprint == keysig:
			found_keypair = True

	if not found_keypair:
		return render('/error_start.mako')

	return render('/start.mako')

    def stop(self):
	try:
		keysig = request.environ['QUERY_STRING'].split('=')[1]
		conn = EC2Connection(config.get('aws_access_key'), config.get('aws_secret_access_key'))
	except:
		return render('/error_start.mako')


	found_keypair = False
	# find the signature's key name 
	for keypair in conn.get_all_key_pairs():
		keyname = str(keypair).split(':')[1]
		key_pair = conn.get_key_pair(keyname)
		if key_pair.fingerprint == keysig:
			found_keypair = True

	if not found_keypair:
		return render('/error_start.mako')

	return render('/stop.mako')
	
    # start server stuff
    def check_server_start(self):
	try:
		#keysig = request.params['keysig']
		keysig = request.environ['QUERY_STRING'].split('=')[1]
		conn = EC2Connection(config.get('aws_access_key'), config.get('aws_secret_access_key'))
	except:
		return "something is wrong!"

	found_keypair = False
	# find the signature's key name, again
	for keypair in conn.get_all_key_pairs():
		keyname = str(keypair).split(':')[1]
		key_pair = conn.get_key_pair(keyname)
		if key_pair.fingerprint == keysig:
			found_keypair = True
			to_address = keyname

	# check to see if we have an instance running with this keypair
	found_instance = False
	for reservation in conn.get_all_instances():
		for instance in reservation.instances:
			if to_address in instance.key_name:
				if str(instance.state) == u'running':
					# get the instance's hostname
					fqdn = instance.dns_name
					found_instance = True
					return ("Host: <strong>%s</strong><br/><br/>Your server is running and ready for connections!  Keep in mind that it may take 20-30 seconds to start the services on the box after it is up.<br/><br/><br/>Issue the following to connect via ssh with Linux or OSX:<br/><br/><strong>chmod 600 fabulatr.pem<br/>ssh -i fabulatr.pem root@%s</strong><br/><form method='post' action='/stop?keysig=%s'><ul><li class='buttons'><input id='stopInstance' class='btTxt' type='submit' tabindex='6' value='Stop Instance'/></li></ul></form>" % (fqdn, fqdn, keysig)) 
				elif str(instance.state) == u'pending':
					# do nothing
					found_instance = True
					return ("Instance is starting...<br/><img src='spinner.gif'/>") 

	# if we didn't find a running or pending instance, we start a new one
	if not found_instance:	
		instance = conn.get_image(config.get('ami_number'))
		image = instance
		reservation = image.run(key_name=to_address)
		return ("Instance is starting...<br/><img src='spinner.gif'/>") 

    # start server stuff
    def check_server_stop(self):
	try:
		keysig = request.environ['QUERY_STRING'].split('=')[1]
		conn = EC2Connection(config.get('aws_access_key'), config.get('aws_secret_access_key'))
	except:
		return "something is wrong!"

	found_keypair = False
	# find the signature's key name, again
	for keypair in conn.get_all_key_pairs():
		keyname = str(keypair).split(':')[1]
		key_pair = conn.get_key_pair(keyname)
		if key_pair.fingerprint == keysig:
			found_keypair = True
			to_address = keyname

	# check to see if we have an instance running with this keypair
	halted_instance = False
	shutting_instance = False
	for reservation in conn.get_all_instances():
		for instance in reservation.instances:
			instance.update()
			if to_address in instance.key_name:
				if str(instance.state) == u'terminated':
					# get the instance's hostname
					halted_instance = True
				elif str(instance.state) == u'shutting-down':
					# do nothing
					shutting_instance = True
				elif str(instance.state) == u'running':
					instance.stop()		
					shutting_instance = True

	if shutting_instance:
		return ("Halting instance...<br/><img src='spinner.gif'/>") 
	elif halted_instance:
		return ("<br/>Your server is shutdown!<br/><form method='post' action='/start?keysig=%s'><ul><li class='buttons'><input id='stopInstance' class='btTxt' type='submit' tabindex='6' value='Start Instance'/></li></ul></form>" % (keysig)) 
	else:
		return ("Halting instance...<br/><img src='spinner.gif'/>") 



    def serverinfo(self):
        import cgi
	import pprint
	c.pretty_environ = cgi.escape(pprint.pformat(request.environ))
	c.name = ''
	return render('/serverinfo.mako')
