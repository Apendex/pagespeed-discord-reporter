import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
image_file = "pagespeed_insights_results.png"
json_file = "pagespeed_insights_results.json"
website_url = os.getenv("WEBSITE_URL")

# Load the JSON data to get the viewer URLs
try:
    with open(json_file, "r") as f:
        data = json.load(f)
        mobile_url = data.get("mobile_viewer_url", "https://pagespeed.web.dev")
        desktop_url = data.get("desktop_viewer_url", "https://pagespeed.web.dev")
        target_url = data.get("url", website_url)
except Exception as e:
    print(f"Error loading JSON data: {e}")
    mobile_url = desktop_url = "https://pagespeed.web.dev"
    target_url = website_url

# 1. Define your payload structure referencing the attached file
payload = {
    "embeds": [
        {
            "title": f"PageSpeed Insights for {target_url}",
            "description": (
                f"**Full Reports:**\n"
                f"[Mobile Report]({mobile_url})\n"
                f"[Desktop Report]({desktop_url})\n"
                f"Generated from [PageSpeed Insights](https://pagespeed.web.dev)"
            ),
            "image": {
                "url": f"attachment://{image_file}"
            }
        }
    ]
}

# 2. Open the file in binary mode and send the POST request
with open(image_file, "rb") as file:
    form_data = {
        "payload_json": (None, json.dumps(payload), "application/json")
    }
    file_data = {
        "file": (image_file, file, "image/png")
    }
    
    response = requests.post(webhook_url, data=form_data, files=file_data)

# 3. Verify the status of your request
if response.status_code == 200 or response.status_code == 204:
    print("Success: Image sent to Discord.")
else:
    print(f"Failed with status code: {response.status_code}")
    print(response.text)

