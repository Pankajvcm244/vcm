# Server Script: Update Fiscal Year Accounting Dimension in Submitted Purchase Orders
#bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.fiscal_year_update.update_fiscal_year
import frappe

import logging
logging.basicConfig(level=logging.DEBUG)

def update_fiscal_year():
    # Parameters — customize as needed
    target_fiscal_year = "2025-2026"  # Adjust to your fiscal year
    po_list = ["HKMV-PO-2504-00002-1", "HKMV-PO-2504-00003"]  # List of Purchase Orders to update

    # Loop through each PO
    for po_name in po_list:
        try:
            po = frappe.get_doc("Purchase Order", po_name)
            if not po:
                frappe.throw(f"{po_name} not found. Skipping.")

            if po.docstatus != 1:
                frappe.throw(f"{po_name} is not submitted. Skipping.")

            # Bypass standard restrictions
            frappe.db.set_value("Purchase Order", po_name, "fiscal_year", target_fiscal_year)
            frappe.db.commit()

            frappe.msgprint(f"Fiscal Year updated for {po_name}")

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Error updating {po_name}")
            frappe.msgprint(f"Error updating {po_name}: {str(e)}")