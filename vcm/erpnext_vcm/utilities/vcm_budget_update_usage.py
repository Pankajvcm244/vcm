import frappe
from frappe.utils import flt
import logging
logging.basicConfig(level=logging.DEBUG)

@frappe.whitelist()
def validate_vcm_po_budget_amount_budgethead(po_doc):
    """ Updates the used budget in VCM Budget when a PO is submitted """
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    company_name = frappe.get_doc("Company", po_doc.company)
    company_abbr = company_name.abbr
    #budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{pe_doc.cost_center}"
    budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{po_doc.location}-{po_doc.cost_center}"

    
    #logging.debug(f"in validate_vcm_po_ 2 {budget_name}")
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        return True    
    budget_validation_flag = True  
    for budget_item in budget_doc.get("budget_items") or []:
        #logging.debug(f"in validate_vcm_po_budget_amount_budgethead 2 {po_doc.budget_head}")
        if budget_item.budget_head == po_doc.budget_head:
            budget_validation_flag = False
            if po_doc.rounded_total > budget_item.balance_budget:
                frappe.throw(f"Budget Exceeded for {po_doc.budget_head}, Balance: {budget_item.balance_budget}, Request: {po_doc.rounded_total}")
                #logging.debug(f"validate_vcm_po_budget_amount_budgethead budget exceeded return false")
                return False
    if budget_validation_flag:
        frappe.throw(f"PO Budget not found for Cost Center: {po_doc.cost_center}, Budget Head: {po_doc.budget_head}")
        return False        
    return True


@frappe.whitelist()
def update_vcm_po_budget_usage(po_doc):
    """ Updates the used budget in VCM Budget when a PO is submitted """
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    company_name = frappe.get_doc("Company", po_doc.company)
    company_abbr = company_name.abbr
    #budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{pe_doc.cost_center}"
    budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{po_doc.location}-{po_doc.cost_center}"
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        return True 
    #budget_updated_flag = True
    for budget_item in budget_doc.get("budget_items") or []:
        #logging.debug(f"in update_vcm_po_budget_usage 2 {po_doc.budget_head}")
        if budget_item.budget_head == po_doc.budget_head:
            #budget_updated_flag = False
            #logging.debug(f"in update_vcm_po_budget_usage 3 {po_doc.rounded_total}")
            budget_item.used_budget += po_doc.rounded_total  # Update Used Budget
            budget_item.balance_budget -= po_doc.rounded_total  # Adjust Remaining Budget
            budget_item.unpaid_purchase_order += po_doc.rounded_total  # Adjust Remaining Budget
            #logging.debug(f"update_vcm_po_budget_usage6, {budget_item.budget_head},{po_doc.rounded_total}")                           
            break
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()    
    #logging.debug(f"update_vcm_po_budget_usage10 return true")
    return True

@frappe.whitelist()
def revert_vcm_po_budget_usage(po_doc):
    """ Reverts budget usage when PO is canceled """
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    company_name = frappe.get_doc("Company", po_doc.company)
    company_abbr = company_name.abbr
    budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{po_doc.location}-{po_doc.cost_center}"
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        return True    
    for budget_item in budget_doc.get("budget_items") or []:
        if budget_item.budget_head == po_doc.budget_head:
            budget_item.used_budget -= po_doc.rounded_total  # Revert Used Budget
            budget_item.balance_budget += po_doc.rounded_total  # Restore Balance
            budget_item.unpaid_purchase_order -= po_doc.rounded_total
            #logging.debug(f"revert vcm_po_budget -1, {budget_item.budget_head},{po_doc.rounded_total}")            
            break
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
    company_name = frappe.get_doc("Company", pi_doc.company)
    company_abbr = company_name.abbr
    budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{pi_doc.location}-{pi_doc.cost_center}"
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
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

    for budget_item in budget_doc.get("budget_items") or []:
            if budget_item.budget_head == pi_doc.budget_head:
                budget_updated_flag = False
                budget_validation_flag = False
                #logging.debug(f"in update_vcm_po_budget_usage 3 {po_doc.rounded_total}")                
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                if PI_FLAG_WITH_PO: 
                    a = 0                    
                    #logging.debug(f"PI With PO , {pi_doc.budget_head},{tax_deducted},{budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total}")                
                else:
                    # #reduce and check budget for PI without PO
                    if (pi_doc.rounded_total - total_vcm_advance + tax_deducted ) > budget_item.balance_budget:
                        frappe.throw(f"Budget exceeded for:{pi_doc.budget_head},Balance:{budget_item.balance_budget},Request:{pi_doc.rounded_total}, Adv: {total_vcm_advance}, Tax: {tax_deducted}")
                        return False
                    #logging.debug(f"Direct PI W/O PO ,{pi_doc.budget_head}, {tax_deducted}, {budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total},{total_vcm_advance}") 
                break

    if budget_validation_flag:
        frappe.throw(f"PI Budget not found for Budget Head: {pi_doc.budget_head}")
        return False        
    return True

@frappe.whitelist()
def update_vcm_pi_budget_usage(pi_doc):
    """Update budget used amount when a Purchase Invoice is submitted."""
    PI_FLAG_WITH_PO = False
    PI_FLAG_WITH_RETURN = False
    #logging.debug(f"in update_vcm_pi_budget_usage 1 {pi_doc}")
    for item in pi_doc.items:
        #logging.debug(f"in Purchase InvoiceDOc Ref: {item}, {item.purchase_order} ")
        if item.purchase_order:
            PI_FLAG_WITH_PO = True
            break  # Exit loop as soon as we find a linked PO        
    
    logging.debug(f"in PI -1: {pi_doc.is_return} ")
    # this is Return/Debit nore entry from Purchase Invocie
    if pi_doc.is_return == 1:
        logging.debug(f"in PI_FLAG_WITH_RETURN: {pi_doc.rounded_total} , PI_FLAG_WITH_RETURN")
        PI_FLAG_WITH_RETURN = True

    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    company_name = frappe.get_doc("Company", pi_doc.company)
    company_abbr = company_name.abbr
    budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{pi_doc.location}-{pi_doc.cost_center}"
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        return True 
    #budget_updated_flag = True

    total_vcm_advance = 0.0  # Initialize advance amount
    # Check if advances exist
    if pi_doc.advances:
        for advance in pi_doc.advances:
            total_vcm_advance += flt(advance.allocated_amount)  # Sum allocated advances
    #logging.debug(f"in Purchase Invoice Advance: {pi_doc.allocate_advances_automatically}, {total_vcm_advance} ")
    tax_deducted = 0.0  # Initialize advance amount
    if pi_doc.taxes_and_charges_deducted:
        tax_deducted = pi_doc.taxes_and_charges_deducted

    for budget_item in budget_doc.get("budget_items") or []:
            if budget_item.budget_head == pi_doc.budget_head:
                #budget_updated_flag = False
                #logging.debug(f"in update_vcm_po_budget_usage 3 {po_doc.rounded_total}")                
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                if PI_FLAG_WITH_PO:
                    if PI_FLAG_WITH_RETURN:
                        # return amount comes as -ve number
                        logging.debug(f"in PI-PO - with return: {pi_doc.rounded_total}")
                        budget_item.unpaid_purchase_invoice += (pi_doc.rounded_total - total_vcm_advance + tax_deducted )  #Increase PI amount
                    else:
                        budget_item.unpaid_purchase_order -= (pi_doc.rounded_total - total_vcm_advance + tax_deducted)
                        budget_item.unpaid_purchase_invoice += (pi_doc.rounded_total - total_vcm_advance + tax_deducted )  #Increase PI amount
                        logging.debug(f"PI With PO , {pi_doc.budget_head},{tax_deducted},{budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total}")
                else:
                    if PI_FLAG_WITH_RETURN:
                        logging.debug(f"in PI - with return: {pi_doc.rounded_total} ")
                        budget_item.used_budget += (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Update Used Budget
                        budget_item.balance_budget -= (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Adjust Remaining Budget
                        budget_item.unpaid_purchase_invoice += (pi_doc.rounded_total - total_vcm_advance + tax_deducted) 
                    else:
                        #reduce and check budget for PI without PO                   
                        budget_item.used_budget += (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Update Used Budget
                        budget_item.balance_budget -= (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Adjust Remaining Budget
                        budget_item.unpaid_purchase_invoice += (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Adjust Remaining Budget
                        logging.debug(f"Direct PI W/O PO ,{pi_doc.budget_head}, {tax_deducted}, {budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total},{total_vcm_advance}") 
                break
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True

@frappe.whitelist()
def revert_vcm_pi_budget_usage(pi_doc):
    PI_FLAG_WITH_PO = False
    PI_FLAG_WITH_RETURN = False
    #logging.debug(f"in revert_vcm_pi_budget_usage 1 {pi_doc}")
    for item in pi_doc.items:
        #logging.debug(f"in revert Purchase InvoiceDOc Ref: {item}, {item.purchase_order} ")
        if item.purchase_order:
            PI_FLAG_WITH_PO = True
            break  # Exit loop as soon as we find a linked PO
    
    logging.debug(f"in PI return -1: {pi_doc.is_return}, {PI_FLAG_WITH_RETURN} ")
    # this is Return/Debit nore entry from Purchase Invocie
    if pi_doc.is_return == 1:
        PI_FLAG_WITH_RETURN = True
        logging.debug(f"in revert PI return flag: {pi_doc.is_return} , PI_FLAG_WITH_RETURN ")

    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    company_name = frappe.get_doc("Company", pi_doc.company)
    company_abbr = company_name.abbr
    budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{pi_doc.location}-{pi_doc.cost_center}"
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no busget for this cost center then just move on
        #logging.debug(f"in validate_vcm_po_ 3 {budget_name}")
        return True 
    #budget_updated_flag = True
    total_vcm_advance = 0.0  # Initialize advance amount     
    # Check if advances exist
    if pi_doc.advances:
        for advance in pi_doc.advances:
            total_vcm_advance += flt(advance.allocated_amount)  # Sum allocated advances
    #logging.debug(f"in Purchase Invoice Advance: {pi_doc.allocate_advances_automatically}, {total_vcm_advance} ")
    tax_deducted = 0.0  # Initialize advance amount
    if pi_doc.taxes_and_charges_deducted:
        tax_deducted = pi_doc.taxes_and_charges_deducted

    for budget_item in budget_doc.get("budget_items") or []:
            #logging.debug(f"in update_vcm_pi_budget_usage 2 {pi_doc.budget_head}")
            if budget_item.budget_head == pi_doc.budget_head:
                #budget_updated_flag = False
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                if PI_FLAG_WITH_PO:
                    if PI_FLAG_WITH_RETURN:
                        logging.debug(f"PI With PO return, {pi_doc.rounded_total}, {PI_FLAG_WITH_RETURN}")
                        budget_item.unpaid_purchase_order += (pi_doc.rounded_total - total_vcm_advance + tax_deducted)
                        budget_item.unpaid_purchase_invoice -= (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  
                        logging.debug(f"PI With PO revert return, {tax_deducted}, {budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total}")
                    else:
                        budget_item.unpaid_purchase_order += (pi_doc.rounded_total - total_vcm_advance + tax_deducted)
                        budget_item.unpaid_purchase_invoice -= (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  
                        logging.debug(f"PI With PO revert , {tax_deducted}, {budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total}")
                else:
                    if PI_FLAG_WITH_RETURN:
                        logging.debug(f"PI return, {pi_doc.rounded_total}")
                        budget_item.used_budget -= (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Update Used Budget
                        budget_item.balance_budget += (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Adjust Remaining Budget
                        budget_item.unpaid_purchase_invoice -= (pi_doc.rounded_total - total_vcm_advance + tax_deducted)
                    else:
                        #reduce and check budget for PI without PO
                        budget_item.used_budget -= (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Update Used Budget
                        budget_item.balance_budget += (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Adjust Remaining Budget
                        budget_item.unpaid_purchase_invoice -= (pi_doc.rounded_total - total_vcm_advance + tax_deducted)  # Adjust Remaining Budget
                        logging.debug(f"Direct PI revert W/O PO , {tax_deducted}, {budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total},{total_vcm_advance}")           
                break
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True

@frappe.whitelist()
def validate_vcm_budget_on_payment_entry(pe_doc):
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
    company_name = frappe.get_doc("Company", pe_doc.company)
    company_abbr = company_name.abbr
    budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{pe_doc.location}-{pe_doc.cost_center}"
    # Fetch budget settings based on Cost Center or Project
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
        #logging.debug(f" in Payment Entry DOc Ref: {reference.reference_doctype} {reference.reference_name}")
        if reference.reference_doctype == "Purchase Order":
           PAYMENT_FLAG_WITH_PO = True
        elif reference.reference_doctype == "Purchase Invoice":
            PAYMENT_FLAG_WITH_PI = True
    logging.debug(f"in Payment entry   {pe_doc.payment_type}, {PAYMENT_TYPE_RECEIVE}")
    # If Payment Receive entry reverse budget entry
    if pe_doc.payment_type == "Receive":
        PAYMENT_TYPE_RECEIVE = True

    # If Payment Receive entry reverse budget entry
    if pe_doc.party_type == "Supplier":
        DEBIT_NOTE_SUPPLIER = True

    if pe_doc.party_type in {"Shareholder", "Customer"}:
        logging.debug(f"in payment entryparty  type custonmer {pe_doc.party_type}")
        PARTY_TYPE_CUSTOMER = True

    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    company_name = frappe.get_doc("Company", pe_doc.company)
    company_abbr = company_name.abbr
    budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{pe_doc.location}-{pe_doc.cost_center}"
    #logging.debug(f"{company_abbr}-{vcm_budget_settings.financial_year}-{pe_doc.location}-{pe_doc.cost_center}")
    # Fetch budget settings based on Cost Center or Project
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
                if PAYMENT_TYPE_RECEIVE and DEBIT_NOTE_SUPPLIER:
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
                        logging.debug(f"in Payment entry -4  {total_vcm_paid_amount}, {PAYMENT_TYPE_RECEIVE}")
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
                            logging.debug(f"in Payment entry -25  {total_vcm_paid_amount}, {PAYMENT_TYPE_RECEIVE}")
                        else:
                            budget_item.used_budget += total_vcm_paid_amount  # Update Used Budget
                            budget_item.balance_budget -= total_vcm_paid_amount  # Adjust Remaining Budget
                            budget_item.paid_payment_entry += total_vcm_paid_amount 
                            logging.debug(f"update_vcm_ w/O PI pi_budget_usage6, {budget_updated_flag}{budget_item.budget_head},{total_vcm_paid_amount}")           
                break 
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True

@frappe.whitelist()
def revert_vcm_budget_on_payment_submit(pe_doc):
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
    company_name = frappe.get_doc("Company", pe_doc.company)
    company_abbr = company_name.abbr
    budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{pe_doc.location}-{pe_doc.cost_center}"
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
                if PAYMENT_TYPE_RECEIVE and DEBIT_NOTE_SUPPLIER:
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
                            #logging.debug(f"revert_PE_without PI usage6, {budget_item.budget_head},{total_paid_amount}") 
                #logging.debug(f"revert_PE_without PI_budget_usage7, {budget_item.budget_head},{total_paid_amount}")                           
                break 
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True

@frappe.whitelist()
def validate_vcm_budget_from_jv(jv_doc):    
    """
    Update Budget Used when a Journal Entry (JV) is submitted.
    """    
    #child table of JV, as Cost center is not in JV form, we need to pull from child table
    for account in jv_doc.accounts:  
        #logging.debug(f"update_vcm_JV 2 {account.cost_center},{account.debit}")
        if not account.budget_head:  # Consider only debit entries for expenses
            frappe.throw(f"Budget Head is mandatory for JV entry: {jv_doc.name}")
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
                company_name = frappe.get_doc("Company", account.company)
                company_abbr = company_name.abbr
                budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{account.location}-{account.cost_center}"
                # Fetch budget settings based on Cost Center or Project
                if frappe.db.exists("VCM Budget", budget_name):
                    budget_doc = frappe.get_doc("VCM Budget", budget_name)
                else:
                    #If there is no budget for this cost center then just move on
                    return True                
                for budget_item in budget_doc.get("budget_items") or []: 
                    #logging.debug(f"update_vcm_JV 3 , {account.budget_head},{budget_item.balance_budget}") 
                    if budget_item.budget_head == account.budget_head:                    
                        if account.debit > budget_item.balance_budget:
                            frappe.throw(f"Budget Exceeded for JV {jv_doc.name}, Balance: {budget_item.balance_budget}, Request: {account.debit}")
                            return False
                        else:
                            budget_updated_flag = False
                            #logging.debug(f"revert_JV budget_usage6, {budget_item.used_budget},{account.debit}")
                            # save doc and DB commit here as JV may have naother cost center which will change the budget doc                
                if budget_updated_flag:
                    frappe.throw(f"JV Budget not found for Budget Head: {account.budget_head}")
                    return False
    return True

@frappe.whitelist()
def update_vcm_budget_from_jv(jv_doc):    
    """
    Update Budget Used when a Journal Entry (JV) is submitted.
    """    
    #child table of JV, as Cost center is not in JV form, we need to pull from child table
    for account in jv_doc.accounts: 
        # Fetch account type of root_type
        account_type = frappe.get_value("Account", account.account, "root_type")
        #logging.debug(f"update_vcm_JV is_exp: {account_type},{account.account}, {account.debit}, {account.credit}")
        if account_type == "Expense":
        # now we will ajust budget only for expense entries    
            #vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
            #budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{account.cost_center}"
            vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
            company_name = frappe.get_doc("Company", account.company)
            company_abbr = company_name.abbr
            budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{account.location}-{account.cost_center}"
            # Fetch budget settings based on Cost Center or Project
            if frappe.db.exists("VCM Budget", budget_name):
                budget_doc = frappe.get_doc("VCM Budget", budget_name)
            else:
                #If there is no budget for this cost center then just move on
                return True                
            for budget_item in budget_doc.get("budget_items") or []: 
                #logging.debug(f"update_vcm_JV 3 , {account.budget_head},{budget_item.balance_budget}") 
                if budget_item.budget_head == account.budget_head:
                    # Adjust budget based on Debit and Credit values
                    if account.debit > 0:
                        # Increase budget usage
                        #logging.debug(f"in update_JV Debit {account.budget_head}, {account.debit}")
                        budget_item.used_budget += account.debit
                        budget_item.balance_budget -= account.debit
                        budget_item.additional_je += account.debit
                        budget_updated_flag = False
                    elif account.credit > 0:
                        # Reduce budget usage (refund)
                        #logging.debug(f"in update_JV Credit {account.budget_head}, {account.credit}")
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
    """
    Update Budget Used when a Journal Entry (JV) is cancelled.
    """    
    #child table of JV, as Cost center is not in JV form, we need to pull from child table
    for account in jv_doc.accounts: 
        # Fetch account type of root_type
        account_type = frappe.get_value("Account", account.account, "root_type")
        #logging.debug(f"update_vcm_JV is_exp: {account_type},{account.account}, {account.debit}, {account.credit}")
        if account_type == "Expense":
            #logging.debug(f"cancel_vcm_JV is_exp: {account_type},{account.account}, {account.debit}, ,{account.credit}")
            # now we will ajust budget only for expense entries      
            #vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
            #budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{account.cost_center}"
            vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
            company_name = frappe.get_doc("Company", account.company)
            company_abbr = company_name.abbr
            budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{account.location}-{account.cost_center}"
            # Fetch budget settings based on Cost Center or Project
            if frappe.db.exists("VCM Budget", budget_name):
                budget_doc = frappe.get_doc("VCM Budget", budget_name)
            else:
                #If there is no budget for this cost center then just move on
                return True                
            for budget_item in budget_doc.get("budget_items") or []: 
                #logging.debug(f"update_vcm_JV 3 , {account.budget_head},{budget_item.balance_budget}") 
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
                    #logging.debug(f"revert_JV budget_usage6, {budget_item.used_budget},{account.debit}")
                    # save doc and DB commit here as JV may have naother cost center which will change the budget doc                
                budget_doc.save()
                frappe.db.commit()
    return True

@frappe.whitelist()          
def adjust_vcm_budget_reconciliation(payment_details, vcm_cost_center, vcm_budget_head):
    """
    Adjusts the VCM budget based on Payment Reconciliation for multiple invoices and payments.
    Explicitly fetches and processes related Payment Entries & Purchase Invoices.
    """
    #logging.debug(f"VCM adjust_vcm_budget_reconciliation {vcm_budget_settings.payment_reconciliation},{vcm_cost_center},{vcm_budget_head}")
    if vcm_budget_settings.payment_reconciliation == "Yes":
        #logging.debug(f"in adjust_vcm_budget_reconciliation 1 {payment_details}")
        #vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        #budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{vcm_cost_center}"
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        company_name = frappe.get_doc("Company", payment_details.company)
        company_abbr = company_name.abbr
        budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{payment_details.location}-{vcm_cost_center}"
        # Fetch budget settings based on Cost Center or Project
        if frappe.db.exists("VCM Budget", budget_name):
            budget_doc = frappe.get_doc("VCM Budget", budget_name)
        else:
            #If there is no busget for this cost center then just move on
            #logging.debug(f"in adjust_vcm_budget_reconciliation 2 {budget_name}")
            return True
        budget_updated_flag = True
        for budget_item in budget_doc.get("budget_items") or []: 
                #logging.debug(f"vcm_budget_reconc 2-2 {payment_details.allocated_amount},{vcm_cost_center}, {budget_item.budget_head}, {vcm_budget_head},{payment_details.budget_head}")           
                #if budget_item.budget_head == payment_details.budget_head:
                if budget_item.budget_head == vcm_budget_head:
                    budget_updated_flag = False                
                    #logging.debug(f"vcm_budget_reconc 3 {payment_details.allocated_amount},{vcm_cost_center}, {payment_details.budget_head}")
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
    """
    Adjusts the VCM budget based on Payment Reconciliation for multiple invoices and payments.
    Explicitly fetches and processes related Payment Entries & Purchase Invoices.
    """
    logging.debug(f"VCM adjust_vcm_budget_reconciliation {vcm_budget_settings.payment_reconciliation}")
    if vcm_budget_settings.payment_reconciliation == "Yes":
        #logging.debug(f"in adjust_vcm_budget_reconciliation 1 {purchase_invoice}, {purchase_invoice.cost_center}")
        #vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        #budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{purchase_invoice.cost_center}"
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        company_name = frappe.get_doc("Company", purchase_invoice.company)
        company_abbr = company_name.abbr
        budget_name = f"{company_abbr}-{vcm_budget_settings.financial_year}-{purchase_invoice.location}-{purchase_invoice.cost_center}"
        # Fetch budget settings based on Cost Center or Project
        if frappe.db.exists("VCM Budget", budget_name):
            budget_doc = frappe.get_doc("VCM Budget", budget_name)
        else:
            #If there is no busget for this cost center then just move on
            #logging.debug(f"in cancel_vcm_budget_reconciliation 2 {budget_name}")
            return True
        budget_updated_flag = True
        for budget_item in budget_doc.get("budget_items") or []: 
                #logging.debug(f"cancel vcm_budget_reconc 2-2 {purchase_invoice.grand_total},{purchase_invoice.budget_head}")           
                if budget_item.budget_head == purchase_invoice.budget_head:
                    budget_updated_flag = False                
                    #logging.debug(f"vcm_budget_reconc 3 {purchase_invoice.grand_total},{purchase_invoice.cost_center}, {purchase_invoice.budget_head}")
                    budget_item.unpaid_purchase_invoice += purchase_invoice.grand_total
                    budget_item.used_budget += purchase_invoice.grand_total
                    budget_item.balance_budget -= purchase_invoice.grand_total                
                    break 
        # Save and commit changes
        budget_doc.save(ignore_permissions=True)
        frappe.db.commit()
        return True
                            
@frappe.whitelist()
def validate_budget_head_mandatory(doc):
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
            

     


        