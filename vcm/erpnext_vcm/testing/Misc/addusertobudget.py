import frappe
import pandas as pd
import os
import logging
logging.basicConfig(level=logging.DEBUG)
#bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.addusertobudget.add_users2budget

def add_users2budget():
    
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/PS2.xlsx"

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"BudgetID", "Email-1", }
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["BudgetID"]) or pd.isna(row["Email-1"]):
            continue

        budget_name = row['BudgetID']
        #print(f"VCM Budget '{budget_name}' found.")
        if pd.isna(budget_name) :
            print(f"Skipping row with missing Budget name: {budget_name}, {row}")
            continue
        try:    
            # Get the VCM Budget document
            vcm_doc = frappe.get_doc("VCM Budget", budget_name)
        except frappe.DoesNotExistError:
            print(f"VCM Budget '{budget_name}' not found. Skipping.")
            continue

        for col in ['Email-1', 'Email-2', 'Email-3', 'Email-4', 'Email-5']:
            vcm_email = row[col]
            #print(f" in loop {vcm_email} to {budget_name}")
            if pd.isna(vcm_email):
                continue

            # Avoid duplicates
            if any(child.user == vcm_email for child in vcm_doc.allowed_users):
                print(f"{vcm_email} already exists in {budget_name}")
                continue

            vcm_doc.append("allowed_users", {
                "user": vcm_email
            })
            #print(f"Added {vcm_email} to {budget_name}")

        vcm_doc.save()