# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/JVcommand-1.log
# bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.BudgetAutoUpdate.update_PE_AutoBudget
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)
from vcm.erpnext_vcm.testing.Misc.VCMBudgetTrigger import (
    update_PO_Budget_new,
    update_PI_Budget,
    update_PE_Budget,
)

def update_PO_AutoBudget():
    #Updated 4028, 0 PO.\n\n Errors: [].
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/pankaj3.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/VCMBudget-finalerp-1.xlsx"
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/FUNDRAISING.xlsx"
    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"Company", "LOCATION", "COST CENTRE", "BUDGET HEAD", "Fiscal Year"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["COST CENTRE"]) or pd.isna(row["BUDGET HEAD"]):
            skipped_count += 1
            continue

        company = row["Company"]
        location = row["LOCATION"]
        cost_center = row["COST CENTRE"]
        budget_head = row["BUDGET HEAD"]
        fiscal_year = row["Fiscal Year"]
        #logging.debug(f"update-1 are: {company}, {location}, {cost_center}, {budget_head}, {fiscal_year} ")
        try:
            # Fetch Sales Invoice
            update_PO_Budget_new(company, location, fiscal_year, cost_center, budget_head)
            updated_count += 1
            #logging.error(f"****** update count :  {updated_count} ")

        except Exception as e:
            errors.append(f"Failed to update {company}, {location}, {cost_center}, {budget_head}, {fiscal_year}: {str(e)}")

    # Return script execution summary
    #return f"Updated {updated_count} invoices.\n\n Errors: {errors}, {len(errors)}."
    return f"Updated {updated_count}, {skipped_count} PO.\n\n Errors: {errors}."

def update_PI_AutoBudget():
    #Updated 4028, 0 PO.\n\n Errors: [].
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/pankaj3.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/VCMBudget-finalerp-1.xlsx"
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/FUNDRAISING.xlsx"
    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"Company", "LOCATION", "COST CENTRE", "BUDGET HEAD", "Fiscal Year"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["COST CENTRE"]) or pd.isna(row["BUDGET HEAD"]):
            skipped_count += 1
            continue

        company = row["Company"]
        location = row["LOCATION"]
        cost_center = row["COST CENTRE"]
        budget_head = row["BUDGET HEAD"]
        fiscal_year = row["Fiscal Year"]
        #logging.debug(f"update-1 are: {company}, {location}, {cost_center}, {budget_head}, {fiscal_year} ")
        try:
            # Fetch Sales Invoice
            update_PI_Budget(company, location, fiscal_year, cost_center, budget_head)
            updated_count += 1
            #logging.error(f"****** update count :  {updated_count} ")

        except Exception as e:
            errors.append(f"Failed to update {company}, {location}, {cost_center}, {budget_head}, {fiscal_year}: {str(e)}")

    # Return script execution summary
    #return f"Updated {updated_count} invoices.\n\n Errors: {errors}, {len(errors)}."
    return f"Updated {updated_count}, {skipped_count} PO.\n\n Errors: {errors}."

def update_PE_AutoBudget():
    #Updated 4028, 0 PO.\n\n Errors: [].
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/pankaj3.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/VCMBudget-finalerp-2.xlsx"
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/FUNDRAISING.xlsx"
    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"Company", "LOCATION", "COST CENTRE", "BUDGET HEAD", "Fiscal Year"}
    if not required_columns.issubset(df.columns):
        frappe.throw("Missing required columns in the Excel file.")
        return

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["COST CENTRE"]) or pd.isna(row["BUDGET HEAD"]):
            skipped_count += 1
            continue

        company = row["Company"]
        location = row["LOCATION"]
        cost_center = row["COST CENTRE"]
        budget_head = row["BUDGET HEAD"]
        fiscal_year = row["Fiscal Year"]
        #logging.debug(f"update-1 are: {company}, {location}, {cost_center}, {budget_head}, {fiscal_year} ")
        try:
            # Fetch Sales Invoice
            update_PE_Budget(company, location, fiscal_year, cost_center, budget_head)
            updated_count += 1
            #logging.error(f"****** update count :  {updated_count} ")

        except Exception as e:
            errors.append(f"Failed to update {company}, {location}, {cost_center}, {budget_head}, {fiscal_year}: {str(e)}")

    # Return script execution summary
    #return f"Updated {updated_count} invoices.\n\n Errors: {errors}, {len(errors)}."
    return f"Updated PE {updated_count}, Skipped {skipped_count}.\n\n Errors: {errors}."