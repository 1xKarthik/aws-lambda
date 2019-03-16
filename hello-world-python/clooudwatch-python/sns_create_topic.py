import boto3
import json

region = 'ap-south-1'
client = boto3.client('sns', region_name=region)
response = client.create_topic(
    Name='EC2Topic'
)

print(response)

response2 = client.subscribe(
    TopicArn=response['TopicArn'],
    Protocol='email',
    Endpoint='karthik.girraj@gmail.com',
    ReturnSubscriptionArn=False
)
print(response2)
