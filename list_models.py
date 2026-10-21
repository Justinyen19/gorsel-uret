import os, requests, json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LEONARDO_API_KEY")
headers = {
    "accept": "application/json",
    "authorization": f"Bearer {API_KEY}"
}

res = requests.get('https://cloud.leonardo.ai/api/rest/v1/platformModels', headers=headers)
if res.status_code == 200:
    data = res.json()
    models = data.get('custom_models', [])
    for m in models:
        print(f"ID: {m['id']} - Name: {m['name']}")
else:
    print(f"Error: {res.status_code} - {res.text}")
