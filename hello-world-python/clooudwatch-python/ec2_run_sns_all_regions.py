import boto3
import json

email = 'karthik.girraj@gmail.com'  # email to send the mails to
role_arn = 'arn:aws:iam::577683050298:role/my_cw_target_role'  # IAM role for the cloudWatch to talk to EC2

sns_topic_name = 'EC2CreationTopic'  # SNS topic to be created in all regions
cw_rule_name = "EC2RunningStatusEventAllRegions"  # CloudWatch Event Name to be created in all regions
ec2 = boto3.client('ec2')
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

    # SNS Topic creation with the specified name
    sns_topic = sns.create_topic(
        Name=sns_topic_name
    )
    sns_topic_arn = sns_topic['TopicArn']
    print("created SNS topic in {} and ARN is {}".format(region, sns_topic_arn))

    # Attach Emails to the SNS Topic
    sns_sub = sns.subscribe(
        TopicArn=sns_topic_arn,
        Protocol='email',
        Endpoint=email
    )
    # print("Email Subscription status - {}".format(sns_sub['SubscriptionArn']))

    # This is the target which will get triggered if instance is created
    sns_target = cw_events.put_targets(
        Rule=cw_rule_name,  # Name of the CloudWatch rule to put target to
        Targets=[
            {
                'Arn': sns_topic_arn,  # SNS is triggered with EC2 instance details
                'Id': 'myCloudWatchEventsTarget',
                "InputTransformer":  # SNS message formatting
                    {
                        "InputPathsMap": {"account": "$.account", "region": "$.region",
                                          "instance": "$.detail.instance-id", "state": "$.detail.state"},
                        "InputTemplate": json.dumps(
                            "Account: <account> | Region: <region> | Instance ID: <instance> | State: <state>")
                    }
            }
        ]
    )

    # Access policy for the CloudWatch Event rule to trigger SNS topic
    attribute_value = {'Version': '2012-10-17', 'Id': '__default_policy_ID', 'Statement': [
        {'Sid': '__default_statement_ID', 'Effect': 'Allow', 'Principal': {'AWS': '*'},
         'Action': ['SNS:GetTopicAttributes', 'SNS:SetTopicAttributes', 'SNS:AddPermission', 'SNS:RemovePermission',
                    'SNS:DeleteTopic', 'SNS:Subscribe', 'SNS:ListSubscriptionsByTopic', 'SNS:Publish', 'SNS:Receive'],
         'Resource': sns_topic_arn,
         'Condition': {'StringEquals': {'AWS:SourceOwner': 'account-id'}}},
        {'Sid': 'TrustCWEToPublishEventsToMyTopic', 'Effect': 'Allow', 'Principal': {'Service': 'events.amazonaws.com'},
         'Action': 'sns:Publish', 'Resource': sns_topic_arn}]}
    # Attach policy to the SNS topic
    sns_policy = sns.set_topic_attributes(
        TopicArn=sns_topic_arn,
        AttributeName='Policy',
        AttributeValue=json.dumps(attribute_value)
    )
    # print("Connected CloudWatch Event to SNS Topic in {}".format(region))
    # print("#############################################################")

print("#############################################################")
print("Created CloudWatch Event and SNS topics in all regions")
print("Confirm Email Subscription status for all regions")
