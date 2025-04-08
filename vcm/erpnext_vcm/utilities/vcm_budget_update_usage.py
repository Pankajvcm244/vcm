import frappe
from frappe.utils import flt
import logging
logging.basicConfig(level=logging.DEBUG)

@frappe.whitelist()
def validate_vcm_po_budget_amount_budgethead(po_doc):    
    """ Updates the used budget in VCM Budget when a PO is submitted """
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")    
    # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {"company": po_doc.company,"location":po_doc.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":po_doc.cost_center,"docstatus":1},
        "name")
    #logging.debug(f"in validate_vcm_po_ 2 {budget_name}")
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no budget for this cost center then throw error as Budget is enabled for this cost cenetr
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        frappe.throw(f"Budget not available for Cost Center:{po_doc.company}, but enabled in Cost Center.  {po_doc.cost_center}, {vcm_budget_settings.financial_year},  Location:{po_doc.location}")
        return False    
    budget_validation_flag = True 
    if po_doc.budget_head == "Salaries & Wages":        
        frappe.throw(f"{po_doc.budget_head} Budget Head can not be used in PO , Request: {po_doc.rounded_total}")
        #logging.debug(f"validate_vcm_po_budget_amount_budgethead budget exceeded return false")
        return False
    elif po_doc.budget_head == "Fixed Assets": 
        for budget_item in budget_doc.get("budget_items") or []:
            #logging.debug(f"in validate_vcm_po_budget_amount_budgethead 2 {po_doc.budget_head}, {budget_item.balance_budget},{po_doc.rounded_total}")
            if budget_item.budget_head == po_doc.budget_head:
                budget_validation_flag = False
                if po_doc.rounded_total > budget_item.balance_budget:
                    frappe.throw(f"Budget Exceeded for {po_doc.budget_head}, Balance: {budget_item.balance_budget}, Request: {po_doc.rounded_total}")
                    #logging.debug(f"validate_vcm_po_budget_amount_budgethead budget exceeded return false")
                    return False
    else:
        #for budget_item in budget_doc.get("budget_items") or []:
            #logging.debug(f"in validate_vcm_po_budget_amount_budgethead 2 {po_doc.budget_head}, {budget_doc.pool_budget_balance},{po_doc.rounded_total} ")
            #if budget_item.budget_head == po_doc.budget_head:
        # Now user can select any budget head and we will allow it if pool has money
        budget_validation_flag = False
        if po_doc.rounded_total > budget_doc.pool_budget_balance:
            frappe.throw(f"Pool Budget Exceeded for {po_doc.budget_head}, Balance: {budget_doc.pool_budget_balance}, Request: {po_doc.rounded_total}")
            #logging.debug(f"validate_vcm_po_budget_amount_budgethead budget exceeded return false")
            return False

    if budget_validation_flag:
        frappe.throw(f"PO Budget not found for Cost Center: {po_doc.cost_center}, Budget Head: {po_doc.budget_head}")
        return False        
    return True

@frappe.whitelist()
def update_vcm_po_budget_usage(po_doc):
#def test_func():
# bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.utilities.vcm_budget_update_usage.update_vcm_po_budget_usage    
    filters = {}    
    conditions = ["docstatus = 1"]  # Only consider approved POs
    """ Updates the used budget in VCM Budget when a PO is submitted """
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {"company": po_doc.company,"location":po_doc.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":po_doc.cost_center,"docstatus":1},
        "name")
   
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no budget for this cost center then just move on
        logging.debug(f"in validate_vcm_po No budget exists 3 {budget_name}")
        return 0 
    filters = {
        "cost_center": po_doc.cost_center,
        "company": po_doc.company,
        "location": po_doc.location,
        "budget_head": po_doc.budget_head,
        "from_date": "2024-04-01",  # Always check from April 1st
    }
    #logging.debug(f"in update_vcm_po_budget_usage 2 {po_doc.cost_center}, {po_doc.company},{po_doc.location} , {po_doc.budget_head}")
    date_field = "transaction_date"
    if filters["cost_center"]:
        conditions.append("cost_center = %(cost_center)s")
    if filters["company"]:
        conditions.append("company = %(company)s")
    if filters["location"]:
        conditions.append("location = %(location)s")
    if filters["budget_head"]:
        conditions.append("budget_head = %(budget_head)s")
    
    # Check all POs from April 1st onward
    conditions.append(f"{date_field} >= %(from_date)s")
    selected_table = "tab" + "Purchase Order"
    amount_field = "grand_total"

    condition_string = " AND ".join(conditions)
    total_used_budget = 0
    query = f"""
        SELECT
            SUM({amount_field}) AS total_used_budget
        FROM `{selected_table}`
        WHERE {condition_string}
    """

    result = frappe.db.sql(query, filters, as_dict=True)
    logging.debug(f"in get po 2 {result} {total_used_budget}")
    total_po_amount = result[0].get("total_used_budget", 0) if result else 0
    #budget_updated_flag = True
    for budget_item in budget_doc.get("budget_items") or []:
        #logging.debug(f"in update_vcm_po_budget_usage 2 {po_doc.budget_head}")
        if budget_item.budget_head == po_doc.budget_head:        
            budget_item.unpaid_purchase_order = total_po_amount  # Adjust Remaining Budget
            budget_item.used_budget = (
                    (budget_item.paid_payment_entry or 0)
                    + (budget_item.unpaid_purchase_invoice or 0)
                    + (budget_item.unpaid_purchase_order or 0)
                    + (budget_item.additional_je or 0)
            )           
            budget_item.balance_budget = (
                    (budget_item.current_budget or 0)
                  - (budget_item.used_budget or 0)
            )
            break    
    # Save and commit changes    
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()    
    return True

@frappe.whitelist()
def validate_vcm_pi_budget_amount(pi_doc):    
    PI_FLAG_WITH_PO = False
    budget_validation_flag = True
    for item in pi_doc.items:
        #logging.debug(f"in Purchase InvoiceDOc Ref: {item}, {item.purchase_order} ")
        if item.purchase_order:
            PI_FLAG_WITH_PO = True
            break  # Exit loop as soon as we find a linked PO  

    #logging.debug(f"in update_vcm_pi_budget_usage 1 {pi_doc}")
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {"company": pi_doc.company,"location":pi_doc.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":pi_doc.cost_center,"docstatus":1},
        "name")
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        frappe.throw(f"Budget not available for Cost Center:{pi_doc.cost_center}, but enabled in Cost Center. Location:{pi_doc.location}, Budget Head:{pi_doc.budget_head}")
        return True 
    budget_updated_flag = True
    total_vcm_advance = 0.0  # Initialize advance amount
    # Check if advances exist
    if pi_doc.advances:
        for advance in pi_doc.advances:
            total_vcm_advance += flt(advance.allocated_amount)  # Sum allocated advances
    #logging.debug(f"in Purchase Invoice Advance: {pi_doc.allocate_advances_automatically}, {total_vcm_advance} ")
    tax_deducted = 0.0  # Initialize advance amount
    if pi_doc.taxes_and_charges_deducted:
        tax_deducted = pi_doc.taxes_and_charges_deducted

    if pi_doc.budget_head == "Salaries & Wages":        
        frappe.throw(f"{pi_doc.budget_head} Budget Head can not be used in Payment Invoice , Request: {pi_doc.rounded_total}")
        #logging.debug(f"validate_vcm_po_budget_amount_budgethead budget exceeded return false")
        return False
    elif pi_doc.budget_head == "Fixed Assets": 
        for budget_item in budget_doc.get("budget_items") or []:
            #logging.debug(f"in validate_vcm_po_budget_amount_budgethead 2 {po_doc.budget_head}, {budget_item.balance_budget},{po_doc.rounded_total}")
            if budget_item.budget_head == pi_doc.budget_head:
                budget_validation_flag = False
                if pi_doc.rounded_total > budget_item.balance_budget:
                    frappe.throw(f"Budget Exceeded for {pi_doc.budget_head}, Balance: {budget_item.balance_budget}, Request: {pi_doc.rounded_total}")
                    #logging.debug(f"validate_vcm_po_budget_amount_budgethead budget exceeded return false")
                    return False
    else:
        # Now user can select any budget head and we will allow it if pool has money
        budget_validation_flag = False
        if PI_FLAG_WITH_PO: 
                    # Do nothing, Budget has been consumed in PO
                    a = 0                    
    #                 #logging.debug(f"PI With PO , {pi_doc.budget_head},{tax_deducted},{budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total}")  
        else:
            if (pi_doc.rounded_total - total_vcm_advance + tax_deducted ) > budget_doc.pool_budget_balance:
                frappe.throw(f"Pool Budget Exceeded for PI {pi_doc.budget_head}, Balance: {budget_doc.pool_budget_balance}, Request: {pi_doc.rounded_total}")
                #logging.debug(f"validate_vcm_po_budget_amount_budgethead budget exceeded return false")
                return False

    if budget_validation_flag:
        frappe.throw(f"PI Budget not found for Budget Head: {pi_doc.budget_head}")
        return False        
    return True

@frappe.whitelist()
def update_vcm_pi_budget_usage(pi_doc):
    """
    Updates the used budget in VCM Budget when a Purchase Invoice without a PO is submitted.
    """
    filters = {}   
    alias = "pi_doc" 
    conditions = [
        f"{alias}.docstatus = 1", 
        f"{alias}.is_return = 0", 
        "(pii.purchase_order IS NULL OR pii.purchase_order = '')"
        ]  # Approved PIs without PO
    

    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")

    # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {
            "company": pi_doc.company,
            "location": pi_doc.location,
            "fiscal_year": vcm_budget_settings.financial_year,
            "cost_center": pi_doc.cost_center,
            "docstatus": 1
        },
        "name"
    )

    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        # If there is no budget for this cost center then just move on
        logging.debug(f"in update_vcm_pi_budget_usage: No budget exists for {budget_name}")
        return 0 

    filters = {
        "cost_center": pi_doc.cost_center,
        "company": pi_doc.company,
        "location": pi_doc.location,
        "budget_head": pi_doc.budget_head,
        "from_date": "2024-04-01",  # Always check from April 1st
    }

    date_field = "posting_date"
    if filters.get("cost_center"):
        conditions.append(f"{alias}.cost_center = %(cost_center)s")
    if filters.get("company"):
        conditions.append(f"{alias}.company = %(company)s")
    if filters.get("location"):
        conditions.append(f"{alias}.location = %(location)s")
    if filters.get("budget_head"):
        conditions.append(f"{alias}.budget_head = %(budget_head)s")

    # Check all PIs from April 1st onward
    conditions.append(f"{alias}.{date_field} >= %(from_date)s")

    selected_table = "tabPurchase Invoice"
    amount_field = "grand_total"

    condition_string = " AND ".join(conditions)
    logging.debug(f"in update_vcm_pi_budget 1 {condition_string}")
    query = f"""
        SELECT
            SUM({amount_field}) AS total_used_budget
        FROM `{selected_table}` {alias}
        LEFT JOIN `tabPurchase Invoice Item` pii ON pii.parent = {alias}.name
        WHERE {condition_string}
    """

    result = frappe.db.sql(query, filters, as_dict=True)
    logging.debug(f"in get pi usage: {result}")
    total_pi_amount = result[0].get("total_used_budget", 0) if result else 0
    logging.debug(f"in update_vcm_pi_budget 2 {total_pi_amount}")

    for budget_item in budget_doc.get("budget_items") or []:
        if budget_item.budget_head == pi_doc.budget_head:        
            budget_item.unpaid_purchase_invoice = total_pi_amount  # Adjust Remaining Budget
            budget_item.used_budget = (
                (budget_item.paid_payment_entry or 0)
                + (budget_item.unpaid_purchase_invoice or 0)
                + (budget_item.unpaid_purchase_order or 0)
                + (budget_item.additional_je or 0)
            )
            budget_item.balance_budget = (
                (budget_item.current_budget or 0)
                - (budget_item.used_budget or 0)
            )
            break    

    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()    
    return True



@frappe.whitelist()
def validate_vcm_budget_on_payment_entry(pe_doc):
    return False
    """Update budget used when a Payment Entry is submitted."""
    # Ensure this is a Payment Entry affecting budget (Outgoing Payment)
    if pe_doc.payment_type not in ["Pay", "Receive"]:
        return False
    # Fetch related Purchase Invoice
    PAYMENT_FLAG_WITH_PI = False
    PAYMENT_FLAG_WITH_PO = False    
    # Iterate through the references table to check for Purchase Order or Purchase Invoice
    for reference in pe_doc.references:
        #logging.debug(f" in Payment Entry DOc Ref: {reference.reference_doctype} {reference.reference_name}")
        if reference.reference_doctype == "Purchase Order":
           PAYMENT_FLAG_WITH_PO = True
        elif reference.reference_doctype == "Purchase Invoice":
            PAYMENT_FLAG_WITH_PI = True
            
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
   # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {"company": pe_doc.company,"location":pe_doc.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":pe_doc.cost_center,"docstatus":1},
        "name")
    # Fetch budget settings based on Cost Center or Project
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        frappe.throw(f"Budget not available for Cost Center:{pe_doc.cost_center}, Location:{pe_doc.location}, Budget Head:{pe_doc.budget_head}")
        return True 
    # Calculate the paid amount impacting budget
    total_vcm_paid_amount = flt(pe_doc.paid_amount)
    #If budget doc is vaailable then we must update budget
    budget_updated_flag = True  
    for budget_item in budget_doc.get("budget_items") or []:
            if budget_item.budget_head == pe_doc.budget_head:
                budget_updated_flag = False
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                # In reeive dont check amount limit
                if pe_doc.payment_type != "Receive":
                    if PAYMENT_FLAG_WITH_PI: 
                        #logging.debug(f"in update_vcm_pE_budget_usage 3 {total_vcm_paid_amount},{budget_item.paid_payment_entry}")
                        if total_vcm_paid_amount > budget_item.unpaid_purchase_invoice:
                            frappe.throw(f"Unpaid Purchase Invoice is not available {pe_doc.budget_head}, Balance: {budget_item.unpaid_purchase_invoice}, Request: {total_vcm_paid_amount}")
                            return False  
                    elif PAYMENT_FLAG_WITH_PO:
                        #logging.debug(f"in update_vcm_pe_budget_usage 3 {total_vcm_paid_amount},{budget_item.paid_payment_entry}")
                        if total_vcm_paid_amount > budget_item.unpaid_purchase_order:
                            frappe.throw(f"Unpaid Purchase Order is not available {pe_doc.budget_head}, Balance: {budget_item.unpaid_purchase_order}, Request: {total_vcm_paid_amount}")
                            return False
                    else:
                        #reduce and check budget for PI without PO
                        if total_vcm_paid_amount > budget_item.balance_budget:
                            frappe.throw(f"Budget Exceeded for {pe_doc.budget_head}, Balance: {budget_item.balance_budget}, Request: {total_vcm_paid_amount}")
                            return False                    
                            #logging.debug(f"update_vcm_ w/O PI pi_budget_usage6, {budget_updated_flag}{budget_item.budget_head},{total_vcm_paid_amount}")           
                        break     
    if budget_updated_flag:
        frappe.throw(f"PE Budget not found for Budget Head:{pe_doc.budget_head} {budget_updated_flag},{budget_item.budget_head}")
        return False
    return True

@frappe.whitelist()    
def update_vcm_budget_on_payment_submit(pe_doc):
    return False
    """Update budget used when a Payment Entry is submitted."""
    # Ensure this is a Payment Entry affecting budget (Outgoing Payment)
    if pe_doc.payment_type not in ["Pay", "Receive"]:
        return False
    # Fetch related Purchase Invoice
    PAYMENT_FLAG_WITH_PI = False
    PAYMENT_FLAG_WITH_PO = False 
    PAYMENT_TYPE_RECEIVE = False
    DEBIT_NOTE_SUPPLIER = False  
    PARTY_TYPE_CUSTOMER = False
       
    # Iterate through the references table to check for Purchase Order or Purchase Invoice
    for reference in pe_doc.references:
        #logging.debug(f" in Payment Entry Doc Ref: {reference.reference_doctype} {reference.reference_name}")
        if reference.reference_doctype == "Purchase Order":
           PAYMENT_FLAG_WITH_PO = True
        elif reference.reference_doctype == "Purchase Invoice":
            PAYMENT_FLAG_WITH_PI = True
    #logging.debug(f"in Payment entry   {pe_doc.payment_type}, {PAYMENT_TYPE_RECEIVE}")
    # If Payment Receive entry reverse budget entry
    if pe_doc.payment_type == "Receive":
        PAYMENT_TYPE_RECEIVE = True

    # If Payment Receive entry reverse budget entry
    if pe_doc.party_type == "Supplier":
        DEBIT_NOTE_SUPPLIER = True

    if pe_doc.party_type in {"Shareholder", "Customer"}:
        #logging.debug(f"in payment entryparty  type custonmer {pe_doc.party_type}")
        PARTY_TYPE_CUSTOMER = True

    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
   # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {"company": pe_doc.company,"location":pe_doc.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":pe_doc.cost_center,"docstatus":1},
        "name")
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        return True 
    # Calculate the paid amount impacting budget
    total_vcm_paid_amount = flt(pe_doc.paid_amount)
    #If budget doc is vaailable then we must update budget
    budget_updated_flag = True  
    for budget_item in budget_doc.get("budget_items") or []:
            if budget_item.budget_head == pe_doc.budget_head:
                budget_updated_flag = False
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                #logging.debug(f"in update_vcm_pE_budget_usage direct receive without PI {total_vcm_paid_amount},{budget_item.paid_payment_entry}, {PAYMENT_FLAG_WITH_PI}")
                if PAYMENT_TYPE_RECEIVE and DEBIT_NOTE_SUPPLIER and (PAYMENT_FLAG_WITH_PI == False):
                    #this is supplier Debit note and it will be positive  number
                    #logging.debug(f"in update_vcm_pE_budget_usage direct receive without PI {total_vcm_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.paid_payment_entry -= total_vcm_paid_amount
                    budget_item.used_budget -= total_vcm_paid_amount  # Update Used Budget
                    budget_item.balance_budget += total_vcm_paid_amount  # Adjust Remaining Budget
                elif PAYMENT_TYPE_RECEIVE and DEBIT_NOTE_SUPPLIER and (PAYMENT_FLAG_WITH_PI == True):
                    #this is supplier Debit note and it will be positive  number
                    #logging.debug(f"in update_vcm_pE_budget_usage debit note {total_vcm_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.paid_payment_entry -= total_vcm_paid_amount 
                    budget_item.unpaid_purchase_invoice += total_vcm_paid_amount
                elif PAYMENT_FLAG_WITH_PI: 
                    #logging.debug(f"in update_vcm_pE_budget_usage 3 {total_vcm_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.unpaid_purchase_invoice -= total_vcm_paid_amount  #Decrease PI amount
                    if PAYMENT_TYPE_RECEIVE:
                        budget_item.paid_payment_entry -= total_vcm_paid_amount
                        #logging.debug(f"in Payment entry -3  {total_vcm_paid_amount}, {PAYMENT_TYPE_RECEIVE}")
                    else:
                        budget_item.paid_payment_entry += total_vcm_paid_amount  
                elif PAYMENT_FLAG_WITH_PO:
                    #logging.debug(f"in update_vcm_pe_budget_usage 3 {total_vcm_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.unpaid_purchase_order -= total_vcm_paid_amount  #Decrease PO amount
                    if PAYMENT_TYPE_RECEIVE:
                        #logging.debug(f"in Payment entry -4  {total_vcm_paid_amount}, {PAYMENT_TYPE_RECEIVE}")
                        budget_item.paid_payment_entry -= total_vcm_paid_amount
                    else:
                        budget_item.paid_payment_entry += total_vcm_paid_amount
                else:
                    if PARTY_TYPE_CUSTOMER == False:
                        #reduce and check budget for PI without PO
                        if PAYMENT_TYPE_RECEIVE:
                            budget_item.used_budget -= total_vcm_paid_amount  # Update Used Budget
                            budget_item.balance_budget += total_vcm_paid_amount  # Adjust Remaining Budget
                            budget_item.paid_payment_entry -= total_vcm_paid_amount 
                            #logging.debug(f"in Payment entry -25  {total_vcm_paid_amount}, {PAYMENT_TYPE_RECEIVE}")
                        else:
                            budget_item.used_budget += total_vcm_paid_amount  # Update Used Budget
                            budget_item.balance_budget -= total_vcm_paid_amount  # Adjust Remaining Budget
                            budget_item.paid_payment_entry += total_vcm_paid_amount 
                            #logging.debug(f"update_vcm_ w/O PI pi_budget_usage6, {budget_updated_flag}{budget_item.budget_head},{total_vcm_paid_amount}")           
                break 
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True

@frappe.whitelist()
def revert_vcm_budget_on_payment_submit(pe_doc):
    return False
    """Update budget used when a Payment Entry is submitted."""
    # Ensure this is a Payment Entry affecting budget (Outgoing Payment)
    if pe_doc.payment_type not in ["Pay", "Receive"]:
        return False   
     # Fetch related Purchase Invoice
    PAYMENT_FLAG_WITH_PI = False
    PAYMENT_FLAG_WITH_PO = False 
    PAYMENT_TYPE_RECEIVE = False  
    DEBIT_NOTE_SUPPLIER = False 
    PARTY_TYPE_CUSTOMER = False
        # If Payment Receive entry reverse budget entry
    if pe_doc.payment_type == "Receive":
        PAYMENT_TYPE_RECEIVE = True
    # Iterate through the references table to check for Purchase Order or Purchase Invoice
    for reference in pe_doc.references:
        #logging.debug(f" in Payment Entry DOc Ref: {reference.reference_doctype} {reference.reference_name}")
        if reference.reference_doctype == "Purchase Order":
           PAYMENT_FLAG_WITH_PO = True
        elif reference.reference_doctype == "Purchase Invoice":
            PAYMENT_FLAG_WITH_PI = True

        # If Payment Receive entry reverse budget entry
    if pe_doc.party_type == "Supplier":
        DEBIT_NOTE_SUPPLIER = True

    if pe_doc.party_type in {"Shareholder", "Customer"}:
        #logging.debug(f"in payment entryparty  type custonmer {pe_doc.party_type}")
        PARTY_TYPE_CUSTOMER = True

    # Iterate through the references table to check for Purchase Order or Purchase Invoice
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {"company": pe_doc.company,"location":pe_doc.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":pe_doc.cost_center,"docstatus":1},
        "name")
    # Fetch budget settings based on Cost Center or Project
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        return True 
    # Calculate the paid amount impacting budget
    total_paid_amount = flt(pe_doc.paid_amount)
    budget_updated_flag = True  
    for budget_item in budget_doc.get("budget_items") or []:            
            if budget_item.budget_head == pe_doc.budget_head:
                budget_updated_flag = False
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                if PAYMENT_TYPE_RECEIVE and DEBIT_NOTE_SUPPLIER and (PAYMENT_FLAG_WITH_PI == False):
                    #this is supplier Debit note and it will be positive  number
                    #logging.debug(f"in update_vcm_pE_budget_usage direct receive without PI {total_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.paid_payment_entry += total_paid_amount
                    budget_item.used_budget += total_paid_amount  # Update Used Budget
                    budget_item.balance_budget -= total_paid_amount  # Adjust Remaining Budget
                elif PAYMENT_TYPE_RECEIVE and DEBIT_NOTE_SUPPLIER and (PAYMENT_FLAG_WITH_PI == True):
                    #this is supplier Debit note and it will be positive  number
                    #logging.debug(f"in update_vcm_pE_budget_usage debit note cancell {total_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.paid_payment_entry += total_paid_amount 
                    budget_item.unpaid_purchase_invoice -= total_paid_amount
                elif PAYMENT_FLAG_WITH_PI: 
                    #logging.debug(f"revert update_vcm_pE_budget_usage 3 {total_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.unpaid_purchase_invoice += total_paid_amount  #Decrease PI amount
                    if PAYMENT_TYPE_RECEIVE:
                        budget_item.paid_payment_entry += total_paid_amount
                    else:
                        budget_item.paid_payment_entry -= total_paid_amount  
                elif PAYMENT_FLAG_WITH_PO:
                    #logging.debug(f"revert update_vcm_pE_budget_usage 3 {total_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.unpaid_purchase_order += total_paid_amount
                    if PAYMENT_TYPE_RECEIVE:
                        budget_item.paid_payment_entry += total_paid_amount
                    else:
                        budget_item.paid_payment_entry -= total_paid_amount
                else:
                    if PARTY_TYPE_CUSTOMER == False:
                        if PAYMENT_TYPE_RECEIVE:
                            budget_item.used_budget += total_paid_amount  # Update Used Budget
                            budget_item.balance_budget -= total_paid_amount  # Adjust Remaining Budget
                            budget_item.paid_payment_entry += total_paid_amount
                        else:
                            budget_item.used_budget -= total_paid_amount  # Update Used Budget
                            budget_item.balance_budget += total_paid_amount  # Adjust Remaining Budget
                            budget_item.paid_payment_entry -= total_paid_amount 
                            logging.debug(f"revert_PE_without PI usage6, {budget_item.budget_head},{total_paid_amount}") 
                logging.debug(f"revert_PE_without PI_budget_usage7, {budget_item.budget_head},{total_paid_amount}")                           
                break 
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True

@frappe.whitelist()
def validate_vcm_budget_from_jv(jv_doc):  
    return False  
    """
    Update Budget Used when a Journal Entry (JV) is submitted.
    """    
    #child table of JV, as Cost center is not in JV form, we need to pull from child table

    for account in jv_doc.accounts:  
        budget_updated_flag = False
        #logging.debug(f"update_vcm_JV 2 {account.cost_center},{account.debit}")
        if not account.budget_head:  # Consider only debit entries for expenses
            frappe.throw(f"Budget Head is mandatory for JV entry: {jv_doc.name}")
            return False
        if not account.location:  # Consider only debit entries for expenses
            frappe.throw(f"Budget Location is mandatory for JV entry: {jv_doc.name}")
            return False
        
        # Fetch account type of root_type
        account_type = frappe.get_value("Account", account.account, "root_type")
        #logging.debug(f"validate_vcm_JV is_exp: {account_type},{account.account}, {account.debit}, {account.credit}")
        if account_type == "Expense":
            # Consider only debit entries for expenses , as they consume budget
            # Don't worry about credit entry as they free budget
            if account.cost_center and account.debit > 0:  
                #vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
                #budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{account.cost_center}"
                vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
                # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
                budget_name = frappe.db.get_value(
                    "VCM Budget", 
                    {"company": jv_doc.company,"location":account.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":account.cost_center,"docstatus":1},
                    "name")
                # Fetch budget settings based on Cost Center or Project
                if frappe.db.exists("VCM Budget", budget_name):
                    budget_doc = frappe.get_doc("VCM Budget", budget_name)
                else:
                    #If there is no budget for this cost center then just move on
                    frappe.throw(f"Budget not available for Cost Center:{account.cost_center}, Location:{account.location}, Budget Head:{account.budget_head}")
                    return False                
                for budget_item in budget_doc.get("budget_items") or []: 
                    logging.debug(f"update_vcm_JV 3 , {account.budget_head},{budget_item.budget_head}, {budget_updated_flag}") 
                    if budget_item.budget_head == account.budget_head: 
                        logging.debug(f"MATCHED , {account.budget_head},{budget_item.budget_head}, {budget_updated_flag}")                    
                        if account.debit > budget_item.balance_budget:
                            frappe.throw(f"Budget Exceeded for JV {jv_doc.name}, Balance: {budget_item.balance_budget}, Request: {account.debit}")
                            return False
                        else:
                            budget_updated_flag = True
                            logging.debug(f"matched validate JV budget_usage6, {budget_item.budget_head},{budget_item.balance_budget}")
                            # save doc and DB commit here as JV may have naother cost center which will change the budget doc  
                if budget_updated_flag is False:
                    frappe.throw(f"Budget not available for Cost Center:{account.cost_center}, Location:{account.location}, Budget Head:{account.budget_head}")
                    return False

    return True

@frappe.whitelist()
def update_vcm_budget_from_jv(jv_doc): 
    return False   
    """
    Update Budget Used when a Journal Entry (JV) is submitted.
    """    
    #child table of JV, as Cost center is not in JV form, we need to pull from child table
    for account in jv_doc.accounts: 
        # Fetch account type of root_type
        account_type = frappe.get_value("Account", account.account, "root_type")
        logging.debug(f"update_vcm_JV is_exp: {account_type},{account.account}, {account.debit}, {account.credit}")
        if account_type == "Expense":
        # now we will ajust budget only for expense entries    
            #vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
            #budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{account.cost_center}"
            vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
            # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
            budget_name = frappe.db.get_value(
                "VCM Budget", 
                {"company": jv_doc.company,"location":account.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":account.cost_center,"docstatus":1},
                "name")
            logging.debug(f"In JV budget: {budget_name}")
            # Fetch budget settings based on Cost Center or Project
            if frappe.db.exists("VCM Budget", budget_name):
                budget_doc = frappe.get_doc("VCM Budget", budget_name)
            else:
                #If there is no budget for this cost center then just move on
                logging.debug(f"In JV submit budget name not found: {budget_name}")
                return False                
            for budget_item in budget_doc.get("budget_items") or []: 
                logging.debug(f"update_vcm_JV 3 , {account.budget_head},{budget_item.balance_budget}") 
                if budget_item.budget_head == account.budget_head:
                    # Adjust budget based on Debit and Credit values
                    if account.debit > 0:
                        # Increase budget usage
                        logging.debug(f"in update_JV Debit {account.budget_head}, {account.debit}")
                        budget_item.used_budget += account.debit
                        budget_item.balance_budget -= account.debit
                        budget_item.additional_je += account.debit
                        budget_updated_flag = False
                    elif account.credit > 0:
                        # Reduce budget usage (refund)
                        logging.debug(f"in update_JV Credit {account.budget_head}, {account.credit}")
                        budget_item.used_budget -= account.credit
                        budget_item.balance_budget += account.credit
                        budget_item.additional_je -= account.credit
                        budget_updated_flag = False
                    #logging.debug(f"revert_JV budget_usage6, {budget_item.used_budget},{account.debit}")
                    # save doc and DB commit here as JV may have naother cost center which will change the budget doc                
                budget_doc.save()
                frappe.db.commit()
    return True

@frappe.whitelist()
def reverse_vcm_budget_from_jv(jv_doc):
    return False
    """
    Update Budget Used when a Journal Entry (JV) is cancelled.
    """    
    #child table of JV, as Cost center is not in JV form, we need to pull from child table
    for account in jv_doc.accounts: 
        # Fetch account type of root_type
        account_type = frappe.get_value("Account", account.account, "root_type")
        logging.debug(f"reverse_vcm_JV is_exp: {account_type},{account.account}, {account.debit}, {account.credit}")
        if account_type == "Expense":
            #logging.debug(f"cancel_vcm_JV is_exp: {account_type},{account.account}, {account.debit}, ,{account.credit}")
            # now we will ajust budget only for expense entries      
            vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
            # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
            budget_name = frappe.db.get_value(
                "VCM Budget", 
                {"company": jv_doc.company,"location":account.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":account.cost_center,"docstatus":1},
                "name")
            logging.debug(f" reverse JV name: {budget_name}")
            # Fetch budget settings based on Cost Center or Project
            if frappe.db.exists("VCM Budget", budget_name):
                budget_doc = frappe.get_doc("VCM Budget", budget_name)
            else:
                #If there is no budget for this cost center then just move on
                logging.debug(f"In JV reverse budget name not found: {budget_name}")
                return False                
            for budget_item in budget_doc.get("budget_items") or []: 
                logging.debug(f"reverse _vcm_JV 3 , {account.budget_head},{budget_item.balance_budget}") 
                if budget_item.budget_head == account.budget_head:
                    # Adjust budget based on Debit and Credit values
                    if account.debit > 0:
                        # Decrease budget usage as we canceleld JV
                        #logging.debug(f"in cancel_JV Debit {account.budget_head},, {account.debit}")
                        budget_item.used_budget -= account.debit
                        budget_item.balance_budget += account.debit
                        budget_item.additional_je -= account.debit
                        budget_updated_flag = False
                    elif account.credit > 0:
                        # Increase budget usage (refund) as we canceleld JV
                        #logging.debug(f"in cancel_JV Credit {account.budget_head},{account.credit}")
                        budget_item.used_budget += account.credit
                        budget_item.balance_budget -= account.credit
                        budget_item.additional_je += account.credit
                        budget_updated_flag = False
                    logging.debug(f"revert_JV budget_usage6, {budget_item.used_budget},{account.debit}")
                    # save doc and DB commit here as JV may have naother cost center which will change the budget doc                
                budget_doc.save()
                frappe.db.commit()
    return True

@frappe.whitelist()          
def adjust_vcm_budget_reconciliation(payment_details, vcm_cost_center, vcm_budget_head, vcm_company):
    return False
    """
    Adjusts the VCM budget based on Payment Reconciliation for multiple invoices and payments.
    Explicitly fetches and processes related Payment Entries & Purchase Invoices.
    """
    #logging.debug(f"VCM adjust_vcm_budget_reconciliation {vcm_budget_settings.payment_reconciliation},{vcm_cost_center},{vcm_budget_head}")
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    if vcm_budget_settings.payment_reconciliation == "Yes":
        #logging.debug(f"in adjust_vcm_budget_reconciliation 1 {payment_details}")       
        # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
        budget_name = frappe.db.get_value(
            "VCM Budget", 
            {"company": vcm_company,"location":payment_details.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":vcm_cost_center,"docstatus":1},
            "name")
        #logging.debug(f"in adjust_vcm_budget_reconciliation Budget name {budget_name}") 
        # Fetch budget settings based on Cost Center or Project
        if frappe.db.exists("VCM Budget", budget_name):
            budget_doc = frappe.get_doc("VCM Budget", budget_name)
        else:
            #If there is no busget for this cost center then just move on
            logging.debug(f"in adjust_vcm_budget_reconciliation  Budget not found error {budget_name}")
            return True
        budget_updated_flag = True
        for budget_item in budget_doc.get("budget_items") or []: 
                #logging.debug(f"vcm_budget_reconc 2-2 {payment_details.allocated_amount},{vcm_cost_center}, {budget_item.budget_head}, {vcm_budget_head},{payment_details.budget_head}")           
                #if budget_item.budget_head == payment_details.budget_head:
                if budget_item.budget_head == vcm_budget_head:
                    budget_updated_flag = False                
                    budget_item.unpaid_purchase_invoice -= payment_details.allocated_amount
                    budget_item.used_budget -= payment_details.allocated_amount
                    budget_item.balance_budget += payment_details.allocated_amount                
                    #logging.debug(f"vcm_budget_reconc 2-2, {budget_item.unpaid_purchase_invoice},{budget_item.used_budget},{budget_item.balance_budget}")                           
                    break 
        # Save and commit changes
        budget_doc.save(ignore_permissions=True)
        frappe.db.commit()
        return True    

@frappe.whitelist()
def cancel_vcm_PI_reconciliation(purchase_invoice):
    return False
    """
    Adjusts the VCM budget based on Payment Reconciliation for multiple invoices and payments.
    Explicitly fetches and processes related Payment Entries & Purchase Invoices. """
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    logging.debug(f"VCM adjust_vcm_budget_reconciliation {vcm_budget_settings.payment_reconciliation}")
    if vcm_budget_settings.payment_reconciliation == "Yes":
        logging.debug(f"in adjust_vcm_budget_reconciliation 1 {purchase_invoice}, {purchase_invoice.cost_center}")
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        budget_name = frappe.db.get_value(
                        "VCM Budget", 
                        {"company": purchase_invoice.company,"location":purchase_invoice.location,"fiscal_year":vcm_budget_settings.financial_year,"cost_center":purchase_invoice.cost_center,"docstatus":1},
                        "name")
        # Fetch budget settings based on Cost Center or Project
        if frappe.db.exists("VCM Budget", budget_name):
            budget_doc = frappe.get_doc("VCM Budget", budget_name)
        else:
            #If there is no busget for this cost center then just move on
            logging.debug(f"in cancel_vcm_budget_reconciliation Budget Not found {budget_name}")
            frappe.throw(f"Budget not available for Cost Center:{purchase_invoice.cost_center}, Location:{purchase_invoice.location}, Budget Head:{purchase_invoice.budget_head}")
            return True
        budget_updated_flag = True
        for budget_item in budget_doc.get("budget_items") or []: 
                logging.debug(f"cancel vcm_budget_reconc 2-2 {purchase_invoice.name},{purchase_invoice.budget_head}")           
                if budget_item.budget_head == purchase_invoice.budget_head:
                    budget_updated_flag = False
                    # Here we have two cases , when PI amount is less then we will free PI amount
                    # But if Payment entry amount was less then we need to free Payment entry amount
                    # # lets find Payment ENtry 
                    # 
                    # payment_entries = frappe.get_all(
                    #     "Payment Entry Reference",
                    #     filters={"reference_doctype": "Purchase Invoice", "reference_name": purchase_invoice.name, "parent": },
                    #     fields=["allocated_amount"]
                    # )
                    #logging.debug(f"vcm_budget_reconc 2-1 {payment_entries}")
                    #for entry in payment_entries:                        
                        #reco_payment = entry['allocated_amount']
                        #logging.debug(f"vcm_budget_reconc 2-3 {reco_payment}, {entry}")
                                        
                    #if (purchase_invoice.grand_total <=  reco_payment):              
                    #logging.debug(f"vcm_budget_reconc 3 {purchase_invoice.grand_total},{reco_payment}, {purchase_invoice.cost_center}, {purchase_invoice.budget_head}")
                    budget_item.unpaid_purchase_invoice += purchase_invoice.grand_total
                    budget_item.used_budget += purchase_invoice.grand_total
                    budget_item.balance_budget -= purchase_invoice.grand_total                
                    break 
                   # else:
                        #logging.debug(f"vcm_budget_reconc 3-1 {purchase_invoice.grand_total},{reco_payment}, {purchase_invoice.cost_center}, {purchase_invoice.budget_head}")
                    #    budget_item.unpaid_purchase_invoice += reco_payment
                    #    budget_item.used_budget += reco_payment
                    #    budget_item.balance_budget -= reco_payment                
                    #    break 

        # Save and commit changes
        budget_doc.save(ignore_permissions=True)
        frappe.db.commit()
        return True
                            
@frappe.whitelist()
def validate_budget_head_n_location_mandatory(doc):
        #Journal Entry has cost center in child table, rest other doc have in main doc
        if doc.doctype == "Journal Entry":
            for row in doc.accounts:  # Assuming 'accounts' is the child table in Journal Entry
                if frappe.db.exists("Cost Center", row.cost_center):
                    cost_center_doc = frappe.get_doc("Cost Center", row.cost_center)
                    # check if Budget is applicable for this cost center
            if cost_center_doc.custom_vcm_budget_applicable ==  "Yes":
                # is yes, then Budget Head is mandatory
                if not row.budget_head:
                    frappe.throw(f"Budget Head is mandatory for Cost Center where Budget is applicable: {row.cost_center}")
                    return False
                if not row.location:
                    frappe.throw(f"Location is mandatory for Cost Center where Budget is applicable: {row.cost_center}")
                    return False
                return True
            else:
                return False
        else: 
            #logging.debug(f"validate_budget_head_mandatory 1")       
            if frappe.db.exists("Cost Center", doc.cost_center):
                cost_center_doc = frappe.get_doc("Cost Center", doc.cost_center)
                #logging.debug(f"validate_budget_head_mandatory 1 {cost_center_doc},{cost_center_doc.custom_vcm_budget_applicable},{doc.budget_head}  ")
                # check if Budget is applicable for this cost center
                if cost_center_doc.custom_vcm_budget_applicable ==  "Yes":
                    # is yes, then Budget Head is mandatory
                    if not doc.budget_head:
                        frappe.throw(f"Budget Head is mandatory for Cost Center where Budget is applicable: {doc.cost_center}")
                        return False
                    if not doc.location:
                        frappe.throw(f"Location is mandatory for Cost Center where Budget is applicable: {doc.location}")
                        return False
                    #logging.debug(f"validate_budget_head_mandatory 2 True {doc.cost_center}")  
                    return True
                else:
                    #logging.debug(f"validate_budget_head_mandatory 3 False {doc.cost_center} ")  
                    return False
            else:
                #logging.debug(f"validate_budget_head_mandatory 5 False {doc.cost_center} ")  
                return False
            

     


        