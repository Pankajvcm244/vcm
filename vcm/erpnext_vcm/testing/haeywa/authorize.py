import requests

url = "https://devanalytics.haeywa.ai/v1/authorize"

payload = {}
files={}
headers = {
  'X-Client-Id': 'HYWADOTNOVA',
  'X-Client-Secret': 'K3O9rR6019up2gm5eKyk11hoNG1411Ai'
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
