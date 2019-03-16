import boto3
import json
import os

ct_conn = boto3.client('cloudtrail')

events_dict = ct_conn.lookup_events(LookupAttributes=[{'AttributeKey': 'ResourceName', 'AttributeValue': 'i-09bdb738e2968ed4d'}])

for data in events_dict['Events']:
    json_file = json.loads(data['CloudTrailEvent'])
    print (json_file['userIdentity']['userName'])
