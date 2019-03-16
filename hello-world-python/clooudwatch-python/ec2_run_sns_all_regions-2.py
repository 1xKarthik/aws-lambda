import boto3
import json
from botocore.exceptions import ClientError

email = 'karthik.girraj@gmail.com'  # email to send the mails to
role_arn = 'arn:aws:iam::577683050298:role/my_cw_target_role'  # IAM role for the cloudWatch to talk to EC2

sns_topic_name = 'EC2CreationTopic'  # SNS topic to be created in all regions
cw_rule_name = "EC2RunningStatusEventAllRegions"  # CloudWatch Event Name to be created in all regions
ec2 = boto3.client('ec2')
lambda_client = boto3.client('lambda')
regions = ec2.describe_regions().get('Regions', [])
# all_regions = [region['RegionName'] for region in regions]  # get all AWS region names
all_regions = ['ap-south-1']  # for testing

# following code runs for every region specified in all_regions variable
for region in all_regions:
    cw_events = boto3.client('events', region_name=region)
    sns = boto3.client('sns', region_name=region)

    # CloudWatch rule which will trigger target actions if a new instance is started running in its region
    cw_event = cw_events.put_rule(
        Name=cw_rule_name,
        RoleArn=role_arn,
        EventPattern="{\"source\": [\"aws.ec2\"],\"detail-type\": [\"EC2 Instance State-change Notification\"],\"detail\": {\"state\": [\"running\"]}}",
        State='ENABLED'
    )
    cw_rule_arn = cw_event['RuleArn']
    print(cw_event['RuleArn'])

    sns_target = cw_events.put_targets(
        Rule=cw_rule_name,  # Name of the CloudWatch rule to put target to
        Targets=[
            {
                'Arn': "arn:aws:lambda:ap-south-1:577683050298:function:ec2_cloudwatch_sns",
                'Id': 'myCloudWatchEventsTarget'
            }
        ]
    )

    try:
        lambda_policy = lambda_client.add_permission(
            FunctionName='arn:aws:lambda:ap-south-1:577683050298:function:ec2_cloudwatch_sns',
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            StatementId='TrustCWEToInvokeMyLambdaFunction',
            SourceArn=cw_rule_arn,
        )
        print(lambda_policy)
    except ClientError as e:
        print("Exits")

    # print("Connected CloudWatch Event to SNS Topic in {}".format(region))
    # print("#############################################################")

# print("#############################################################")
# print("Created CloudWatch Event and SNS topics in all regions")
# print("Confirm Email Subscription status for all regions")
