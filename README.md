# AWS EC2 Cost Optimization Project

This project automates the detection and management of underutilized AWS EC2 instances to reduce cloud costs. Using **AWS Lambda** and **EventBridge Scheduler**, the function periodically identifies instances with low utilization and stops them. Notifications are sent to a designated **Discord channel** using a webhook for visibility.

---

## Prerequisites

1. **AWS Account** with appropriate permissions:
   - `AmazonEC2ReadOnlyAccess`
   - `AmazonEC2FullAccess`
   - `AWSLambdaBasicExecutionRole`
   - `AmazonEventBridgeSchedulerFullAccess`
2. **Discord Webhook** for sending notifications.
3. Python installed locally for testing and packaging dependencies.

You can either follow these steps along and write the code aswell or you can just download the project, if you do so then you will only need to create your webhook and follow the steps along from the AWS part

---

## Project Setup

### 1. **Set Up the Lambda Function**

1. **Create the Lambda Function:**
   - Go to the [AWS Lambda Console](https://console.aws.amazon.com/lambda/home).
   - Click **Create function** → **Author from scratch**.
   - Function name: `EC2_Cost_Optimizer`.
   - Runtime: `Python 3.8+`.

2. **Attach an IAM Role:**
   - Create an IAM Role with the following permissions:
     - `AmazonEC2ReadOnlyAccess`
     - `AmazonEC2FullAccess`
     - `AWSLambdaBasicExecutionRole`
     - `AmazonEventBridgeSchedulerFullAccess`
     - `CloudWatchReadOnlyAccess`
   - Attach the role to the Lambda function.
     
  ![image3](https://github.com/user-attachments/assets/b72a0b84-582b-45fe-b2e1-6ea2e757bd14)
3. **Write the Lambda Code:**
   - Paste the following code into the **Function Code** section of the Lambda function:

```python
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

```

4. **Install Dependencies:**
   - Locally, create a directory for the project.
   - Install `requests` library:
     ```bash
     pip install requests -t .
     ```
     ![image8](https://github.com/user-attachments/assets/1549aa5f-fef9-4b24-838e-f8c86c762658)

   - Zip the directory, including `lambda_function.py` and the `requests` folder.
   - Upload the ZIP file to the Lambda function.

---

### 2. **Set Up Discord Webhook**

1. Open Discord and go to the desired channel.
2. Navigate to **Channel Settings → Integrations → Webhooks**.
3. Click **New Webhook**, name it, and copy the **Webhook URL**.
   ![image5](https://github.com/user-attachments/assets/075fbe11-1a0f-45aa-b8b7-f8e42fd42b1c)

5. Replace `DISCORD_WEBHOOK_URL` in the Lambda code with your Webhook URL.

---

### 3. **Set Up EventBridge Scheduler**

1. Open the [EventBridge Scheduler Console](https://console.aws.amazon.com/events/home#/schedules).
2. Click **Create schedule**.
3. Configure the schedule:
   - **Name**: `EC2_Cost_Optimizer_Scheduler`
   - **Schedule Type**: Rate expression (`rate(1 hours)`).
   - **Time Zone**: Set as needed (e.g., `Europe/Stockholm`).
4. Set the **Target**:
   - **Target Type**: AWS Lambda.
   - **Function**: Select `EC2_Cost_Optimizer`.
5. **Permissions**:
   - Select `Use an existing role` and choose the IAM role (`EC2_Cost_Optimizer-role-...`).
6. Click **Create schedule**.

---![image9](https://github.com/user-attachments/assets/64c2795a-d6ca-4991-810e-8baaad9af0d7)


## Testing

1. **Send a Test Message to Discord:**
   - Modify the Lambda handler to send a test message:
   ```python
   def lambda_handler(event, context):
       send_discord_alert(["Test instance ID"])
       return {"status": "test sent"}
   ```



2. **Manually Trigger the Lambda Function:**
   - Go to AWS Lambda Console → Test the function.
  
     ![image4](https://github.com/user-attachments/assets/f85acd4a-95ce-4163-b77f-caa3345f6f1d)


3. **Verify Logs:**
   - Open **CloudWatch Logs** and ensure the function runs without errors.

4. **Check Discord:**
   - Verify that alerts are received in the specified Discord channel.
     
  ![image2](https://github.com/user-attachments/assets/f7b64ee5-63d8-465d-ab02-5391a96fa672)
---

## Enhancements for the future

1. **Add Tag-Based Exclusions:**
   - Modify the Lambda function to skip instances with specific tags (e.g., `Always-On`).

2. **Generate Cost Reports:**
   - Use AWS Cost Explorer API to calculate savings from stopped instances.



