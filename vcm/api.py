import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_erp_domains():
    # Fetch records from the custom Doctype 'ERP Domain'
    records = frappe.get_all(
        'VCM ERP Domain',  # Doctype name
        fields=['erp_title', 'erp_address']  # Fields to fetch
    )
    return records