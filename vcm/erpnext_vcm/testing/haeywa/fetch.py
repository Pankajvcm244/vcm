import json
import requests
from datetime import datetime

def get_transactions():
    # Step 1: Getting token from /v1/authorize
    auth_url = "https://devanalytics.haeywa.ai/v1/authorize"
    headers = {
        'X-Client-Id': 'HYWADOTNOVA',
        'X-Client-Secret': 'K3O9rR6019up2gm5eKyk11hoNG1411Ai'
    }

    auth_response = requests.post(auth_url, headers=headers)

    if auth_response.status_code != 200:
        return {"status": "ERROR", "subCode": auth_response.status_code, "message": "Failed to get token"}

    auth_data = auth_response.json()
    token_auth = auth_data.get("data", {}).get("token")

    if not token_auth:
        return {"status": "ERROR", "subCode": 401, "message": "Token not found in response"}

    # Step 2: Use the token for /v1/transactions/GST request
    gst = "06AAICD8897M1ZP"
    duration = 4
    start_date = "2025-02-25"
    end_date = "2025-03-02"

    api_url = "https://devanalytics.haeywa.ai/v1/transactions/GST"
    headers = {
        "Authorization": f"Bearer {token_auth}",  
        "Content-Type": "application/json"
    }
    payload = {
        "gst": gst,
        "duration": duration,
        "start_date": start_date,
        "end_date": end_date
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()

        response_data = response.json()
        transactions = response_data.get("data", [])

        if not transactions:
            return {"status": "ERROR", "subCode": 404, "message": "No transactions found"}

        return {"status": "SUCCESS", "data": transactions}

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            return {"status": "ERROR", "subCode": 401, "message": "Unauthorized: Invalid token"}
        return {"status": "ERROR", "subCode": response.status_code, "message": str(http_err)}

    except requests.exceptions.RequestException as e:
        return {"status": "ERROR", "subCode": 500, "message": f"Failed to fetch transactions: {str(e)}"}


def transform_transaction(transaction):
    return {
        "txn_id": transaction.get("ref_Number"),
        "doctype": "Payment Entry",
        "payment_type": "Pay",
        "company": transaction.get("business_name"),
        "party_type": "Supplier",
        "party": transaction.get("emp_id"), 
        "paid_from": "",
        "paid_from_account_currency": "INR",
        "paid_from_account": "",
        "paid_to_account": "",
        "cost_center": transaction.get("circle_Codes", "NA"), 
        "budget_head": transaction.get("category", "NA"), 
        "location": transaction.get("location", "NA"),  
        "paid_amount": transaction.get("dr", 0),  
        "posting_date": transaction.get("date", "").split()[0],
        "reference_no": f"{transaction.get('utr_number', '')}",
        "reference_date": transaction.get("date", "").split()[0],
        "received_amount": transaction.get("dr", 0),
        "source_currency": "INR",
        "target_currency": "INR",
        "source_exchange_rate": "1"
    }


# Run the function and transform transactions
if __name__ == "__main__":
    result = get_transactions()

    if result["status"] == "SUCCESS":
        transformed_transactions = [transform_transaction(tx) for tx in result["data"]]
        print(json.dumps(transformed_transactions, indent=2))
    else:
        print(json.dumps(result, indent=2))
