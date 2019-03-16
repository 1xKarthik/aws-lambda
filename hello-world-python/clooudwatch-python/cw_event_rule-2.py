import boto3
import json

sns = boto3.client('sns')
sns_arn = 'arn:aws:sns:ap-south-1:577683050298:ec2testing'
role_arn = 'arn:aws:iam::577683050298:role/my_cw_target_role'
regions = ['ap-south-1', 'ap-southeast-1']

for region in regions:
    cw_events = boto3.client('events', region_name=region)

    response = cw_events.put_rule(
        Name="EC2RunningAllRegions",
        RoleArn=role_arn,
        EventPattern="{\"source\": [\"aws.ec2\"],\"detail-type\": [\"EC2 Instance State-change Notification\"],\"detail\": {\"state\": [\"running\"]}}",
        State='ENABLED'
    )

    # Put target for rule
    SNSresponse = cw_events.put_targets(
        Rule='EC2RunningAllRegions',
        Targets=[
            {
                'Arn': sns_arn,
                'Id': 'myCloudWatchEventsTarget',
                "InputTransformer":
                    {
                        "InputPathsMap": {"account": "$.account", "instance": "$.detail.instance",
                                          "status": "$.detail.status"},
                        "InputTemplate": "<account> <instance> <status>"
                    }
            }
        ]
    )


    attribute_value = {'Version': '2012-10-17', 'Id': '__default_policy_ID', 'Statement': [
        {'Sid': '__default_statement_ID', 'Effect': 'Allow', 'Principal': {'AWS': '*'},
         'Action': ['SNS:GetTopicAttributes', 'SNS:SetTopicAttributes', 'SNS:AddPermission', 'SNS:RemovePermission',
                    'SNS:DeleteTopic', 'SNS:Subscribe', 'SNS:ListSubscriptionsByTopic', 'SNS:Publish', 'SNS:Receive'],
         'Resource': sns_arn,
         'Condition': {'StringEquals': {'AWS:SourceOwner': 'account-id'}}},
        {'Sid': 'TrustCWEToPublishEventsToMyTopic', 'Effect': 'Allow', 'Principal': {'Service': 'events.amazonaws.com'},
         'Action': 'sns:Publish', 'Resource': sns_arn}]}

    snssresponse = sns.set_topic_attributes(
        TopicArn=sns_arn,
        AttributeName='Policy',
        AttributeValue=json.dumps(attribute_value)
    )
    print(response)
    print(SNSresponse)
    print(snssresponse)
