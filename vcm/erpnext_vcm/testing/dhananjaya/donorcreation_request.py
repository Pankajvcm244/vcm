# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.dhananjaya.donorcreation_request.donor_creation_request
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def donor_creation_request():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/donor_creation_request-final-1.xlsx"  # Change as needed

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
    added_count = 0
    error  = 0
    skipped_count = 0
    duplicate_count  = 0
    not_a_req_type = 0
    submitted_count = 0

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["Full Name"] ):
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
                    duplicate_count += 1
                    print(f"Error: Donor Creation Request {id_no} already exists.")
            else:
                #create new doc type
                #"name": id_no,  # Explicitly setting the name
                donrcreation_request = frappe.get_doc({
                    "doctype": "Donor Creation Request",
                    "initial": id_no,
                    "name": id_no, 
                    "status": status,
                    "full_name": fullname,
                    "llp_preacher": llp_preacher,
                    "email": email,
                    "contact_number": contact_number,
                    "address_type": address_type,
                    "address_line_1": add_line1,
                    "address_line_2": add_line2,
                    "city": city,
                    "state": state,
                    "country": country,
                    "pin_code": pincode,
                    "pan_number": pan_no,
                    "aadhar_number": aadhar_no
                })
                donrcreation_request.insert(ignore_permissions=True)
                
                if status == "Closed" :
                    submitted_count += 1
                    #donrcreation_request.set_status_closed()  # This submits the document
                    #donrcreation_request.db_set("status", "Closed", commit=True)
                    donrcreation_request.submit()  # Submitting the document
                    # dwe have changed class for "Open" to "Closed" change it to Open after migration
                    # on_submit(self):
                    #    self.db_set("status", "Closed", commit=True)
                    frappe.db.commit()
                    #print(f"donrcreation_request {id_no} submitted successfully.")
                else:
                    #donrcreation_request.set_status_open()  # This keeps the document Open
                    donrcreation_request.set_status_open()
                    frappe.db.commit()
                    added_count += 1
                    #print(f"donrcreation_request {id_no} added successfully.")
        
        except Exception as e:
            error += 1
            print(f"Error: {e}")
    print(f"****donrcreation Open:{added_count}, submitted: {submitted_count}, already exists:{duplicate_count}, Error: {error}, Name missing{skipped_count}, ID missing {not_a_req_type} added successfully.")
