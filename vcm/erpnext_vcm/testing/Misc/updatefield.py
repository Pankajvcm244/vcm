# Server Script: Update Fiscal Year Accounting Dimension in Submitted Purchase Orders
#bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.updatefield.updatePI_field
import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)


def updatePI_field():
    invoice_name = "HPIO2504-00042"    

    fiscal_year = "2025-2026" 
    if fiscal_year:
        # Set the value in the custom field (assumes 'fiscal_year' exists)
        frappe.db.set_value("Purchase Invoice", invoice_name, "fiscal_year", fiscal_year)
        frappe.db.commit()
        print(f"✅ Updated {invoice_name} with Fiscal Year: {fiscal_year}")
    else:
        print(f"⚠️ No matching Fiscal Year found for date {invoice_name} ")



# bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.updatefield.update_child_field
def update_child_field():
    print("Starting child update function...")
    je_id = "HKMV-JV-2504-00042"  # Example Journal Entry ID
    target_location = "VRN"  # Example location  
    target_budget_head = "AUDIT EXPENSES"  # Example budget head or cost center
    
    # Get all child rows for this Journal Entry
    child_rows = frappe.get_all(
        "Journal Entry Account",
        filters={"parent": je_id},
        fields=["name"]
    )
    print(f"Found child rows for {je_id}: {child_rows}")
    if not child_rows:
        frappe.msgprint(f"⚠️ No matching account rows found in Journal Entry: {je_id}")
        return   
    
    for child in child_rows:
        print(f"inside child {je_id} ")
        frappe.db.set_value("Journal Entry Account", child["name"], "location", target_location)
        frappe.db.set_value("Journal Entry Account", child["name"], "budget_head", target_budget_head)
        

    frappe.msgprint(f"✅ Fiscal year, location, and budget head updated in  rows for Journal Entry: {je_id}")
