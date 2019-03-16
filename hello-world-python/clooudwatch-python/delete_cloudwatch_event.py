import boto3
from botocore.exceptions import ClientError

rule_name = "EC2RunningStatusEventAllRegions"  # Your CloudWatch Event Rule Name to delete in all regions

ec2 = boto3.client('ec2')
regions = ec2.describe_regions().get('Regions', [])
all_regions = [region['RegionName'] for region in regions]

for region in all_regions:
    client = boto3.client('events', region_name=region)

    try:
        response = client.list_targets_by_rule(
            Rule=rule_name
        )
        target_ids = []
        for t in response['Targets']:
            target_ids.append(t['Id'])

        if target_ids:
            response = client.remove_targets(
                Rule=rule_name,
                Ids=target_ids,
                Force=True
            )
            print("Deleted target Ids - {}".format(target_ids))
            # print("Failed - {}".format(json.dumps(response['FailedEntries'])))
        else:
            print('No targets found')

        response = client.delete_rule(
            Name=rule_name,
            Force=True
        )
        print("Deleted CloudWatch Event Rule - {}".format(rule_name))
    except ClientError as e:
        print("Resource not found in region - {}".format(region))
