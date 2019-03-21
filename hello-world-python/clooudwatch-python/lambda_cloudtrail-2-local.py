import boto3
import gzip
import json
from datetime import datetime
from collections import defaultdict

with open('both_events.json', 'rb') as rec:
    x = rec.read()

sns_topic = "arn:aws:sns:ap-south-1:577683050298:CW-Testing"  # your SNS topic
sns_subject = "EC2 Alert"  # Email Subject

s3_client = boto3.resource('s3')
sns_client = boto3.client('sns')

EVENT_SOURCE = "ec2.amazonaws.com"
EVENT_NAMES = ["RunInstances", "TerminateInstances"]

kwargs = defaultdict(str)


def lambda_handler(events, context):
    event = json.loads(events)
    if 'Records' in event:
        # print("Printing Dictionary Content: {} \n\n".format(event))
        for item in event['Records']:
            if 'eventSource' in item:
                if item['eventSource'] == EVENT_SOURCE:
                    if item['eventName'] in EVENT_NAMES:
                        print('EVENT FOUND')
                        # Grab other useful details for investigation
                        try:
                            if 'userName' in item['userIdentity']:
                                kwargs['userName'] = item['userIdentity']['userName']
                            else:
                                userArn = item['userIdentity']['arn']
                                kwargs['userName'] = userArn.split(':')[5]

                            kwargs['sourceIPAddress'] = item.get('sourceIPAddress', None)
                            kwargs['awsRegion'] = item.get('awsRegion', None)
                            kwargs['eventName'] = item.get('eventName', None)
                            instance_details = item['responseElements']['instancesSet']['items'][0]
                            kwargs['instanceId'] = instance_details['instanceId']
                            kwargs['instanceType'] = instance_details.get('instanceType', None)

                            if item['eventName'] == 'RunInstances':
                                launch_time = item['responseElements']['instancesSet']['items'][0]
                                if 'launchTime' in launch_time:
                                    kwargs['launchTime'] = datetime.utcfromtimestamp(
                                        launch_time['launchTime'] / 1000.0).strftime(
                                        '%Y-%m-%d %H:%M:%S')
                            print(kwargs)
                            msg = ''
                            for key, value in sorted(kwargs.iteritems()):
                                if value is not None:
                                    msg += key + " => " + value + '\n'
                            print('############################')
                            print(msg)
                            kwargs.clear()

                        except KeyError:
                            print('Nope')
                            msg = 'Key Error'

                        # sns_client.publish(
                        #     TopicArn=sns_topic,
                        #     Message=msg,
                        #     Subject=sns_subject,
                        #     MessageStructure='string',
                        # )


lambda_handler(x, "")
