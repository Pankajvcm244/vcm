# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.sevasubtype.add_sevasubtype
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def add_sevasubtype():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/sevasubtype-test1.xlsx"  # Change as needed

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"Company (Cost Centers)", "Seva Name", "Enabled","Include in Analysis"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    not_a_seva_sub_type = 0
    error  = 0
    skipped_count = 0
    duplicate_count  = 0

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["Seva Name"] ):
            skipped_count += 1
            continue
              
        seva_name = row.get("Seva Name")
        priority = row.get("Priority")
        enabled_flag = row.get("Enabled") 
        amount = row.get("Amount")
        old_parent = row.get("Old Parent")
        parent_seva_type = row.get("Parent Seva Subtype")        
        is_group = row.get("Is Group")
        patronship_flag = row.get("Patronship Allowed")
        analysis_flag = row.get("Include in Analysis")
        is_a_yatra = row.get("Is a Yatra")
        from_date = row.get("From Date")
        to_date = row.get("To Date")  
        company_cost_centers = row.get("Company (Cost Centers)")
        cost_cost_center = row.get("Cost Center (Cost Centers)")      
        
        if not seva_name:
                not_a_seva_sub_type += 1
                continue  # Skip rows without a name        
        
        # Handle NaN values by replacing them with None        
        old_parent = None if pd.isna(old_parent) else old_parent
        parent_seva_type = None if pd.isna(parent_seva_type) else parent_seva_type
        from_date = None if pd.isna(from_date) else from_date
        to_date = None if pd.isna(to_date) else to_date
        company_cost_centers = None if pd.isna(company_cost_centers) else company_cost_centers
        cost_cost_center = None if pd.isna(cost_cost_center) else cost_cost_center

        

        
        try:
            # Check if LLP Preacher already exists
            if frappe.db.exists("Seva Subtype", seva_name):                
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
                updated_count = updated_count + 1
                frappe.db.commit()
                print(f"SevaSubType {seva_name} added successfully.")
        
        except Exception as e:
            error += 1
            print(f"Error: {e}")
    print(f"SevaSubType updated:{updated_count}, Error: {error}, notseva {not_a_seva_sub_type} , duplicate {duplicate_count} added successfully.")
