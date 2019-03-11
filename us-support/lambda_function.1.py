from collections import defaultdict

import boto3

EC2_TAG_NAMES = ['your_EC2_target_tag_names']  # EX: dev, prod
ec2_sns = 'Your-SNS-Topic'  # Ex: arn:aws:sns:ap-south-1:577683054564:CW-Testing


def lambda_handler(event, context):
    ec2 = boto3.resource('ec2')
    cw = boto3.client('cloudwatch')
    ec2info = defaultdict()
    running_instances = ec2.instances.filter(
        Filters=[{'Name': 'tag-key', 'Values': EC2_TAG_NAMES, }])
    for instance in running_instances:
        for tag in instance.tags:
            if 'Name'in tag['Key']:
                name = tag['Value']
                ec2info[instance.id] = {'Name': name,
                                        'InstanceId': instance.instance_id, }

                for instance in ec2info.items():
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
                        AlarmName=(nameinsta) + "_StatusCheckFailed_(Lambda)",
                        AlarmDescription='StatusCheckFailed ',
                        ActionsEnabled=True,
                        AlarmActions=[ec2_sns, ],
                        MetricName='StatusCheckFailed',
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
                        AlarmActions=[ec2_sns],
                        MetricName='StatusCheckFailed_System',
                        Namespace='AWS/EC2',
                        Statistic='Average',
                        Dimensions=[
                            {'Name': "InstanceId", 'Value': instanceid}, ],
                        Period=900,
                        EvaluationPeriods=1,
                        Threshold=1,
                        ComparisonOperator='GreaterThanOrEqualToThreshold')
