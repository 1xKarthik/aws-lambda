import boto3
import gzip
import json
from datetime import datetime
from collections import defaultdict

sns_topic = "arn:aws:sns:ap-south-1:577683050298:CW-Testing"  # your SNS topic
sns_subject = "EC2 Alert"  # Email Subject
region = 'ap-south-1'

s3_client = boto3.resource('s3', region_name=region)
sns_client = boto3.client('sns', region_name=region)

EVENT_SOURCE = "ec2.amazonaws.com"
EVENT_NAMES = ["RunInstances", "TerminateInstances"]
kwargs = defaultdict(str)


def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        s3_client.Bucket(bucket).download_file(key, '/tmp/myfile.gz')

        with gzip.open(r"/tmp/myfile.gz", 'rb') as f_in:
            binaryContent = f_in.read()
        raw_logs = binaryContent.decode()
        dict_logs = json.loads(raw_logs)

        # Make sure json_logs key 'Records' exists
        if 'Records' in dict_logs.keys():
            print("Printing Dictionary Content: {} \n\n".format(dict_logs))
            for item in dict_logs['Records']:
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
                                print(msg)
                                kwargs.clear()

                            except KeyError:
                                print('Key Error')
                                msg = 'Key Error'
                                kwargs.clear()

                            sns_client.publish(
                                TopicArn=sns_topic,
                                Message=msg,
                                Subject=sns_subject,
                                MessageStructure='string',
                            )
