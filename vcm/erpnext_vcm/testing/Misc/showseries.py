import frappe
from frappe.utils import now_datetime
# bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.showseries.show_series_and_counters  

def get_resolved_series_key(series_template):
    """Convert a series template like 'SINV-.YYYY.-' to actual series key"""
    today = now_datetime()
    replacements = {
        ".YYYY.": today.strftime("%Y"),
        ".YY.": today.strftime("%y"),
        ".MM.": today.strftime("%m"),
        ".DD.": today.strftime("%d")
    }
    key = series_template
    for token, value in replacements.items():
        key = key.replace(token, value)
    return key

def show_series_and_counters():
    doctype = "Donation Credit"
    meta = frappe.get_meta(doctype)
    options = []

    # Check if overridden via Property Setter
    overridden = frappe.db.get_value(
        "Property Setter",
        {
            "doc_type": doctype,
            "property": "options",
            "field_name": "naming_series"
        },
        "value"
    )
    if overridden:
        options = overridden.split("\n")
    else:
        field = meta.get_field("naming_series")
        if field and field.options:
            options = field.options.split("\n")

    print(f"Naming Series Options for {doctype}:\n")

    for series in options:
        actual_key = get_resolved_series_key(series)
        current = frappe.db.get_value("Series", actual_key, "current", order_by=None) or 0

        print(f"{series} → Current Count: {current}")

# Example usage
#show_series_and_counters()  

def print_series():
    # Example series prefix
    series_prefix = "HKMV-DC-25-1"
    current = frappe.db.get_value("Series", actual_key, "current", order_by=None) or 0
    print(f"Current counter for {series_prefix} is {current}")
