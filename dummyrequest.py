import requests
import json

with open('extract.json', 'r', encoding='utf-8') as f:
    user_sessions = json.load(f)  # or use the NDJSON method above

data = {
    "prompt": "what can you understand from this data, can you give more detailed insights and generate stats and things to suggest in order to make page better, your task is to analyze the data and tell what users tend to do in general given this data.for each session analyt,ze the user actions and give an overall insights on each section aggregated ",
    "user_json": json.dumps(user_sessions)  # Convert list to JSON string for sending
}

response = requests.post("http://127.0.0.1:5000/ask", json=data)
print(response.json())