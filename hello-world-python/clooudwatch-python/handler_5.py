from collections import defaultdict
from botocore.config import Config
import boto3

region = 'ap-south-1'
tag_name = 'cloudwatch'  # place your tag name
tag_value = 'yes'  # place your tag_value
ec2_sns = 'arn:aws:sns:ap-south-1:577683050298:CW-Testing'  # Ex: arn:aws:sns:ap-south-1:577683054564:CW-Testing
ec2_recovery = 'arn:aws:automate:ap-south-1:ec2:recover'
config = Config(
    retries=dict(
        max_attempts=20
    )
)
ec2r = boto3.resource('ec2', region_name=region)
cw = boto3.client('cloudwatch', config=config)
ec2info = defaultdict()


def get_running_instances(t_name, t_value):
    instances = [i for i in ec2r.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['terminated']},
                 {'Name': 'tag:' + tag_name, 'Values': [tag_value]}])]
    for instance in instances:
        for tag in instance.tags or []:
            if t_name in tag['Key']:
                if instance.id in ec2info:
                    ec2info[instance.id]['InstanceId'] = instance.instance_id
                else:
                    ec2info[instance.id] = {'InstanceId': instance.instance_id}
            elif "Name" in tag['Key']:
                i_name = tag['Value']
                if instance.id in ec2info:
                    ec2info[instance.id]['Name'] = i_name
                else:
                    ec2info[instance.id] = {'Name': i_name}
    return ec2info


print(get_running_instances(tag_name, tag_value))


def lambda_handler():
    # def lambda_handler(event, context):
    running_instances = get_running_instances(tag_name, tag_value).items()
    output_format = 'instances with tags matching: {t_name} = {t_value}'.format(t_name=tag_name, t_value=tag_value)
    if not running_instances:
        print('No {}'.format(output_format))
        return False
    print('List of running {}'.format(output_format))
    for instance_id, instance in running_instances:
        instanceid = instance["InstanceId"]
        nameinsta = instance["Name"]
        print("Creating Alarm for instance: {insta_id} - {inst_name}".format(insta_id=instance_id, inst_name=nameinsta))
        # Create CPU Alarms
        cw.put_metric_alarm(
            AlarmName="{id}_{name}_CPU_Load_(Lambda)".format(id=instance_id, name=nameinsta),
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
    #     # Create StatusCheckFailed Alarms
    #     # cw.put_metric_alarm(
    #     #     AlarmName="{name}_StatusCheckFailed_Instance(Lambda)".format(name=nameinsta),
    #     #     AlarmDescription='StatusCheckFailed_Instance',
    #     #     ActionsEnabled=True,
    #     #     AlarmActions=[ec2_sns, ],
    #     #     MetricName='StatusCheckFailed_Instance',
    #     #     Namespace='AWS/EC2',
    #     #     Statistic='Average',
    #     #     Dimensions=[
    #     #         {'Name': "InstanceId", 'Value': instanceid}, ],
    #     #     Period=900,
    #     #     EvaluationPeriods=1,
    #     #     Threshold=1,
    #     #     ComparisonOperator='GreaterThanOrEqualToThreshold')
    #     # Create StatusCheckFailed_System Alarms
    #     cw.put_metric_alarm(
    #         AlarmName="{name}_StatusCheckFailed_System_(Lambda)".format(name=nameinsta),
    #         AlarmDescription='StatusCheckFailed_System ',
    #         ActionsEnabled=True,
    #         AlarmActions=[ec2_sns, ec2_recovery, ],
    #         MetricName='StatusCheckFailed_System',
    #         Namespace='AWS/EC2',
    #         Statistic='Average',
    #         Dimensions=[
    #             {'Name': "InstanceId", 'Value': instanceid}, ],
    #         Period=900,
    #         EvaluationPeriods=1,
    #         Threshold=1,
    #         ComparisonOperator='GreaterThanOrEqualToThreshold')
    #     # cw.put_metric_alarm(
    #     #     AlarmName="{name}_StatusCheckFailed_Any_(Lambda)".format(name=nameinsta),
    #     #     AlarmDescription='StatusCheckFailed_Any ',
    #     #     ActionsEnabled=True,
    #     #     AlarmActions=[ec2_sns, ],
    #     #     MetricName='StatusCheckFailed',
    #     #     Namespace='AWS/EC2',
    #     #     Statistic='Average',
    #     #     Dimensions=[
    #     #         {'Name': "InstanceId", 'Value': instanceid}, ],
    #     #     Period=300,
    #     #     EvaluationPeriods=1,
    #     #     Threshold=1,
    #     #     ComparisonOperator='GreaterThanOrEqualToThreshold')


lambda_handler()
