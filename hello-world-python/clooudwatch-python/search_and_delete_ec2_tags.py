import boto3

my_region = 'ap-south-1'  # specify your main region

# Search Tags (Case Sensitive)
search_tag_name = 'Name'
search_tag_value = 'gold'

# Delete Tags (Case Sensitive)
delete_tag_name = 'GoldenAMI'  # Tag keys are case-sensitive and accept a maximum of 127 Unicode characters. May not begin with aws: .
delete_tag_value = 'Yes'  # Tag values are case-sensitive and accept a maximum of 255 Unicode characters.

client = boto3.client('ec2', region_name=my_region)
regions = client.describe_regions().get('Regions', [])
all_regions = [region['RegionName'] for region in regions]  # to search and create tags for all regions in aws
# all_regions = ['us-east-1', 'ap-south-1']  # to search and create tags for specific regions only

print('Instances with tags matching: [{} = {}]'.format(search_tag_name, search_tag_value))
for region in all_regions:  # loop though all regions
    ec2 = boto3.resource('ec2', region_name=region)
    ec2_client = boto3.client('ec2', region_name=region)
    instances = ec2.instances.filter(Filters=[
        {'Name': 'tag:' + search_tag_name, 'Values': [search_tag_value]}])  # filter the instances with matching tags
    ids = []
    for instance in instances:  # loop through all the matched instances
        if instance.state['Name'] == 'running':  # select only running instances
            ids.append(instance.id)  # add the instance to the ids array
    print('[{}]=> {}'.format(region, ids))
    if ids:  # if ids is not empty
        # Delete the tag for all the found instance ids in this particular region
        ec2_client.delete_tags(
            Resources=ids,
            Tags=[
                {
                    'Key': delete_tag_name,
                    'Value': delete_tag_value
                }
            ]
        )
        print('Deleted tags in all of {}'.format(region))
        ids = []  # reset the ids array and move on to next region

print('====================== DONE =========================')
