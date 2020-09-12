import boto3
import os
AWS_ACCESS_KEY_ID =os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
AWS_BUCKET_NAME = 'lokiproject'
client = boto3.client(
	's3',
	aws_access_key_id = AWS_ACCESS_KEY_ID,
	aws_secret_access_key = AWS_SECRET_KEY,
	region_name = 'ap-south-1'
)

def get_upload_url(filename):
	try:
		upload_url= client.generate_presigned_url(
			ClientMethod = 'put_object',  
			Params = {
				'Bucket': AWS_BUCKET_NAME,
				'Key': filename,
			}, 
			ExpiresIn = 600,
		)
		return upload_url
	except Exception as e:
		print("Error at get_upload_url ",e)
		return 0

def get_download_url(filename):
	try:
		download_url= client.generate_presigned_url(
		ClientMethod = 'get_object',  
		Params = {
			'Bucket': AWS_BUCKET_NAME,
			'Key': filename,
		}, 
		ExpiresIn = 3600,
	)
		return download_url
	except Exception as e:
		print("Error at get_download_url ",e)
		return 0

def delete_file(filename):
	try:
		client.delete_object(Bucket=AWS_BUCKET_NAME,Key=filename)
		return 1
	except Exception as e:
		print(" Error at s3_handle.delete_file ",e)
		return 0
# print(get_download_url("hello_world.jpg"))
# print(delete_file("hello_world.jpg"))
# print(get_upload_url("hello_world.jpg"))
