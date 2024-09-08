import json

import requests

url = "http://219.147.99.189:5205/webhooks/foryor_robot/webhook"

payload = json.dumps({
  "input_content": "乳腺癌的存活率是多少？",
  "input_type": "text",
  "message_id": "16093",
  "meta_data": {},
  "session_id": "493nb78ak3sqr",
  "timestamp": 1698728781053,
  "input_intent": None,
  "customer_id": None
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
