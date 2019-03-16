import boto3
import gzip
import json

sns_topic = "arn:aws:sns:ap-south-1:577683050298:CW-Testing"
sns_subject = "Cloudtrail Testing"

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')


# Print out the response

def lambda_handler(event, context):
    # print(event)
    response = sns_client.publish(
        TopicArn='arn:aws:sns:ap-south-1:577683050298:CW-Testing',
        Message=str(event),
        Subject=sns_subject,
        MessageStructure='string',
    )
    # for record in event['Records']:
    #     bucket = record['s3']['bucket']['name']
    #     key = record['s3']['object']['key']

    #     # Fetch logs from S3
    #     s3_object = s3_client.get_object(
    #         Bucket=bucket,
    #         Key=key,
    #     )

    #     # # Extract file and metadata from gzipped S3 object
    #     # with gzip.open(s3_object['Body'], 'rb') as f_in:
    #     #     binaryContent = f_in.read()
    #         # print(binaryContent)

    #     # # # Convert from binary data to text
    #     # raw_logs = binaryContent.decode()

    #     # # # Change text into a dictionary
    #     # dict_logs = json.loads(raw_logs)
    #     # print(dict_logs)

    #     # # Make sure json_logs key 'Records' exists
    #     # if 'Records' in dict_logs.keys():
    #     #     print("Printing Dictionary Content: {} \n\n".format(dict_logs))
    #     #     response = sns_client.publish(
    #     #         TopicArn='arn:aws:sns:ap-south-1:577683050298:CW-Testing',
    #     #         Message=str(dict_logs),
    #     #         Subject=sns_subject,
    #     #         MessageStructure='string',
    #     #     )
    #     # # print(event)
    #     # # print(response)
    #     # else:
    #     #     print("Records key not found")
    #     #     response = sns_client.publish(
    #     #         TopicArn='arn:aws:sns:ap-south-1:577683050298:CW-Testing',
    #     #         Message="nope",
    #     #         Subject=sns_subject,
    #     #         MessageStructure='string',
    #     #     )

# lambda_handler(eventy, context="")
