# Server Script: Update Fiscal Year Accounting Dimension in Submitted Purchase Orders
#bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.fiscal_year_update.update_PO_fiscal_year
import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def update_PO_fiscal_year():
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/PO_fiscal_year.xlsx"
    # Parameters — customize as needed
    target_fiscal_year = "2025-2026"  # Adjust to your fiscal year
    #po_list = ["HKMV-PO-2504-00002-1", "HKMV-PO-2504-00003"]  # List of Purchase Orders to update

    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)
    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"PO_ID"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["PO_ID"]) or pd.isna(row["Company"]):
            skipped_count += 1
            continue

        po_id = row["PO_ID"]
        
        try:
            po = frappe.get_doc("Purchase Order", po_id)
            if not po:
                frappe.throw(f"{po_id} not found. Skipping.")

            if po.docstatus != 1:
                frappe.throw(f"{po_id} is not submitted. Skipping.")

            # Bypass standard restrictions
            frappe.db.set_value("Purchase Order", po_id, "fiscal_year", target_fiscal_year)
            frappe.db.commit()

            frappe.msgprint(f"Fiscal Year updated for {po_id}")

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Error updating {po_id}")
            frappe.msgprint(f"PO fiscal year Error updating {po_id}: {str(e)}")

def update_PI_fiscal_year():
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/PI_fiscal_year.xlsx"
    # Parameters — customize as needed
    target_fiscal_year = "2025-2026"  # Adjust to your fiscal year
    #po_list = ["HKMV-PO-2504-00002-1", "HKMV-PO-2504-00003"]  # List of Purchase Orders to update

    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)
    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"PI_ID"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["PI_ID"]) or pd.isna(row["Company"]):
            skipped_count += 1
            continue

        pi_id = row["PI_ID"]
        
        try:
            pi = frappe.get_doc("Purchase Invoice", pi_id)
            if not pi:
                frappe.throw(f"{pi_id} not found. Skipping.")

            if pi.docstatus != 1:
                frappe.throw(f"{pi_id} is not submitted. Skipping.")

            # Bypass standard restrictions
            frappe.db.set_value("Purchase Invoice", pi_id, "fiscal_year", target_fiscal_year)
            frappe.db.commit()

            frappe.msgprint(f"Fiscal Year updated for {pi_id}")

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Error updating {pi_id}")
            frappe.msgprint(f"PI fiscal year Error updating {pi_id}: {str(e)}")


def update_PE_fiscal_year():
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/PE2_fiscal_year.xlsx"
    # Parameters — customize as needed
    target_fiscal_year = "2025-2026"  # Adjust to your fiscal year
    #po_list = ["HKMV-PO-2504-00002-1", "HKMV-PO-2504-00003"]  # List of Purchase Orders to update

    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)
    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"PE_ID"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["PE_ID"]) or pd.isna(row["Company"]):
            skipped_count += 1
            continue

        pe_id = row["PE_ID"]
        
        try:
            pe = frappe.get_doc("Payment Entry", pe_id)
            if not pe:
                frappe.throw(f"{pe_id} not found. Skipping.")

            if pe.docstatus != 1:
                frappe.throw(f"{pe_id} is not submitted. Skipping.")

            # Bypass standard restrictions
            frappe.db.set_value("Payment Entry", pe_id, "fiscal_year", target_fiscal_year)
            frappe.db.commit()

            frappe.msgprint(f"Fiscal Year updated for {pe_id}")

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Error updating {pe_id}")
            frappe.msgprint(f"PE fiscal year Error updating {pe_id}: {str(e)}")

def update_JV_fiscal_year():
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/JV_fiscal_year.xlsx"
    target_fiscal_year = "2025-2026"

    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    df = pd.read_excel(file_path)
    df = df.dropna(how="all")

    required_columns = {"JE_ID"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    updated_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        je_id = row.get("JE_ID")
        

        if pd.isna(je_id) :
            skipped_count += 1
            continue

        try:
            je = frappe.get_doc("Journal Entry", je_id)
            if not je:
                errors.append(f"{je_id} not found.")
                continue

            if je.docstatus != 1:
                errors.append(f"{je_id} is not submitted.")
                continue

            
            # Get all child rows for this Journal Entry
            child_rows = frappe.get_all(
                "Journal Entry Account",
                filters={"parent": je_id},
                fields=["name"]
            )

            for child in child_rows:
                frappe.db.set_value("Journal Entry Account", child["name"], "fiscal_year", target_fiscal_year)
                frappe.msgprint(f"Fiscal year updated in Journal Entry: {je_id}")
                updated_count += 1
            else:
                skipped_count += 1
                errors.append(f"No matching account rows in {je_id} for company {company}.")

        except Exception as e:
            errors.append(f"Error processing {je_id}: {str(e)}")
            continue

    frappe.msgprint(f"Update complete. {updated_count} updated, {skipped_count} skipped.")
    if errors:
        frappe.msgprint("Errors:\n" + "\n".join(errors))