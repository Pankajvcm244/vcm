import frappe
from frappe import _
from erpnext.stock.doctype.purchase_receipt import purchase_receipt_dashboard


def get_data(data=None):
    # Load core dashboard data first
    if data is None:
        data = purchase_receipt_dashboard.get_data()

    # Add custom internal link to VCM Gate-In
    data.setdefault("internal_links", {})
    data["internal_links"]["VCM Gate-In"] = "custom_gate_in_reference"

    # Add VCM Gate-In to Transactions section
    data["transactions"].append({
        "label": frappe._("VCM Transactions"),
        "items": ["VCM Gate-In"]
    })

    return data