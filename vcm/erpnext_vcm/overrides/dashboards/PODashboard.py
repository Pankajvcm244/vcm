import frappe
from frappe import _
from erpnext.buying.doctype.purchase_order import purchase_order_dashboard

def get_data(data=None):
    if data is None:
        data = purchase_order_dashboard.get_data()

    # Add custom section
    data["transactions"].append({
        "label": _("VCM Transactions"),
        "items": ["VCM Gate-In"]
    })

    return data