import os
import requests
import json
from mage_ai.data_preparation.shared.secrets import get_secret_value

DISCORD_WEBHOOK_URL = get_secret_value("DISCORD_WEBHOOK_URL")
HEADERS = {"Content-Type": "application/json"}
EXPECTED_STATUS = 204

if 'callback' not in globals():
    from mage_ai.data_preparation.decorators import callback


@callback('success')
def success_callback(parent_block_data, **kwargs):
    try:
        block_uuid = kwargs.get('block_uuid')
        execution_date = kwargs.get('execution_date')
        alert = f"Successful pipeline run.\nExecuted at: {execution_date}"
        payload = {
            'username': 'mage_alerts',
            "content": alert
        }
        response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=HEADERS)
        
        if response.status_code != EXPECTED_STATUS:
            raise Exception(f"Error: Message was not posted to webhook correctly. Status: {response.status_code}\n")

        print("Message sent successfully\n")
    except Exception as e:
        print(f"Failed to send message, response code: {e}")


@callback('failure')
def failure_callback(parent_block_data, **kwargs):
    try:
        pipeline_uuid = kwargs.get('pipeline_uuid')
        execution_date = kwargs.get('execution_date')
        alert = f"Unsuccessful pipeline run.\nExecuted at: {execution_date}"
        payload = {
            'username': 'mage_alerts',
            "content": alert
        }
        response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=HEADERS)
        
        if response.status_code != EXPECTED_STATUS:
            raise Exception(f"Error: Message was not posted to webhook correctly. Status: {response.status_code}\n")

        print("Message sent successfully\n")
    except Exception as e:
        print(f"Failed to send message, response code: {e}")