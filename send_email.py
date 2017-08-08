from smtplib import SMTP
from smtplib import SMTPException
from email.mime.text import MIMEText
import config

def listToStr(lst):
	return ','.join(lst)

def sendEmail(content):
	message = MIMEText(content, config.TEXT_SUBTYPE)
	message['Subject'] = config.EMAIL_SUBJECT
	message['From'] = config.EMAIL_FROM
	message['To'] = config.EMAIL_TO

	try:
		smtpConn = SMTP(config.MAIL_SERVER, config.MAIL_PORT)
		smtpConn.ehlo()
		smtpConn.starttls()
		smtpConn.ehlo()
		smtpConn.login(user=config.EMAIL_FROM, password=config.MAIL_PASSWORD)
		smtpConn.sendmail(config.EMAIL_FROM, config.EMAIL_TO, message.as_string())
		smtpConn.quit()
	except SMTPException as error:
		print "Error: unable to send email : {err}".format(err=error)

