import boto3
from botocore.exceptions import ClientError

client = boto3.client('s3')
lambda_client = boto3.client('lambda')

lambda_function = 'arn:aws:lambda:ap-south-1:577683050298:function:cloudtrail'  # place your lambda function here
s3_bucket_name = 'ct-s3-test-1'  # place your bucket here

try:
    lambda_policy = lambda_client.add_permission(
        FunctionName=lambda_function,
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        StatementId='TrustS3ToInvokeMyLambdaFunction',
        SourceArn="arn:aws:s3:::{}".format(s3_bucket_name),
    )
    print("Lambda permissions added")
except ClientError as e:
    print("Permission already exists Exits")

response = client.put_bucket_notification_configuration(
    Bucket=s3_bucket_name,
    NotificationConfiguration={'LambdaFunctionConfigurations': [
        {
            'LambdaFunctionArn': lambda_function,
            'Events': ['s3:ObjectCreated:*']
        }
    ]})

print("Attached S3 bucket to Lambda Function")
