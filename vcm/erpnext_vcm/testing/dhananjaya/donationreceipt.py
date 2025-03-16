# created by Pankaj on 1st Feb 2025 to update cost venter based upon SINV number
# script apps/vcm/vcm/erpnext_vcm/testing/SINVcommand-1.log
# bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.dhananjaya.donationreceipt.add_donationreceipt
# # exit

import frappe
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

def add_donationreceipt():
    # Path to Excel file (Store this in your private files folder)
    #file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/CostCentresCorrectionPooja.xlsx"  # Change as needed
    file_path = "/home/ubuntu/frappe-bench/apps/vcm/vcm/erpnext_vcm/testing/excelfiles/donationreceipt-try-1.xlsx"  # Change as needed

    # Ensure file exists
    if not os.path.exists(file_path):
        frappe.throw("Excel file not found. Please upload the correct file.")
        return

    # Read Excel File
    df = pd.read_excel(file_path)

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Validate columns
    required_columns = {"ID", "Workflow State", "Receipt Date","Donor"}
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
        # Skip rows where essential value donor name is missing
        if pd.isna(row["Donor"] ):
            skipped_count += 1
            continue
              
        id_no = row.get("ID")
        workflow_state = row.get("Workflow State")
        company = row.get("Company") 
        rec_date = row.get("Receipt Date")
        preacher = row.get("Preacher")
        donor = row.get("Donor")        
        full_name = row.get("Full Name")
        patron = row.get("Patron")
        patron_name = row.get("Patron Name")
        in_the_name = row.get("In the name of")
        mobile = row.get("Contact No.")
        email = row.get("Email")  
        address = row.get("Address")
        paymnet_method = row.get("Payment Method") 
        amount = row.get("Amount")
        payment_gateway_doc = row.get("Payment Gateway Document")        
        add_charges = row.get("Additional Charges")
        reference = row.get("Reference No.")
        tranx_remark = row.get("Transaction Remarks")
        payment_screen = row.get("Payment Screenshot")
        print_remark_on_recipt = row.get("Print Remarks On Receipt")
        seva_type = row.get("Seva Type")  
        g80_req = row.get("80G Required")
        seva_subtype = row.get("Seva Subtype") 
        yatra_req = row.get("Yatra Registration")
        is_ecs = row.get("Is ECS")
        ecs_trnx_id = row.get("ECS Transaction ID")
        ecs_rej_reason = row.get("ECS Rejection Reason")
        auto_generated = row.get("Auto Generated")
        is_csr = row.get("Is CSR")
        usr_rem = row.get("User Remarks")
        chq_no = row.get("Cheque Number")
        chq_date = row.get("Cheque Date")
        ifsc_code = row.get("IFSC Code")
        chq_bank_name = row.get("Cheque Bank Name")
        chq_branch = row.get("Cheque Branch")
        amend_from = row.get("Amended From")
        bank_acc = row.get("Bank Account")
        bank_trx = row.get("Bank Transaction")
        bank_trx_desc = row.get("Bank Transaction Description")
        gateway_exp_acc = row.get("Gateway Expense Account")


        cash_rec_date = row.get("Cash Received Date")
        cost_center = row.get("Cost Center")
        don_amount = row.get("Donation Account")
        cash_acc = row.get("Cash Account")
        tds_acc = row.get("TDS Account")
        don_creat_req = row.get("Donor Creation Request")
        don_crea_req_name = row.get("Donor Creation Request Name")
        old_dr_no = row.get("Old DR No")
        old_re_date = row.get("Old Receipt Date")
        
        if not id_no:
            not_a_req_type += 1
            continue  # Skip rows without a name        
        
        # Handle NaN values by replacing them with None        
        preacher = None if pd.isna(preacher) else preacher
        donor = None if pd.isna(donor) else donor
        full_name = None if pd.isna(full_name) else full_name
        patron = None if pd.isna(patron) else patron
        patron_name = None if pd.isna(patron_name) else patron_name
        in_the_name = None if pd.isna(in_the_name) else in_the_name
        mobile = None if pd.isna(mobile) else mobile
        email = None if pd.isna(email) else email
        address = None if pd.isna(address) else address
        paymnet_method = None if pd.isna(paymnet_method) else paymnet_method
        payment_gateway_doc = None if pd.isna(payment_gateway_doc) else payment_gateway_doc
        add_charges = None if pd.isna(add_charges) else add_charges
        reference = None if pd.isna(reference) else reference
        tranx_remark = None if pd.isna(tranx_remark) else tranx_remark
        payment_screen = None if pd.isna(payment_screen) else payment_screen
        print_remark_on_recipt = None if pd.isna(print_remark_on_recipt) else print_remark_on_recipt
        seva_type = None if pd.isna(seva_type) else seva_type
        g80_req = None if pd.isna(g80_req) else g80_req
        seva_subtype = None if pd.isna(seva_subtype) else seva_subtype
        yatra_req = None if pd.isna(yatra_req) else yatra_req
        is_ecs = None if pd.isna(is_ecs) else is_ecs
        ecs_trnx_id = None if pd.isna(ecs_trnx_id) else ecs_trnx_id
        ecs_rej_reason = None if pd.isna(ecs_rej_reason) else ecs_rej_reason
        auto_generated = None if pd.isna(auto_generated) else auto_generated
        is_csr = None if pd.isna(is_csr) else is_csr
        usr_rem = None if pd.isna(usr_rem) else usr_rem
        chq_no = None if pd.isna(chq_no) else chq_no
        chq_date = None if pd.isna(chq_date) else chq_date
        ifsc_code = None if pd.isna(ifsc_code) else ifsc_code
        chq_bank_name = None if pd.isna(chq_bank_name) else chq_bank_name
        chq_branch = None if pd.isna(chq_branch) else chq_branch
        amend_from = None if pd.isna(amend_from) else amend_from
        bank_acc = None if pd.isna(bank_acc) else bank_acc
        bank_trx = None if pd.isna(bank_trx) else bank_trx
        bank_trx_desc = None if pd.isna(bank_trx_desc) else bank_trx_desc
        cash_rec_date = None if pd.isna(cash_rec_date) else cash_rec_date
        cost_center = None if pd.isna(cost_center) else cost_center
        cash_acc = None if pd.isna(cash_acc) else cash_acc
        tds_acc = None if pd.isna(tds_acc) else tds_acc
        don_creat_req = None if pd.isna(don_creat_req) else don_creat_req
        don_crea_req_name = None if pd.isna(don_crea_req_name) else don_crea_req_name
        old_dr_no = None if pd.isna(old_dr_no) else old_dr_no
        old_re_date = None if pd.isna(old_re_date) else old_re_date
        gateway_exp_acc = None if pd.isna(gateway_exp_acc) else gateway_exp_acc

        try:
            # Check if LLP Preacher already exists
            if frappe.db.exists("Donation Receipt", id_no): 
                    duplicate_count += 1
                    print(f"Error: Donation Receipt {id_no} already exists.")
            else:
                #create new doc type
                #"name": id_no,  # Explicitly setting the name
                initial_stage = "Draft"
                donrcreation_request = frappe.get_doc({
                    "doctype": "Donation Receipt",
                    "workflow_state": initial_stage,
                    "initial": id_no,
                    "name": id_no, 
                    "company": company,
                    "receipt_date": rec_date,
                    "preacher": preacher,
                    "donor": donor,
                    "full_name": full_name,
                    "patron": patron,
                    "patron_name": patron_name,
                    "sevak_name": in_the_name,
                    "contact": mobile,
                    "email": email,
                    "address": address,
                    "payment_method": paymnet_method,
                    "amount": amount,
                    "payment_gateway_document": payment_gateway_doc,
                    "additional_charges": add_charges,
                    "reference_no": reference,
                    "remarks": tranx_remark,
                    "print_remarks_on_receipt": print_remark_on_recipt,
                    "seva_type": seva_type,
                    "atg_required": g80_req,
                    "seva_subtype": seva_subtype,
                    "yatra_registration": yatra_req,
                    "is_ecs": is_ecs,
                    "ecs_transaction_id": ecs_trnx_id,
                    "ecs_rejection_reason": ecs_rej_reason,
                    "auto_generated": auto_generated,
                    "is_csr": is_csr,
                    "user_remarks": usr_rem,
                    "cheque_number": chq_no,
                    "cheque_date": chq_date,
                    "ifsc_code": ifsc_code,
                    "bank_name": chq_bank_name,
                    "cheque_branch": chq_branch,
                    "amended_from": amend_from,
                    "bank_account": bank_acc,
                    "bank_transaction": bank_trx,
                    "bank_transaction_description": bank_trx_desc,
                    "donation_account":don_amount,
                    "cash_account": cash_acc ,
                    "tds_account": tds_acc,
                    "gateway_expense_account": gateway_exp_acc,
                    "cash_received_date": cash_rec_date,
                    "cost_center": cost_center,
                    "donor_creation_request": don_creat_req,
                    "donor_creation_request_name": don_crea_req_name,
                    "old_dr_no": old_dr_no,                    
                    "old_receipt_date": old_re_date, 
                })
                donrcreation_request.name = id_no

                donrcreation_request.insert(ignore_permissions=True)
                
                #if status == "Closed" :
                   # submitted_count += 1
                    #donrcreation_request.set_status_closed()  # This submits the document
                    #donrcreation_request.db_set("status", "Closed", commit=True)
                    #donrcreation_request.submit()  # Submitting the document
                    # dwe have changed class for "Open" to "Closed" change it to Open after migration
                    # on_submit(self):
                    #    self.db_set("status", "Closed", commit=True)
                    #frappe.db.commit()
                    #print(f"donrcreation_request {id_no} submitted successfully.")
                #else:
                    #donrcreation_request.set_status_open()  # This keeps the document Open
                    #donrcreation_request.set_status_open()
                #frappe.db.commit()
                added_count += 1

                # Fetch the existing document
                donation_receipt = frappe.get_doc("Donation Receipt", id_no)
                print(f"****donation receipt state -1 {donation_receipt.workflow_state}, submitted: {workflow_state}")
                # Update the workflow state
                donation_receipt.workflow_state = workflow_state
                print(f"****donation receipt state -2 {donation_receipt.workflow_state}, submitted: {workflow_state}")
                #donation_receipt.name = id_no
                donation_receipt.save()
                frappe.db.commit()
                    #print(f"donrcreation_request {id_no} added successfully.")
        
        except Exception as e:
            error += 1
            print(f"Error: {e}")
    print(f"****donation receipt Open:{added_count}, submitted: {submitted_count}, already exists:{duplicate_count}, Error: {error}, Name missing{skipped_count}, ID missing {not_a_req_type} added successfully.")
