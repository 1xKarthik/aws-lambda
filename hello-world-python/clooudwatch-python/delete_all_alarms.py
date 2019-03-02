import boto3

client = boto3.client('cloudwatch')
get_alarms = client.describe_alarms()


def delete_alarms():
    for alarm in get_alarms['MetricAlarms']:
        print("Deleting Alarm " + alarm['AlarmName'])
        client.delete_alarms(
            AlarmNames=[alarm['AlarmName']],
        )


delete_alarms()
