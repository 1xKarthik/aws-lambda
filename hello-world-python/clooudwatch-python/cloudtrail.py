import boto3
import gzip
import json
import shutil

sns_topic = "arn:aws:sns:ap-south-1:577683050298:CW-Testing"
sns_subject = "Cloudtrail Testing"

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
eventy = {
    "Records": [
        {
            "eventVersion": "2.1",
            "eventTime": "2019-03-14T17: 48: 31.871Z",
            "requestParameters": {
                "sourceIPAddress": "13.53.111.38"
            },
            "s3": {
                "configurationId": "5d01ba09-6582-438d-b76d-61b60b8f06bb",
                "object": {
                    "eTag": "7c3f050e1276e5834fa255eba0a811ce",
                    "sequencer": "005C8A93EFB0000869",
                    "key": "AWSLogs/577683050298/CloudTrail/eu-north-1/2019/03/14/577683050298_CloudTrail_eu-north-1_20190314T1745Z_cg12ZJeNKblRwJKY.json.gz",
                    "size": 467
                },
                "bucket": {
                    "arn": "arn:aws:s3: : :ec2-cloudtrail-logs-all-regions",
                    "name": "ec2-cloudtrail-logs-all-regions",
                    "ownerIdentity": {
                        "principalId": "AWNUOWS4ETKQF"
                    }
                },
                "s3SchemaVersion": "1.0"
            },
            "responseElements": {
                "x-amz-id-2": "oNfpmMDfEBkQHeyCjjHqNp4zr3jwQKDK6pmgAWYfXLVQ9WQMfXfoF8U+zW/LQ2P/viGEz5Q/poQ=",
                "x-amz-request-id": "DBDAA7BD4FF8621A"
            },
            "awsRegion": "ap-south-1",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "AWS:AROAJXU6OFNGOWO744HUC:regionalDeliverySession"
            },
            "eventSource": "aws:s3"
        }
    ]
}


# Print out the response

def lambda_handler(event, context):
    # print(event)
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Fetch logs from S3
        s3_object = s3_client.get_object(
            Bucket=bucket,
            Key=key,
        )

        # # Extract file and metadata from gzipped S3 object
        # f = gzip.open(r"C:\qwe\asd.gz", 'rb')
        # file_content = f.read()
        # print(file_content)
        # f.close()
        # with gzip.open(r"C:\qwe\asd.gz", 'rb') as binaryObj:
        #     binaryContent = binaryObj.read()
        with gzip.open(r"C:\qwe\577683050298_CloudTrail_ap-south-1_20190314T1925Z_V7W10FMQBvKZHzpZ.json.gz",
                       'rb') as f_in:
            binaryContent = f_in.read()
            print(binaryContent)

        # # Convert from binary data to text
        # raw_logs = binaryContent.decode()
        #
        # # # Change text into a dictionary
        # dict_logs = json.loads(raw_logs)
        # print(dict_logs)

        # # Make sure json_logs key 'Records' exists
        # if 'Records' in dict_logs.keys():
        #     print("Printing Dictionary Content: {} \n\n".format(dict_logs))
        #     response = sns_client.publish(
        #         TopicArn='arn:aws:sns:ap-south-1:577683050298:CW-Testing',
        #         Message=str(dict_logs),
        #         Subject=sns_subject,
        #         MessageStructure='string',
        #     )
        # # print(event)
        # # print(response)
        # else:
        #     print("Records key not found")
        #     response = sns_client.publish(
        #         TopicArn='arn:aws:sns:ap-south-1:577683050298:CW-Testing',
        #         Message="nope",
        #         Subject=sns_subject,
        #         MessageStructure='string',
        #     )
        # response = sns_client.publish(
        #     TopicArn='arn:aws:sns:ap-south-1:577683050298:CW-Testing',
        #     Message=str(dict_logs),
        #     Subject=sns_subject,
        #     MessageStructure='string',
        # )


lambda_handler(eventy, context="")
