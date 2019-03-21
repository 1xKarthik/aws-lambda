import boto3
import json
from botocore.exceptions import ClientError

s3_resource = boto3.resource('s3')
ENABLE_LOG = True
lambda_function = 'arn:aws:lambda:ap-south-1:577683050298:function:cloudtrail'  # place your lambda function here
s3_bucket_name = 'ct-s3-test-1'  # place your bucket here
region = 'ap-south-1'
trail_name = 'EC2TrailAllRegions'
sts = boto3.client("sts")
account_id = sts.get_caller_identity()["Account"]
ct_client = boto3.client('cloudtrail', region_name=region)
lambda_client = boto3.client('lambda', region_name=region)
s3_client = boto3.client('s3', region_name=region)
bucket_policy = s3_resource.BucketPolicy(s3_bucket_name)
# print(bucket_policy)
# policy = s3_client.get_bucket_policy(Bucket='bucket_name')
# print(policy)
# try:
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

response = s3_client.put_bucket_policy(
    Bucket=s3_bucket_name,
    Policy=json.dumps(user_policy)
)
ct_client.create_trail(
    Name=trail_name,
    S3BucketName=s3_bucket_name,
    IncludeGlobalServiceEvents=True,
    IsMultiRegionTrail=True,
    EnableLogFileValidation=True,
)
# except ClientError as e:
#     print("Trail with the name {} already Exists".format(trail_name))

# print(ct_client)
