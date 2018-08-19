import ConfigParser
import sys
import time
import poplib
import imaplib
import logging
import requests
import email
import json
import time
from email import parser

config = ConfigParser.RawConfigParser()

logging.basicConfig(filename='dapmail.log',level=logging.ERROR)
logger = logging.getLogger(__name__)

def get_timestring():
	timestring = time.strftime("%m/%d/%Y - %H:%M:%S")
	return timestring

def read_setting():
	config.read('dapmail.ini')
	global set_interval
	global set_separator
	global mail_type
	global mail_host
	global mail_port
	global mail_ssl
	global mail_user
	global mail_passwd
	global dap_base_uri
	global dap_core_uri
	global dap_port
	global dap_user
	global dap_passwd
	set_interval = config.getint('Settings','poll_interval') 
	set_separator = config.get('Settings','separator_char')
	mail_type = config.get('Mailserver','mail_type')
	mail_host = config.get('Mailserver','mail_host')
	mail_port = config.get('Mailserver','mail_port')
	mail_ssl = config.getboolean('Mailserver', 'mail_ssl')
	mail_user = config.get('Mailserver','mail_user')
	mail_passwd = config.get('Mailserver','mail_passwd')
	dap_base_uri = config.get('DAPNET','dap_base_uri')
	dap_core_uri = config.get('DAPNET','dap_core_uri')
	dap_port = config.get('DAPNET', 'dap_port')
	dap_user = config.get('DAPNET','dap_user')
	dap_passwd = config.get('DAPNET','dap_passwd')
	
def get_imapmail(mailhost):
	if mail_ssl == False:
		M = imaplib.IMAP4(mail_host,mail_port)
	if mail_ssl == True:
		M = imaplib.IMAP4_SSL(mail_host)
	try:
		M.login(mail_user,mail_passwd)
	except:
		logging.warn(get_timestring() + ' - Unable to log in to imap server')
		return
	M.select()
	result, data = M.uid('search',None,'ALL')
	for num in data[0].split():
		#get message with UID num
		result, msg = M.uid('fetch', num,'(UID RFC822)')
		message = email.message_from_string(msg[0][1])
		msg_list = message['Subject'].split(set_separator)
		if msg_list[0].upper() == 'DAPNET':
			#this seems to be a pager message, continue!
			msg_ric = create_list(msg_list[1].lower()) #call sign must be lower case
			msg_func = msg_list[2]
			msg_trx = create_list(msg_list[3].lower()) #transmitter group must be lower case
			msg_emr = msg_list[4]
			msg_txt = msg_list[5]
			send_page(msg_ric,msg_func,msg_trx,msg_emr,msg_txt)
	clean_imapmailbox()

	
def clean_imapmailbox():
	if mail_ssl == False:
		M = imaplib.IMAP4(mail_host,mail_port)
	if mail_ssl == True:
		M = imaplib.IMAP4_SSL(mail_host)
	M.login(mail_user,mail_passwd)
	M.select()
	typ, data = M.search(None, 'ALL')
	for num in data[0].split():
		M.store(num,'+FLAGS', '\\Deleted')
	M.expunge()
	M.close()
	M.logout()
	
def create_list(list_string):
	#function to remove any spaces and to split the string up based on commas
	return (list_string.replace(' ','').split(','))
	
def get_popmail(mailhost):
	if mail_ssl == False:
		M = poplib.POP3(mailhost,mail_port)
	if mail_ssl == True:
		M = poplib.POP3_SSL(mailhost,mail_port)
	try:
		M.user(mail_user)
		M.pass_(mail_passwd)
	except:
		logging.warn(get_timestring() + ' - Unable to log in to pop3 server')
		return		
	NumMessages = len(M.list()[1])
	messages = [M.retr(i) for i in range(1, NumMessages + 1)] 
	messages = ["\n".join(mssg[1]) for mssg in messages]
	messages = [parser.Parser().parsestr(mssg) for mssg in messages]
	#loop through messages
	for message in messages:
		msg_subj = message['subject']
		#check if message starts with DAPNET
		if msg_subj[:6].upper() == 'DAPNET':
			#this seems to be a pager message, continue!
			msg_list = msg_subj.split(set_separator)
			msg_ric = create_list(msg_list[1].lower()) #call sign must be lower case
			msg_func = msg_list[2]
			msg_trx = create_list(msg_list[3].lower())#transceiver group must be lower case
			msg_emr = msg_list[4]
			msg_txt = msg_list[5]
			send_page(msg_ric,msg_func,msg_trx,msg_emr,msg_txt)
	clean_popmailbox()
	M.quit()
	
def clean_popmailbox():
# remove emails from inbox
		M = poplib.POP3_SSL(mail_host,mail_port)
		M.user(mail_user)
		M.pass_(mail_passwd)
		poplist = M.list()
		if poplist[0].startswith('+OK'):
			msglist = poplist[1]
     		for msgspec in msglist:
     			msgnum = int(msgspec.split(' ')[0])
     			print "Deleting msg %d\r" % msgnum,
     			pop.dele(msgnum) 			

	
def send_page(msg_ric,func,trx,emr,msgtxt):
	full_uri = dap_base_uri + ':' + dap_port + "/" + dap_core_uri
	req = requests.post(full_uri,auth=(dap_user,dap_passwd),json={'text':msgtxt,'callSignNames':msg_ric,'transmitterGroupNames':trx,'emergency':emr})

def main_loop():
	while 1:
		#read config
		read_setting()
		if mail_type.lower() == 'pop3':
			get_popmail(mail_host)
		if mail_type == 'imap':
			get_imapmail(mail_host)
		#pause based on the number of seconds set in the config file
		time.sleep(set_interval)

if __name__ == '__main__':
	try:
		main_loop()
	except KeyboardInterrupt:
		print >> sys.stderr, '\nExiting by user request.\n'
		sys.exit(0)
