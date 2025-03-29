# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/JVcommand-1.log
# bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.doc_rename.update_docname
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def update_docname():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/pankaj3.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/BudgetHeadProd-1.xlsx"
    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"OldName",  "NewName"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["OldName"]) or pd.isna(row["NewName"]):
            continue        
        new_docname = row["NewName"]
        old_docname = row["OldName"]
        logging.debug(f"update {updated_count} is : {new_docname}, {old_docname} ")
        try:
            # Fetch Document
            doc = frappe.get_doc("Budget Head", old_docname)
            #logging.debug(f"SINV number : {old_docname} ")
            # Ensure invoice is in Draft mode
            # if doc.docstatus != 0:
            #     errors.append(f"Invoice {doc_ID_no} is not in Draft state.")
            #     continue

            # Update cost center for each item
            # for account in doc.accounts:
            #     logging.debug(f"****** Items : {doc_ID_no}, {account.cost_center}, {new_cost_center} ")
            #     account.cost_center = new_cost_center

            # Save and commit changes
            frappe.rename_doc("Budget Head", old_docname, new_docname)
            #doc.save()  rename already saves document
            frappe.db.commit()
            updated_count += 1
            #logging.error(f"****** update count :  {updated_count} ")

        except Exception as e:
            errors.append(f"Failed to update {old_docname}: {str(e)}")

    # Return script execution summary
    #return f"Updated {updated_count} invoices.\n\n Errors: {errors}, {len(errors)}."
    return f"Renamed {updated_count} Docs.\n\n Errors: {errors}."