import boto3
import botocore
import subprocess
import ast
import os
import send_email
import config

sqs = boto3.client('sqs')
s3 = boto3.resource('s3')

# Configure application Variables
queue_url = config.QUEUE_URL
scanFolder = config.SCAN_FOLDER
quarantineFolder = config.QUARANTINE_FOLDER

# Get Message
def getMessage():
	response = sqs.receive_message(
        	QueueUrl=queue_url,
        	AttributeNames=[
                	'av-scan-event'
        	],
        	MaxNumberOfMessages=1,
        	MessageAttributeNames=[
                	'All'
        	],
        	VisibilityTimeout=0,
        	WaitTimeSeconds=0
	)
	if 'Messages' in response:
		message = response['Messages'][0]
		body = ast.literal_eval(message['Body'])
		receipt_handle = message['ReceiptHandle']
		bucketName = body['Records'][0]['s3']['bucket']['name']
		obj = body['Records'][0]['s3']['object']['key']
		deleteMessage(receipt_handle)
		getFile(bucketName, obj)

# Remove message from queue
def deleteMessage(receipt_handle):
	sqs.delete_message(
       		QueueUrl=queue_url,
       		ReceiptHandle=receipt_handle
	)

# Get object from bucket
def getFile(bucketName, obj):
	bucket = s3.Bucket(bucketName)
	exists = True
	objName = obj.split('/')[-1]

	try:
        	bucket.download_file(obj, scanFolder + objName)
		scanFile(objName)
	except botocore.exceptions.ClientError as e:
        	error_code = int(e.response['Error']['Code'])
        	if error_code == 404:
                	exists = False
# Scan file
def scanFile(objName):
	proc = subprocess.Popen(['clamscan', scanFolder + objName], stdout=subprocess.PIPE)
	output = proc.stdout.read().split('\n')
	line = output[0].split(' ')

	if line[1] != 'OK':
        	print 'Sending SNS Message'
		os.rename(scanFolder + objName, quarantineFolder + objName)
		send_email.sendEmail('A virus has been detected in file ' + objName)
	else:
		os.remove(scanFolder + objName)

# Poll SQS Queue
while True:
	getMessage()
