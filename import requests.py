import requests

# Replace with your Discord Webhook URL
DISCORD_WEBHOOK_URL = "Your own webhook goes here :)"
instances = "This is a test"
def send_test_message():
    message = {
        "content": f"🛑 **EC2 Cost Optimization Alert** 🛑\n\nThe following **EC2 instances** were stopped due to low utilization:\n```\n{instances}\n```",
        "username": "AWS Cost Optimizer",
        "avatar_url": "https://aws.amazon.com/favicon.ico"  # AWS logo (optional)
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    if response.status_code == 204:
        print("✅ Test message sent successfully!")
    else:
        print(f"❌ Failed to send test message: {response.status_code}, {response.text}")

if __name__ == "__main__":
    send_test_message()
