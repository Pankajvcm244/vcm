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
    update_JV_Budget,
)
from vcm.erpnext_vcm.doctype.vcm_budget.vcm_budget import is_pool_budget_head


def update_PO_AutoBudget():
    #Updated 4028, 0 PO.\n\n Errors: [].
    #"Updated 4086, 0 PO.\n\n Errors: []." 17/4/2025
    # Updated 4473, 0 PO.\n\n Errors: []." 25/4/2025
    #"Updated 4473, 0 PO.\n\n Errors: []."  2/5/2025 finalerp-5
    # "Updated 4555, 0 PO.\n\n Errors: []."  2/5/2025 finalerp-6
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/pankaj3.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/VCMBudget-finalerp-9.xlsx"
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/YFH-Noida.xlsx"
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
    #"Updated 4086, 0 PO.\n\n Errors: []." 17/4/2025
    # Updated 4473, 0 PI.\n\n Errors: []." 25/4/2025
    #"Updated 4473, 0 PI.\n\n Errors: []." 2/5/2025 finalerp-5
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/pankaj3.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/VCMBudget-finalerp-9.xlsx"
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/YFH-Noida.xlsx"
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
    return f"Updated {updated_count}, {skipped_count} PI.\n\n Errors: {errors}."

def update_PE_AutoBudget():
    #Updated 4028, 0 PO.\n\n Errors: [].    
    #Updated PE 4031, Skipped 0.\n\n Errors: []
    #"Updated PE 4086, Skipped 0.\n\n Errors: []."
    #"Updated PE 4086, Skipped 0.\n\n Errors: []." 17/4/2024
    #"Updated PE 4473, Skipped 0.\n\n Errors: []." 25/4/2025
    # "Updated PE 4473, Skipped 0.\n\n Errors: []."  2/5/2025 finalerp-5
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/pankaj3.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/VCMBudget-finalerp-9.xlsx"
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/YFH-Noida.xlsx"
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

def update_JV_AutoBudget():
    #Updated 4028, 0 PO.\n\n Errors: [].
    #"Updated JV 4031, Skipped 0.\n\n Errors: []."
    #"Updated JV 4086, Skipped 0.\n\n Errors: []." 17/4/2025
    # "Updated JV 4473, Skipped 0.\n\n Errors: []." 25/4/2025
    # "Updated JV 4473, Skipped 0.\n\n Errors: []." 2/5/2025 finalerp-5
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/pankaj3.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/VCMBudget-finalerp-9.xlsx"
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/YFH-Noida.xlsx"
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
            update_JV_Budget(company, location, fiscal_year, cost_center, budget_head)
            updated_count += 1
            #logging.error(f"****** update count :  {updated_count} ")

        except Exception as e:
            errors.append(f"Failed to update {company}, {location}, {cost_center}, {budget_head}, {fiscal_year}: {str(e)}")

    # Return script execution summary
    #return f"Updated {updated_count} invoices.\n\n Errors: {errors}, {len(errors)}."
    return f"Updated JV {updated_count}, Skipped {skipped_count}.\n\n Errors: {errors}."

def update_parent_manual_AutoBudget():
    # bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.BudgetAutoUpdate.update_parent_AutoBudget
    # Path to Excel file (Store this in your private files folder)
    #bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.BudgetAutoUpdate.update_parent_AutoBudget
    
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/VCMParentANNADANA-4.xlsx"
 
    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {
        "Total Amended Amount", "Pool Budget Total", "Total Used Amount", "Total Balance Amount",
        "Pool Used Amount", "Pool Balance Amount", "Purchase Order", "Unlinked Purchase Invoice",
        "Unlinked Payment Entry", "Journal Entry", "Used %"
        }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        frappe.throw(f"Missing required columns in the Excel file: {', '.join(missing_columns)}")

    #logging.debug(f"required columns are: {required_columns} ")
    updated_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        # Skip rows where essential values are missing
        if pd.isna(row["Pool Used Amount"]) or pd.isna(row["Purchase Order"]):
            skipped_count += 1
            continue

        pool_total = row["Pool Budget Total"]
        total_used = row["Total Used Amount"]
        total_balance = row["Total Balance Amount"]
        pool_used = row["Pool Used Amount"]
        pool_balance = row["Pool Balance Amount"]
        po_amount = row["Purchase Order"]
        pi_amount = row["Unlinked Purchase Invoice"]
        pe_amount = row["Unlinked Payment Entry"]
        jv_amount = row["Journal Entry"]
        used_per = row["Used %"]
        budget_name = row["ID"]


        #logging.debug(f"update-1 are: {company}, {location}, {cost_center}, {budget_head}, {fiscal_year} ")
        try:
            frappe.db.sql("""
                UPDATE `tabVCM Budget`
                SET total_used_amount = %s,
                    total_balance_amount = %s,
                    pool_budget_total = %s,
                    pool_budget_used = %s,
                    pool_budget_balance = %s,
                    total_unpaid_purchase_order = %s,
                    total_unpaid_purchase_invoice = %s,
                    total_paid_payment_entry = %s,
                    total_additional_je = %s,
                    used_percent = %s
                WHERE name = %s
            """, (total_used, total_balance, pool_total, pool_used, pool_balance, po_amount, pi_amount, pe_amount, jv_amount,used_per, budget_name))      
            frappe.db.commit()
            updated_count += 1
            #logging.error(f"****** update count :  {updated_count} ")

        except Exception as e:
            errors.append(f"Failed to update  {str(e)}")

    # Return script execution summary
    #return f"Updated {updated_count} invoices.\n\n Errors: {errors}, {len(errors)}."
    return f"Updated {updated_count}, {skipped_count} PO.\n\n Errors: {errors}."

def update_vcm_parent_AutoBudget():
        #bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.BudgetAutoUpdate.update_vcm_parent_AutoBudget
        budgets = frappe.get_all("VCM Budget", pluck="name")
        #name = "HKMV-2025-2026-VRN-YOGA FOR HAPPINESS - HKMV"
        for name in budgets:
            update_vcm_budget_totals(name)
        #Budget: %:87.72692063492063, T: 315000.0, A: 0, TB: 38660.2, TU276339.8, PO: 231924.8, PI: 23940.0, PE: 20475.0, JE: 0, 
        # PB: 315000.0, PU: 276339.8, PBL: 38660.2
        

def update_vcm_budget_totals(budget_name):
    doc = frappe.get_doc("VCM Budget", budget_name)
    total_po = 0
    total_pi = 0
    total_pe = 0
    total_je = 0
    total_amount = 0
    total_used = 0
    total_balance = 0
    total_budget = 0
    total_amended = 0
    total_pool_budget = 0
    total_pool_used = 0
    total_pool_balance = 0
    total_used_percent = 0

    for row in doc.budget_items:
        total_po += row.unpaid_purchase_order or 0
        total_pi += row.unpaid_purchase_invoice or 0
        total_pe += row.paid_payment_entry or 0
        total_je += row.additional_je or 0  

        total_budget += row.original_amount or 0
        total_amended += row.amended_till_now or 0
        total_amount += row.original_amount or 0
        total_balance += row.balance_budget or 0
        total_used += row.used_budget or 0

        if is_pool_budget_head(row.budget_head):
            total_pool_budget += row.current_budget or 0
            total_pool_used += row.used_budget or 0
            total_pool_balance += row.balance_budget or 0         
    
    #percent is for total parent not childwise
    percent = (total_used/ (total_amount + total_amended )) * 100;  
    total_used_percent = percent or 0
    logging.debug(f"Budget {budget_name}, Budget: %:{total_used_percent}, T: {total_amount}, Amend: {total_amended}, TB: {total_balance}, TU: {total_used}, PO: {total_po}, PI: {total_pi}, PE: {total_pe}, JE: {total_je}, PT: {total_pool_budget}, PU: {total_pool_used}, PBL: {total_pool_balance} ")
    doc.db_set("total_unpaid_purchase_order", total_po)
    doc.db_set("total_unpaid_purchase_invoice", total_pi)
    doc.db_set("total_paid_payment_entry", total_pe)
    doc.db_set("total_additional_je", total_je)

    doc.db_set("total_amount", total_amount)
    doc.db_set("total_amended_amount", total_amended)
    doc.db_set("used_percent", total_used_percent)
    doc.db_set("total_balance_amount", total_balance)
    doc.db_set("total_used_amount", total_used)
  
    doc.db_set("pool_budget_total", total_pool_budget)
    doc.db_set("pool_budget_used", total_pool_used)
    doc.db_set("pool_budget_balance", total_pool_balance) 

    #frappe.msgprint(f"Totals updated for {budget_name}")