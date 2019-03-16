import boto3
import gzip
import json
import botocore

sns_topic = "arn:aws:sns:ap-south-1:577683050298:CW-Testing"
sns_subject = "Cloudtrail Testing"

s3_client = boto3.resource('s3')
sns_client = boto3.client('sns')

EVENT_SOURCE = "ec2.amazonaws.com"
EVENT_NAME = "RunInstances"


def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        s3_client.Bucket(bucket).download_file(key, '/tmp/myfile.gz')

        with gzip.open(r"/tmp/myfile.gz", 'rb') as f_in:
            binaryContent = f_in.read()

        raw_logs = binaryContent.decode()

        #     # # # Change text into a dictionary
        dict_logs = json.loads(raw_logs)
        print(dict_logs)

        # Make sure json_logs key 'Records' exists
        if 'Records' in dict_logs.keys():
            print("Printing Dictionary Content: {} \n\n".format(dict_logs))
            for item in dict_logs['Records']:
                if ('eventSource' in item):
                    print(item['eventSource'])
                    print(item['eventName'])
                    if (item['eventSource'] == EVENT_SOURCE):
                        if (item['eventName'] == EVENT_NAME):
                            # Grab other useful details for investigation
                            if item['sourceIPAddress']:
                                src_ip = item['sourceIPAddress']
                            if item['userIdentity']['arn']:
                                src_user = item['userIdentity']['arn']
                                response = sns_client.publish(
                                    TopicArn='arn:aws:sns:ap-south-1:577683050298:CW-Testing',
                                    Message="{} - {} - {}".format(src_ip,src_user, item),
                                    Subject=sns_subject,
                                    MessageStructure='string',
                                )

# lambda_handler(eventy, context="")
