import boto3
from botocore.exceptions import ClientError

topic_name = "EC2CreationTopic"  # your Topic Name to delete in all regions

ec2 = boto3.client('ec2')
sts = boto3.client("sts")
account_id = sts.get_caller_identity()["Account"]
regions = ec2.describe_regions().get('Regions', [])
all_regions = [region['RegionName'] for region in regions]

for region in all_regions:
    client = boto3.client('sns', region_name=region)
    topic_arn = "arn:aws:sns:{}:{}:{}".format(region, account_id, topic_name)
    try:
        response = client.delete_topic(
            TopicArn=topic_arn
        )
        print("Deleted topic Id - {}".format(topic_arn))
    except ClientError as e:
        print("Resource not found in region - {}".format(region))
