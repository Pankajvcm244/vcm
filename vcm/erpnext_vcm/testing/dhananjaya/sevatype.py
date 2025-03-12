# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.sevatype.add_sevatype
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def add_sevatype():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/sevatype-test-1.xlsx"  # Change as needed

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"Company", "Seva Name", "80G Applicable","Patronship Allowed","Enabled","Include in Analysis","Is CSR Allowed"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    not_a_company = 0
    error  = 0
    skipped_count = 0


    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["Company"]) or pd.isna(row["Seva Name"] ):
            skipped_count += 1
            continue

        enabled_flag = row.get("Enabled")
        company_name = row.get("Company")
        seva_name = row.get("Seva Name")
        accounts = row.get("Account")
        cash_account = row.get("Cash Account")        
        g80_applicable = row.get("80G Applicable")
        patronship_flag = row.get("Patronship Allowed")
        analysis_flag = row.get("Include in Analysis")
        in_kind = row.get("In-Kind")
        # there is space in Donation type before satrt
        donation_type = row.get(" Donation Type")
        priority = row.get("Priority")
        csr_account = row.get("CSR Account")        
        csr_flag = row.get("Is CSR Allowed") 

        if not company_name:
                not_a_company += 1
                continue  # Skip rows without a name
        
        
        # Handle NaN values by replacing them with None
        accounts = None if pd.isna(accounts) else accounts
        cash_account = None if pd.isna(cash_account) else cash_account
        csr_account = None if pd.isna(csr_account) else csr_account

        # Check if LLP Preacher already exists
        if frappe.db.exists("Seva Type", seva_name):
            frappe.msgprint(f"Seva Type {seva_name} already exists.")
            continue

        #logging.debug(f"update-1 are: {preacher_name}, {preacher_ID} , {preacher_mobile}, {preacher_email}")
        # Debugging: Print existing child table entries
        #logging.debug(f"Existing users for {preacher_name}: {[user.email for user in preacher.get('llp_preacher_users', [])]}")
        try:
            # Create new LLP Preacher entry
            new_sevatype = frappe.get_doc({
                "doctype": "Seva Type",
                "initial": seva_name, 
                "enabled": enabled_flag,
                "company": company_name,
                "seva_name": seva_name,
                "account": accounts,
                "cash_account": cash_account,
                "80g_applicable": g80_applicable,
                "patronship_allowed": patronship_flag,
                "include_in_analysis": analysis_flag,
                "csr_allowed": csr_flag,
                "kind": in_kind,
                "donation_type" : donation_type,
                "priority": priority,
                "csr_account": csr_account
            })
            new_sevatype.insert(ignore_permissions=True)
            updated_count = updated_count + 1
            frappe.db.commit()
            print(f"SevaType {seva_name} added successfully.")
        
        except Exception as e:
            error += 1
            print(f"Error: {e}")
    print(f"SevaType updated:{updated_count}, Error: {error}, Company missing: {not_a_company} added successfully.")
