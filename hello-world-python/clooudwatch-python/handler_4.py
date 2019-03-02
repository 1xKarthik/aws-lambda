from collections import defaultdict
from botocore.config import Config
import boto3

tag_name = 'qwe'  # place your tag name
tag_value = 'asd'  # place your tag_value
ec2_sns = 'arn:aws:sns:ap-south-1:577683050298:CW-Testing'  # Ex: arn:aws:sns:ap-south-1:577683054564:CW-Testing
ec2_recovery = "arn:aws:automate:ap-south-1:ec2:recover"

config = Config(
    retries=dict(
        max_attempts=20
    )
)
ec2 = boto3.resource('ec2')
cw = boto3.client('cloudwatch', config=config)
ec2info = defaultdict()


def get_running_instances(t_name, t_value):
    running_instances = ec2.instances.filter(
        Filters=[{'Name': 'tag-key', 'Values': [t_name], }])
    for instance in running_instances:
        if instance.state['Name'] == 'running':
            for tag in instance.tags or []:
                if t_name in tag['Key']:
                    env_value = tag['Value']
                    if env_value == t_value:
                        ec2info[instance.id] = {'Name': instance.instance_id, 'InstanceId': instance.instance_id, }
    return ec2info


running_ec2 = get_running_instances(tag_name, tag_value)


def lambda_handler():
    # def lambda_handler(event, context):
    for instance_id, instance in running_ec2.items():
        instanceid = instance["InstanceId"]
        nameinsta = instance["Name"]
        print("Creating Alarm for instance: " + instance_id)
        ###############################################
        # Create CPU Alarms
        cw.put_metric_alarm(
            AlarmName=(nameinsta) + "_CPU_Load_(Lambda)",
            AlarmDescription='CPU Utilization ',
            ActionsEnabled=True,
            AlarmActions=[ec2_sns, ],
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            Statistic='Average',
            Dimensions=[
                {'Name': "InstanceId", 'Value': instanceid}, ],
            Period=300,
            EvaluationPeriods=1,
            Threshold=70.0,
            ComparisonOperator='GreaterThanOrEqualToThreshold')
        ###############################################
        # Create StatusCheckFailed Alamrs
        cw.put_metric_alarm(
            AlarmName=(nameinsta) + "_StatusCheckFailed_Instance(Lambda)",
            AlarmDescription='StatusCheckFailed_Instance',
            ActionsEnabled=True,
            AlarmActions=[ec2_sns, ],
            MetricName='StatusCheckFailed_Instance',
            Namespace='AWS/EC2',
            Statistic='Average',
            Dimensions=[
                {'Name': "InstanceId", 'Value': instanceid}, ],
            Period=900,
            EvaluationPeriods=1,
            Threshold=1,
            ComparisonOperator='GreaterThanOrEqualToThreshold')
        ###############################################
        # Create StatusCheckFailed_System Alamrs
        cw.put_metric_alarm(
            AlarmName=(nameinsta) + "_StatusCheckFailed_System_(Lambda)",
            AlarmDescription='StatusCheckFailed_System ',
            ActionsEnabled=True,
            AlarmActions=[ec2_sns, ec2_recovery, ],
            MetricName='StatusCheckFailed_System',
            Namespace='AWS/EC2',
            Statistic='Average',
            Dimensions=[
                {'Name': "InstanceId", 'Value': instanceid}, ],
            Period=900,
            EvaluationPeriods=1,
            Threshold=1,
            ComparisonOperator='GreaterThanOrEqualToThreshold')
        cw.put_metric_alarm(
            AlarmName=(nameinsta) +
                      "_StatusCheckFailed_Any_(Lambda)",
            AlarmDescription='StatusCheckFailed_Any ',
            ActionsEnabled=True,
            AlarmActions=[ec2_sns, ],
            MetricName='StatusCheckFailed',
            Namespace='AWS/EC2',
            Statistic='Average',
            Dimensions=[
                {'Name': "InstanceId", 'Value': instanceid}, ],
            Period=300,
            EvaluationPeriods=1,
            Threshold=1,
            ComparisonOperator='GreaterThanOrEqualToThreshold')


lambda_handler()
