import boto3
import datetime
from botocore.exceptions import ClientError

age = 1  # specify number of days before the snapshots should get deleted
region_name = 'ap-south-1'


def ebs_delete_fn():
    client = boto3.client('ec2', region_name=region_name)
    snapshots = client.describe_snapshots(OwnerIds=['self'])
    for snapshot in snapshots['Snapshots']:
        snapshot_time = snapshot['StartTime']
        snapshot_date = snapshot_time.date()
        current_date = datetime.datetime.now().date()
        diff_days = current_date - snapshot_date
        try:
            if diff_days.days == age:
                snap_id = snapshot['SnapshotId']
                print('Deleting Snapshot ' + snapshot['SnapshotId'])
                client.delete_snapshot(SnapshotId=snap_id)
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidSnapshot.InUse':
                print('Error in deleting this Snapshot - ' + snapshot['SnapshotId'])
                print(str(e))
                continue


ebs_delete_fn()
