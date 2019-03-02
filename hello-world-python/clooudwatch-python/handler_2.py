from collections import defaultdict

import boto3  # aws sdk for python

tag_name = 'environment'
tag_value = 'EBX12'
ec2_sns = 'arn:aws:sns:ap-south-1:577683050298:CW-Testing'  # Ex: arn:aws:sns:ap-south-1:577683054564:CW-Testing
ec2_recovery = ''  # you recovery action Id


def get_instance_name(list):
    for t in list:
        if t['Key'] == 'Name':
            return t['Value']


def lambda_handler():
    ec2 = boto3.resource('ec2')
    cw = boto3.client('cloudwatch')
    ec2info = defaultdict()
    running_instances = ec2.instances.filter(
        Filters=[{'Name': 'tag-key', 'Values': ['environment'], }])
    for instance in running_instances:
        for tag in instance.tags:

            if tag_name in tag['Key']:
                env_value = tag['Value']
                name = get_instance_name(instance.tags)
                if env_value == tag_value:
                    ec2info[instance.id] = {'Name': name, 'InstanceId': instance.instance_id, }
                    attributes = ['Name', 'InstanceId']
                    for instance_id, instance in ec2info.items():
                        instanceid = instance["InstanceId"]
                        nameinsta = instance["Name"]
                        print(instanceid, nameinsta)
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
                            AlarmName=(nameinsta) +
                                      "_StatusCheckFailed_System_(Lambda)",
                            AlarmDescription='StatusCheckFailed_System ',
                            ActionsEnabled=True,
                            AlarmActions=[ec2_sns, ec2_recovery],
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
                            AlarmActions=[ec2_sns],
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
