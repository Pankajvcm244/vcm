# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.dhananjaya.donationcreation_request.add_donation_creation_request
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def add_donation_creation_request():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/donationcreation-try-1.xlsx"  # Change as needed

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"ID", "Full Name", "LLP Preacher","Status"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    added_count = 0
    not_a_seva_sub_type = 0
    error  = 0
    skipped_count = 0
    duplicate_count  = 0

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["Seva Name"] ):
            skipped_count += 1
            continue
              
        id_no = row.get("ID")
        fullname = row.get("Full Name")
        contact_number = row.get("Contact Number") 
        address_type = row.get("Address Type")
        add_line1 = row.get("Address Line 1")
        city = row.get("City/Town")        
        state = row.get("State")
        status = row.get("Status")
        llp_preacher = row.get("LLP Preacher")
        email = row.get("Email")
        add_line2 = row.get("Address Line 2")
        country = row.get("Country")  
        pincode = row.get("PIN Code")
        pan_no = row.get("PAN Number") 
        aadhar_no = row.get("Aadhar Number") 
             
        
        if not id_no:
                not_a_req_type += 1
                continue  # Skip rows without a name        
        
        # Handle NaN values by replacing them with None        
        email = None if pd.isna(email) else email
        add_line2 = None if pd.isna(add_line2) else add_line2
        country = None if pd.isna(country) else country
        pincode = None if pd.isna(pincode) else pincode
        pan_no = None if pd.isna(pan_no) else pan_no
        aadhar_no = None if pd.isna(aadhar_no) else aadhar_no

        try:
            # Check if LLP Preacher already exists
            if frappe.db.exists("Donor Creation Request", id_no):                
                # Here to update old subseva type or add cost centers                
                if cost_cost_center:
                    old_doc = frappe.get_doc("Seva Subtype", seva_name)
                    # Append one row with both 'company' and 'cost_center' fields
                    old_doc.append("cost_centers", {
                        "company": company_cost_centers,
                        "cost_center": cost_cost_center
                    })
                    old_doc.save()
                    updated_count = updated_count + 1
                    #frappe.db.commit()
                    print(f"SevaSubType {seva_name} updated successfully.")
            else:
                #create new doc type
                new_sevasubtype = frappe.get_doc({
                    "doctype": "Seva Subtype",
                    "initial": seva_name, 
                    "enabled": enabled_flag,
                    "seva_name": seva_name,
                    "account": amount,
                    "old_parent": old_parent,
                    "parent_seva_subtype": parent_seva_type,
                    "is_group": is_group,
                    "patronship_allowed": patronship_flag,
                    "include_in_analysis": analysis_flag,
                    "priority": priority,
                    "cost_centers": []
                })

                if cost_cost_center:
                    # Append one row with both 'company' and 'cost_center' fields
                    new_sevasubtype.append("cost_centers", {
                        "company": company_cost_centers,
                        "cost_center": cost_cost_center
                    })

                new_sevasubtype.insert(ignore_permissions=True)
                added_count += 1 
                frappe.db.commit()
                print(f"SevaSubType {seva_name} added successfully.")
        
        except Exception as e:
            error += 1
            print(f"Error: {e}")
    print(f"SevaSubType added:{added_count}, updated:{updated_count}, Error: {error}, notseva {not_a_seva_sub_type}, skipped{skipped_count}, duplicate {duplicate_count} added successfully.")
