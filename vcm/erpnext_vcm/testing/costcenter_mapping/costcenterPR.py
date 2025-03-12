# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# bench --site test.vcmerp.in execute vcm.erpnext_vcm.testing.costcenterPR.update_sinv_cost_center
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def update_sinv_cost_center():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/pankajPR-1.xlsx"  # Change as needed

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"PANKAJSINVNO", "PANKAJCOSTC"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["PANKAJSINVNO"]) or pd.isna(row["PANKAJCOSTC"]):
            continue

        doc_ID_no = row["PANKAJSINVNO"]
        new_cost_center = row["PANKAJCOSTC"]
        logging.debug(f"update-1 are: {doc_ID_no}, {new_cost_center} ")
        try:
            # Fetch Sales Invoice
            doc = frappe.get_doc("Purchase Receipt", doc_ID_no)
            logging.debug(f"doc ID number : {doc_ID_no}, {new_cost_center} ")
            # Ensure invoice is in Draft mode
            #if doc.docstatus != 0:
            #    errors.append(f"Invoice {sales_invoice_no} is not in Draft state.")
            #    continue
            doc.cost_center = new_cost_center
            logging.debug(f"****** Doc : {doc_ID_no},  {doc.cost_center}, {new_cost_center} ")
            # Update cost center for each item
            #for item in doc.items:
            #    logging.debug(f"****** Items : {doc_ID_no}, {item.item_code}, {item.cost_center}, {new_cost_center} ")
            #    item.cost_center = new_cost_center

            # Save and commit changes
            doc.save()
            #frappe.db.commit()
            updated_count += 1
            #logging.error(f"****** update count :  {updated_count} ")

        except Exception as e:
            errors.append(f"Failed to update {doc_ID_no}: {str(e)}")

    # Return script execution summary
    return f"Updated {updated_count} invoices.\n\n Errors: {errors}, {len(errors)}."
