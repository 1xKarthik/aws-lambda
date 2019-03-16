import boto3
from botocore.exceptions import ClientError

ENABLE_LOG = True
lambda_function = 'arn:aws:lambda:ap-south-1:577683050298:function:cloudtrail'  # place your lambda function here
s3_bucket_name = 'ct-s3-test-1'  # place your bucket here

trail_name = 'EC2TrailAllRegions'
client = boto3.client('cloudtrail')
try:
    response = client.create_trail(
        Name=trail_name,
        S3BucketName=s3_bucket_name,
        IncludeGlobalServiceEvents=True,
        IsMultiRegionTrail=True,
        EnableLogFileValidation=True,
    )
except ClientError as e:
    print("Trail with the name {} already Exists".format(trail_name))

events = client.put_event_selectors(
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

if ENABLE_LOG:
    client.start_logging(
        Name=events['TrailARN']
    )
    print("EC2 Monitoring: ENABLED")
else:
    client.stop_logging(
        Name=events['TrailARN']
    )
    print("EC2 Monitoring: DISABLED")
