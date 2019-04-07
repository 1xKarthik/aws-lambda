import boto3
import json
from botocore.exceptions import ClientError

ENABLE_LOG = True
lambda_function = 'arn:aws:lambda:ap-south-1:577683050298:function:cloudtrail'  # place your lambda function here
s3_bucket_name = 'alksjdlksajdksajk'  # place your bucket here
region = 'ap-south-1'  # replace the region
trail_name = 'EC2TrailAllRegions'  # CLoudTrail name

sts = boto3.client("sts")
ct_client = boto3.client('cloudtrail', region_name=region)
lambda_client = boto3.client('lambda', region_name=region)
s3_client = boto3.client('s3', region_name=region)
account_id = sts.get_caller_identity()["Account"]

user_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck20150319",
            "Effect": "Allow",
            "Principal": {"Service": "cloudtrail.amazonaws.com"},
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::{}".format(s3_bucket_name)
        },
        {
            "Sid": "AWSCloudTrailWrite20150319",
            "Effect": "Allow",
            "Principal": {"Service": "cloudtrail.amazonaws.com"},
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::{}/AWSLogs/{}/*".format(s3_bucket_name, account_id),
            "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
        }
    ]
}

s3_client.put_bucket_policy(
    Bucket=s3_bucket_name,
    Policy=json.dumps(user_policy)
)
print("Bucket policy added")

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
print("CloudTrail added: ARN - {}".format(events['TrailARN']))

s3_client.put_bucket_notification_configuration(
    Bucket=s3_bucket_name,
    NotificationConfiguration={})
print("Old S3 triggers removed")

response = lambda_client.remove_permission(
    FunctionName=lambda_function,
    StatementId='TrustS3ToInvokeMyLambdaFunction'
)
print("Old Lambda permissions removed")

lambda_policy = lambda_client.add_permission(
    FunctionName=lambda_function,
    Action='lambda:InvokeFunction',
    Principal='s3.amazonaws.com',
    StatementId='TrustS3ToInvokeMyLambdaFunction',
    SourceArn="arn:aws:s3:::{}".format(s3_bucket_name),
)

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
