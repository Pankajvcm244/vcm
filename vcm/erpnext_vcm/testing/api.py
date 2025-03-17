#bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.dhananjaya.donorcreation_request.donor_creation_request
import requests

# ERPNext credentials and URL
base_url = "https://test.vcmerp.in"
api_key = "da6ab267bbc616f"
api_secret = "2de12b669f3441f"

# Endpoint for the DocType (e.g., Customer)
endpoint = f"{base_url}/api/resource/Customer"

# Data to upload
data = {
    "customer_name": "Pankaj API",
    "customer_type": "Individual",
    "customer_group": "Commercial",
    "territory": "India"
}

# Make the request
response = requests.post(
    endpoint,
    json=data,
    headers={
        "Authorization": f"token {api_key}:{api_secret}"
    }
)

# Print response
print(response.status_code, response.json())
________________________________________

