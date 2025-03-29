# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# bench --site test.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.vcmbudgetcreation.add_vcmbudget
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def add_vcmbudget():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/vcmbudget-1.xlsx"  # Change as needed

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"Company", "COST CENTRE", "BUDEGT HEAD", "LOCATION", "TOTAL"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return
    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    not_a_costcenter = 0
    not_a_budgethead = 0   
    added_count = 0 
    error  = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["COST CENTRE"]) or pd.isna(row["TOTAL"]):
            continue
        company_name = row.get("Company")
        cost_center = row.get("COST CENTRE")
        budget_head = row.get("BUDEGT HEAD")
        location = row.get("LOCATION")
        total = row.get("TOTAL")
        # preacher_email = row.get("User (Allowed Users)")
        # if not preacher_name:
        #         not_a_preacher += 1
        #         continue  # Skip rows without a name
        
        # Check if cost center exists 
        if not frappe.db.exists("Cost Center", cost_center):
            print(f"Error: Cost Center {cost_center} does not exist in the system.")
            not_a_costcenter += 1
            continue

        # Check if budget center exists 
        if not frappe.db.exists("Budget Head", budget_head):
            print(f"Error: Budget Head {budget_head} does not exist in the system.")
            not_a_budgethead += 1
            continue        
        try:
             # Check if the parent VCM Budget already exists for the Cost Center
            existing_budget = frappe.get_list("VCM Budget", filters={"company":  company_name, "cost_center": cost_center, "location": location}, fields=["name"])
            if existing_budget:
                # Fetch existing VCM Budget record
                budget_doc = frappe.get_doc("VCM Budget", existing_budget[0]["name"])

                # Check if the budget head already exists in the child table
                existing_child = next((item for item in budget_doc.budget_items if item.budget_head == budget_head), None)

                if existing_child:
                    # Update the existing budget head's amount
                    existing_child.amount = total
                    print(f"Updated Budget Head {budget_head} for Cost Center {cost_center}.")
                else:
                    # Append a new budget head entry
                    budget_doc.append("budget_items", {
                        "budget_head": budget_head,
                        "amount": total
                    })
                    print(f"Added Budget Head {budget_head} to Cost Center {cost_center}.")

                # Save the updated document
                budget_doc.save()
                frappe.db.commit()
                updated_count += 1

            else:
                # Create a new VCM Budget document with a child table
                new_budget = frappe.get_doc({
                    "doctype": "VCM Budget",
                    "company": company_name,
                    "cost_center": cost_center,
                    "location": location,
                    "fiscal_year": "25-26",  # Consider fetching dynamically
                    "budget_items": [{
                        "budget_head": budget_head,
                        "amount": total
                    }],
            
                })

                new_budget.insert(ignore_permissions=True)
                frappe.db.commit()
                added_count += 1
                print(f"Created new VCM Budget for Cost Center {cost_center}.")

        except Exception as e:
            print(f"Error processing {cost_center} - {budget_head}: {str(e)}")
            error += 1

    print(f"VCM Budget added: {added_count}, Updated: {updated_count}, Errors: {error}, Missing Cost Centers: {not_a_costcenter}, Missing Budget Heads: {not_a_budgethead}")