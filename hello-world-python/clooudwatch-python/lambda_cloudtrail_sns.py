import boto3
import gzip
import json
from datetime import datetime

sns_topic = "arn:aws:sns:ap-south-1:577683050298:CW-Testing"  # your SNS topic
sns_subject = "EC2 Alert"  # Email Subject

s3_client = boto3.resource('s3')
sns_client = boto3.client('sns')

EVENT_SOURCE = "ec2.amazonaws.com"
EVENT_NAMES = ["RunInstances", "TerminateInstances"]


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
                            if item['sourceIPAddress']:
                                src_ip = item['sourceIPAddress']
                                region = item['awsRegion']
                                status = item['eventName']
                                instance_id = item['responseElements']['instancesSet']['items'][0]['instanceId']
                                src_user = item['userIdentity']['userName']
                            if item['eventName'] == 'RunInstances':
                                creation_time = item['responseElements']['instancesSet']['items'][0]['launchTime']
                                ct = datetime.utcfromtimestamp(creation_time / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
                                msg = "User: {} \nIP: {} \nRegion: {} \nInstance ID: {} \nLaunch Time: {} \nStatus: {}".format(
                                    src_user, src_ip, region, instance_id, ct, status)
                            else:
                                msg = "User: {} \nIP: {} \nRegion: {} \nInstance ID: {} \nStatus: {}".format(
                                    src_user, src_ip, region, instance_id, status)

                            sns_client.publish(
                                TopicArn=sns_topic,
                                Message=msg,
                                Subject=sns_subject,
                                MessageStructure='string',
                            )
