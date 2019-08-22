"""
Search and delete tags for AMI
"""

import boto3

my_region = 'ap-south-1'  # specify your main region

# Case Insensitive
search = 'Gold'  # search string

# Create Tags (Case Sensitive)
create_tag_name = 'GoldenAMI'  # Tag keys are case-sensitive and accept a maximum of 127 Unicode characters. May not begin with aws: .
create_tag_value = 'Yes'  # Tag values are case-sensitive and accept a maximum of 255 Unicode characters.

ec2_client = boto3.client('ec2', region_name=my_region)
regions = ec2_client.describe_regions().get('Regions', [])
all_regions = [region['RegionName'] for region in regions]  # to search and delete tags for all regions in aws
# all_regions = ['us-east-1', 'ap-south-1']  # to search and delete tags for specific regions only

print("AMI's matching string: {}".format(search))
for region in all_regions:  # loop though all regions
    client = boto3.client('ec2', region_name=region)
    response = client.describe_images(Owners=['self'])

    ids = []
    if response['Images']:  # if AMI's with matching string found
        for ami in response['Images']:  # loop through all the matched AMI's
            ami_name = ami['Name']  # get the name of AMI
            ami_id = ami['ImageId']  # get the ID if AMI
            if search.lower() in ami['Name'].lower():  # search if AMI Name has the search string
                ids.append(ami_id)  # if has, then add the AMI id to the id's array
        print('[{}]=> {}'.format(region, ids))  # print all the found Id's in this particular region
        if ids:  # if ids is not empty
            # delete the tag for all the found AMI ids in this particular region
            client.delete_tags(
                Resources=ids,
                Tags=[
                    {
                        'Key': create_tag_name,
                        'Value': create_tag_value
                    }
                ]
            )
            print('Deleted tags in all of {}'.format(region))
            ids = []  # reset the ids array and move on to next region
    else:  # if images with matching tags not found
        print('[{}]=> {}'.format(region, ids))

print('====================== DONE =========================')
