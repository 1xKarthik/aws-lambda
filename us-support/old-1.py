import boto3
import collections
from datetime import datetime
import calendar

EC2_TAG_NAMES = ['Name']  # EX: dev, prod
ec2_sns = 'arn:aws:sns:ap-south-1:577683050298:CW-Testing'  # Ex: arn:aws:sns:ap-south-1:577683054564:CW-Testing

ec = boto3.client('ec2')
cw = boto3.client('cloudwatch')
    
def lambda_handler(event, context):
    reservations = ec.describe_instances()
    for reservation in reservations['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    ###############################################
                    # Create CPU Alarms
                    cw.put_metric_alarm(
                        AlarmName=(instance_name) + "_CPU_Load_(Lambda)", # Alarm Name
                        AlarmDescription='CPU Utilization ', # Description
                        ActionsEnabled=True, # Indicates whether actions should be executed during any changes to the alarm state. The default is TRUE.
                        AlarmActions=[ec2_sns, ], # provide actions to take if this alarm triggers (like creating new ec2 instance/ sending email)
                        MetricName='CPUUtilization', # Metric Name like (NetworkOut, DiskWriteOps, StatusCheckFailed_Instance, StatusCheckFailed_System)
                        Namespace='AWS/EC2', # The namespace for the metric associated specified in MetricName
                        Statistic='Average', # 'Average'|'Sum'|'Minimum'|'Maximum'
                        Dimensions=[
                            {'Name': "InstanceId", 'Value': instance_id}, ], # ID's for the metric specified in MetricName
                        Period=300, # The length, in seconds, used each time the metric specified in MetricName is evaluated. Valid values are 10, 30, and any multiple of 60.
                        EvaluationPeriods=1, # The number of periods over which data is compared to the specified threshold.
                        Threshold=70.0, # The value against which the specified statistic is compared.
                        ComparisonOperator='GreaterThanOrEqualToThreshold') #T he arithmetic operation to use when comparing the specified statistic and threshold
                    ###############################################
                    # Create StatusCheckFailed Alamrs
                    cw.put_metric_alarm(
                        AlarmName=(instance_name) + "_StatusCheckFailed_Instance(Lambda)",
                        AlarmDescription='StatusCheckFailed_Instance',
                        ActionsEnabled=True,
                        AlarmActions=[ec2_sns, ],
                        MetricName='StatusCheckFailed_Instance',
                        Namespace='AWS/EC2',
                        Statistic='Average',
                        Dimensions=[
                            {'Name': "InstanceId", 'Value': instance_id}, ],
                        Period=900,
                        EvaluationPeriods=1,
                        Threshold=1,
                        ComparisonOperator='GreaterThanOrEqualToThreshold')
                    ###############################################
                    # Create StatusCheckFailed_System Alamrs
                    cw.put_metric_alarm(
                        AlarmName=(instance_name) +
                        "_StatusCheckFailed_System_(Lambda)",
                        AlarmDescription='StatusCheckFailed_System ',
                        ActionsEnabled=True,
                        AlarmActions=[ec2_sns],
                        MetricName='StatusCheckFailed_System',
                        Namespace='AWS/EC2',
                        Statistic='Average',
                        Dimensions=[
                            {'Name': "InstanceId", 'Value': instance_id}, ],
                        Period=900,
                        EvaluationPeriods=1,
                        Threshold=1,
                        ComparisonOperator='GreaterThanOrEqualToThreshold')
                    cw.put_metric_alarm(
                        AlarmName=(instance_name) +
                        "_StatusCheckFailed_Any_(Lambda)",
                        AlarmDescription='StatusCheckFailed_Any ',
                        ActionsEnabled=True,
                        AlarmActions=[ec2_sns],
                        MetricName='StatusCheckFailed',
                        Namespace='AWS/EC2',
                        Statistic='Average',
                        Dimensions=[
                            {'Name': "InstanceId", 'Value': instance_id}, ],
                        Period=300,
                        EvaluationPeriods=1,
                        Threshold=1,
                        ComparisonOperator='GreaterThanOrEqualToThreshold')