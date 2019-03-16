import boto3
from botocore.exceptions import ClientError

ENABLE_LOG = False
lambda_function = 'arn:aws:lambda:ap-south-1:577683050298:function:cloudtrail'  # place your lambda function here
s3_bucket_name = 'ct-s3-test-1'  # place your bucket here

trail_name = 'EC2TrailAllRegions'
ct_client = boto3.client('cloudtrail')
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')

try:
    ct_client.create_trail(
        Name=trail_name,
        S3BucketName=s3_bucket_name,
        IncludeGlobalServiceEvents=True,
        IsMultiRegionTrail=True,
        EnableLogFileValidation=True,
    )
except ClientError as e:
    print("Trail with the name {} already Exists".format(trail_name))

events = ct_client.put_event_selectors(
    TrailName=trail_name,
    EventSelectors=[
        {
            'ReadWriteType': 'All',
            'IncludeManagementEvents': True,
            'DataResources': [
                {
                    'Type': 'AWS::Lambda::Function',
                    'Values': [
                        lambda_function
                    ]
                },
            ]
        },
    ]
)
print("CloudTrail data event ARN - {}".format(events['TrailARN']))

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
    print("Permission already exists")

s3_client.put_bucket_notification_configuration(
    Bucket=s3_bucket_name,
    NotificationConfiguration={'LambdaFunctionConfigurations': [
        {
            'LambdaFunctionArn': lambda_function,
            'Events': ['s3:ObjectCreated:*']
        }
    ]})

print("Attached S3 bucket to Lambda Function")

if ENABLE_LOG:
    ct_client.start_logging(
        Name=events['TrailARN']
    )
    print("EC2 Monitoring: ENABLED")
else:
    ct_client.stop_logging(
        Name=events['TrailARN']
    )
    print("EC2 Monitoring: DISABLED")
