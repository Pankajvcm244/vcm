# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# bench --site test.vcmerp.in execute vcm.erpnext_vcm.testing.LLPPreacher.add_llppreacher
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def add_llppreacher():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/Preacher_1.xlsx"  # Change as needed

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"Full Name", "Initial"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    not_a_preacher = 0
    not_a_user = 0
    duplicate_user = 0
    error  = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["Full Name"]) or pd.isna(row["Initial"]):
            continue

        preacher_name = row.get("Full Name")
        preacher_ID = row.get("Initial")
        preacher_mobile = row.get("Mobile Number")
        preacher_email = row.get("User (Allowed Users)")

        if not preacher_name:
                not_a_preacher += 1
                continue  # Skip rows without a name
        
        # Check if email exists in User table, otherwise child table entry will fail
        if preacher_email and not frappe.db.exists("User", preacher_email):
            print(f"Error: {preacher_email} is not a valid user in the system.")
            not_a_user += 1
            continue
        
        # Handle NaN values by replacing them with None
        preacher_ID = None if pd.isna(preacher_ID) else preacher_ID
        preacher_mobile = None if pd.isna(preacher_mobile) else preacher_mobile
        preacher_email = None if pd.isna(preacher_email) else preacher_email

        # Check if LLP Preacher already exists
        if frappe.db.exists("LLP Preacher", preacher_name):
            frappe.msgprint(f"LLP Preacher {preacher_name} already exists.")
            duplicate_user += 1
            continue

        #logging.debug(f"update-1 are: {preacher_name}, {preacher_ID} , {preacher_mobile}, {preacher_email}")
        # Debugging: Print existing child table entries
        #logging.debug(f"Existing users for {preacher_name}: {[user.email for user in preacher.get('llp_preacher_users', [])]}")
        try:
            # Create new LLP Preacher entry
            new_preacher = frappe.get_doc({
                "doctype": "LLP Preacher",
                "initial": preacher_ID,
                "full_name": preacher_name,
                "mobile_no": preacher_mobile,
                "email": preacher_email,
                "include_in_analysis": 1,
                "allowed_users": []
            })

            if preacher_email:
                #new_user = new_preacher.append("allowed_users", {})
                #new_user.user = preacher_email
                new_preacher.append("allowed_users", {"user": preacher_email})

            new_preacher.insert(ignore_permissions=True)
            frappe.db.commit()
            updated_count = updated_count + 1
            print(f"LLP Preacher {preacher_name} added successfully.")
        except Exception as e:
            print(f"Error: {e}")
            error += 1
    print(f"Preacher updated:{updated_count}, Error: {error} Duplicate {duplicate_user}, User missing {not_a_user},Preacher name missing: {not_a_preacher} added successfully.")
