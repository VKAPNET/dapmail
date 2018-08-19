# dapmail
Send DAPNET pager messages via email

This script has been written to collect email and transfer those mails which meet requirements into DAPNET pager messages. To do so, the script only reads the email subject and screens it format. The subject line of an email should contain:

1. the keyword 'dapnet';
2. the callsign of the receiver(s);
3. the function bit 0, 1, 2 or 3 (although this is not used by the REST API);
4. the transmitter group(s) selected to send the message;
5. 'true' or 'false' to determine whether or not this is a priority / emergency message;
6. the message text.

All six fields mentioned above should be used in that particular order, separated by a separation character as determined by the settings in 'dapmail.ini'. This separation character is used by the script to chop the entire subject line into the necessary fields. Therefore a character which is not commonly used needs to be selected. Default this character is set to the pipe symbol |

A typical subject line which can be transfered into a DAPNET message looks like:

dapnet|pa0xyz|3|pa-all|False|This is the actual message body

Furthermore it's possible to send the message to multipe receivers via multiple transceiver groups:

dapnet|pa0xyz,dl3abc|3|pa-lb,dl-nw|False|Message to multiple receivers

For this purpose it's recommended to have a dedicated email address, as the script cleans up all messages at the end of the run. This mailadress can either be a GMail address or at any other service. As long as the mailserver supports either IMAP or POP3.

A typical setting for GMail via IMAP can look like this:

[Mailserver]
mail_type = imap
mail_host = imap.gmail.com
mail_port = 993
mail_ssl = true
mail_user = mypager@gmail.com
mail_passwd = my_5uper5ecretP@55WOrd

You also need your DAPNET credentials to be able to send out messages via the REST API of the DAPNET core. If you're a licensed radio amateur but you don't have an account, please be invited to raise a ticket at www.hampager.de
