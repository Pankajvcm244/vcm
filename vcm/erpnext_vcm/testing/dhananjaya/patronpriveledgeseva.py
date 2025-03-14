# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# clear

# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def add_patronpriveledgeseva():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/patronpriveledgeseva-try-1.xlsx"  # Change as needed

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"ID", "Patron", "Occasion","Month"}
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
        if pd.isna(row["ID"]) or pd.isna(row["Patron"] ):
            skipped_count += 1
            continue

        p_id = row.get("ID")
        patron = row.get("Patron")
        day = row.get("Day")
        month = row.get("Month")
        occasion = row.get("Occasion")        
        patron_name = row.get("Patron Name")
        preacher = row.get("Preacher")
        if not patron:
                not_a_seva += 1
                continue  # Skip rows without a name        
        
        # Handle NaN values by replacing them with None
        occasion = None if pd.isna(occasion) else occasion
        # Check if LLP Preacher already exists
        if frappe.db.exists("Patron Privilege Puja", p_id):
            frappe.msgprint(f"Patron Privilege Puja {p_id} already exists.")
            continue

        #logging.debug(f"update-1 are: {preacher_name}, {preacher_ID} , {preacher_mobile}, {preacher_email}")
        # Debugging: Print existing child table entries
        #logging.debug(f"Existing users for {preacher_name}: {[user.email for user in preacher.get('llp_preacher_users', [])]}")
        try:
            # Create new LLP Preacher entry
            new_patronprivpuja = frappe.get_doc({
                "doctype": "Patron Privilege Puja",
                "initial": p_id, 
                "patron": patron,
                "day": day,
                "month": month,
                "occasion": occasion,
                "patron_name": patron_name,
                "preacher": preacher                
            })
            new_patronprivpuja.insert(ignore_permissions=True)
            updated_count = updated_count + 1
            frappe.db.commit()
            #print(f"Patron Privilege Puja  {p_id} added successfully.")
        
        except Exception as e:
            error += 1
            print(f"Error: {e}")
    print(f"Patron Privilege Puja updated:{updated_count}, Error: {error}, Patron missing: {not_a_seva}, skipped:{skipped_count} added successfully.")
