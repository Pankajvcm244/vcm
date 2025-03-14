# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.dhananjaya.patronsevatype.add_patronsevatype
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def add_patronsevatype():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/patronsevatype-final-1.xlsx"  # Change as needed

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"Seva Code", "Enabled", "Seva Name","Seva Amount"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    not_a_seva = 0
    error  = 0
    skipped_count = 0


    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["Seva Code"]) or pd.isna(row["Seva Name"] ):
            skipped_count += 1
            continue

        enabled = row.get("Enabled")
        seva_code = row.get("Seva Code")
        seva_name = row.get("Seva Name")
        seva_amount = row.get("Seva Amount")
        includedin_commitment = row.get("Included in Commitment Status")        
        priveledge_puja_no = row.get("Privilege Pujas")
        if not seva_name:
                not_a_seva += 1
                continue  # Skip rows without a name        
        
        # Handle NaN values by replacing them with None
        seva_name = None if pd.isna(seva_name) else seva_name
        # Check if LLP Preacher already exists
        if frappe.db.exists("Patron Seva Type", seva_code):
            frappe.msgprint(f"Patron Seva Type {seva_code} already exists.")
            continue

        #logging.debug(f"update-1 are: {preacher_name}, {preacher_ID} , {preacher_mobile}, {preacher_email}")
        # Debugging: Print existing child table entries
        #logging.debug(f"Existing users for {preacher_name}: {[user.email for user in preacher.get('llp_preacher_users', [])]}")
        try:
            # Create new LLP Preacher entry
            new_sevatype = frappe.get_doc({
                "doctype": "Patron Seva Type",
                "initial": seva_name, 
                "enabled": enabled,
                "seva_code": seva_code,
                "seva_name": seva_name,
                "seva_amount": seva_amount,
                "included_in_commitment_status": includedin_commitment,
                "privilege_pujas": priveledge_puja_no                
            })
            new_sevatype.insert(ignore_permissions=True)
            updated_count = updated_count + 1
            frappe.db.commit()
            print(f"Patron Seva Type {seva_name} added successfully.")
        
        except Exception as e:
            error += 1
            print(f"Error: {e}")
    print(f"Patron Seva Type updated:{updated_count}, Error: {error}, Company missing: {not_a_seva}, skipped:{skipped_count} added successfully.")
