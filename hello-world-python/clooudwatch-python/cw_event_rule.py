import boto3

cloudwatch_events = boto3.client('events')
sns = boto3.client('sns')

response = cloudwatch_events.put_rule(
    Name="DEMO",
    RoleArn='arn:aws:iam::577683050298:role/my_cw_target_role',
    EventPattern="{\"source\": [\"aws.ec2\"],\"detail-type\": [\"EC2 Instance State-change Notification\"],\"detail\": {\"state\": [\"running\"]}}",
    State='ENABLED'
)

# Put target for rule
SNSresponse = cloudwatch_events.put_targets(
    Rule='DEMO',
    Targets=[
        {
            'Arn': 'arn:aws:sns:ap-south-1:577683050298:CW-Testing',
            'Id': 'myCloudWatchEventsTarget',
        }
    ]
)

snssresponse = sns.set_topic_attributes(
    TopicArn='arn:aws:sns:ap-south-1:577683050298:CW-Testing',
    AttributeName='Policy',
    AttributeValue="{\"Version\":\"2012-10-17\",\"Id\":\"__default_policy_ID\",\"Statement\":[{\"Sid\":\"__default_statement_ID\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"*\"},\"Action\":[\"SNS:GetTopicAttributes\",\"SNS:SetTopicAttributes\",\"SNS:AddPermission\",\"SNS:RemovePermission\",\"SNS:DeleteTopic\",\"SNS:Subscribe\",\"SNS:ListSubscriptionsByTopic\",\"SNS:Publish\",\"SNS:Receive\"],\"Resource\":\"arn:aws:sns:region:account-id:topic-name\",\"Condition\":{\"StringEquals\":{\"AWS:SourceOwner\":\"account-id\"}}}, {\"Sid\":\"TrustCWEToPublishEventsToMyTopic\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"events.amazonaws.com\"},\"Action\":\"sns:Publish\",\"Resource\":\"arn:aws:sns:ap-south-1:577683050298:CW-Testing\"}]}"
)
print(response)
print(SNSresponse)
print(snssresponse)
