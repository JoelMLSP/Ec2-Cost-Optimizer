import boto3
import requests
import datetime


ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')


DISCORD_WEBHOOK_URL = "Your own webhook goes here :)"

CPU_THRESHOLD = 10.0
CHECK_PERIOD = 86400

def get_low_utilization_instances():

    low_utilization_instances = []


    instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']


            metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=CHECK_PERIOD),
                EndTime=datetime.datetime.utcnow(),
                Period=3600,  # 1 Hour Period
                Statistics=['Average']
            )

            if metrics['Datapoints']:
                avg_cpu = metrics['Datapoints'][0]['Average']
                if avg_cpu < CPU_THRESHOLD:
                    low_utilization_instances.append(instance_id)

    return low_utilization_instances

def send_discord_alert(instances):

    if not instances:
        return

    message = {
        "content": f"🛑 **EC2 Cost Optimization Alert** 🛑\n\nThe following **EC2 instances** were stopped due to low utilization:\n```\n{instances}\n```",
        "username": "AWS Cost Optimizer",
        "avatar_url": "https://aws.amazon.com/favicon.ico"  # AWS logo (optional)
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    if response.status_code == 204:
        print("✅ Discord notification sent successfully!")
    else:
        print(f"❌ Failed to send Discord alert: {response.text}")

#make different rules for this in the futrue.

def stop_instances(instances):

    if not instances:
        print("No underutilized instances found.")
        return


    ec2.stop_instances(InstanceIds=instances)
    print(f"Stopped instances: {instances}")


    send_discord_alert(instances)


def lambda_handler(event, context):

    underutilized_instances = get_low_utilization_instances()
    stop_instances(underutilized_instances)
    return {"status": "success", "stopped_instances": underutilized_instances}
