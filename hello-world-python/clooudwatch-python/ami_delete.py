import boto3
from dateutil.parser import parse
import datetime

age = 0  # specify number of days before the snapshots should get deleted
region_name = 'ap-south-1'

client = boto3.client('ec2', region_name=region_name)
amis = client.describe_images(Owners=['self'])
print(amis)


def days_old(date):
    get_date_obj = parse(date)
    date_obj = get_date_obj.replace(tzinfo=None)
    diff = datetime.datetime.now() - date_obj
    return diff.days


def ami_delete_fn():
    for ami in amis['Images']:
        create_date = ami['CreationDate']
        ami_id = ami['ImageId']
        day_old = days_old(create_date)
        print(day_old)
        if day_old == age:
            print("deleting -> " + ami_id + " - create_date = " + create_date)
            client.deregister_image(ImageId=ami_id)


ami_delete_fn()
