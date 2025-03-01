import frappe
from frappe.utils import flt
import logging
logging.basicConfig(level=logging.DEBUG)

@frappe.whitelist()
def update_vcm_po_budget_usage(po_doc):
    """ Updates the used budget in VCM Budget when a PO is submitted """
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{po_doc.cost_center}"
    budget_doc = frappe.get_doc("VCM Budget", budget_name)
    if not budget_doc:
        #frappe.throw(f"Budget not found for {po_doc.name}, {po_doc.cost_center}")
        return False
    budget_updated_flag = False
    for budget_item in budget_doc.get("budget_items") or []:
        logging.debug(f"in update_vcm_po_budget_usage 2 {po_doc.budget_head}")
        if budget_item.budget_head == po_doc.budget_head:
            if po_doc.rounded_total > budget_item.balance_budget:
                frappe.throw(f"Budget Exceeded for {po_doc.budget_head}, Balance: {budget_item.balance_budget}, Request: {po_doc.rounded_total}")
                return False
            else:
                #logging.debug(f"in update_vcm_po_budget_usage 3 {po_doc.rounded_total}")
                budget_item.used_budget += po_doc.rounded_total  # Update Used Budget
                budget_item.balance_budget -= po_doc.rounded_total  # Adjust Remaining Budget
                budget_item.unpaid_purchase_order += po_doc.rounded_total  # Adjust Remaining Budget
                #logging.debug(f"update_vcm_po_budget_usage6, {budget_item.budget_head},{po_doc.rounded_total}")  
                budget_updated_flag = True           
                break
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    #if not budget_updated_flag:
    #    frappe.throw(f"Budget not found for Budget Head{po_doc.budget_head}")
    #    return False
    return True

@frappe.whitelist()
def revert_vcm_po_budget_usage(po_doc):
    """ Reverts budget usage when PO is canceled """
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{po_doc.cost_center}"
    budget_doc = frappe.get_doc("VCM Budget", budget_name)
    if not budget_doc:
        frappe.throw(f"Budget not found for {po_doc.name}, {po_doc.cost_center}")
        return False
    budget_updated_flag = False
    for budget_item in budget_doc.get("budget_items") or []:
        if budget_item.budget_head == po_doc.budget_head:
            budget_item.used_budget -= po_doc.rounded_total  # Revert Used Budget
            budget_item.balance_budget += po_doc.rounded_total  # Restore Balance
            budget_item.unpaid_purchase_order -= po_doc.rounded_total
            #logging.debug(f"revert vcm_po_budget -1, {budget_item.budget_head},{po_doc.rounded_total}")
            budget_updated_flag = True
            break
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    #if not budget_updated_flag:
    #    frappe.throw(f"Budget Head not found for {po_doc.budget_head}")
    #    return False
    return True

@frappe.whitelist()
def update_vcm_pi_budget_usage(pi_doc):
    """Update budget used amount when a Purchase Invoice is submitted."""
    PI_FLAG_WITH_PO = False
    logging.debug(f"in update_vcm_pi_budget_usage 1 {pi_doc}")
    for item in pi_doc.items:
        if item.purchase_order:
            PI_FLAG_WITH_PO = True
            break  # Exit loop as soon as we find a linked PO
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{pi_doc.cost_center}"
    budget_doc = frappe.get_doc("VCM Budget", budget_name)
    if not budget_doc:
        frappe.throw(f"No budget found for Cost Center: {pi_doc.cost_center}")
        return False
    budget_updated_flag = False   

    for budget_item in budget_doc.get("budget_items") or []:
            if budget_item.budget_head == pi_doc.budget_head:
                #logging.debug(f"in update_vcm_po_budget_usage 3 {po_doc.rounded_total}")
                
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                if PI_FLAG_WITH_PO:  
                    budget_item.unpaid_purchase_order -= pi_doc.rounded_total
                    budget_item.unpaid_purchase_invoice += pi_doc.rounded_total  #Increase PI amount
                    logging.debug(f"PI With PO , {pi_doc.budget_head},{budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total}")
                else:
                    #reduce and check budget for PI without PO
                    if pi_doc.rounded_total > budget_item.balance_budget:
                        frappe.throw(f"Budget Exceeded for {pi_doc.budget_head}, Balance: {budget_item.balance_budget}, Request: {pi_doc.rounded_total}")
                        return False
                    else:
                        budget_item.used_budget += pi_doc.rounded_total  # Update Used Budget
                        budget_item.balance_budget -= pi_doc.rounded_total  # Adjust Remaining Budget
                        budget_item.unpaid_purchase_invoice += pi_doc.rounded_total  # Adjust Remaining Budget
                        logging.debug(f"Direct PI W/O PO ,{pi_doc.budget_head}, {budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total}") 
                budget_updated_flag = True          
                break
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    #if not budget_updated_flag:
    #    frappe.throw(f"Budget not found for Budget Head{pi_doc.budget_head}")
    #    return False
    return True

@frappe.whitelist()
def revert_vcm_pi_budget_usage(pi_doc):
    PI_FLAG_WITH_PO = False
    logging.debug(f"in revert_vcm_pi_budget_usage 1 {pi_doc}")
    for item in pi_doc.items:
        if item.purchase_order:
            PI_FLAG_WITH_PO = True
            break  # Exit loop as soon as we find a linked PO
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{pi_doc.cost_center}"
    budget_doc = frappe.get_doc("VCM Budget", budget_name)
    if not budget_doc:
        frappe.throw(f"No budget found for Cost Center: {pi_doc.cost_center}")
        return False
    budget_updated_flag = False  
    for budget_item in budget_doc.get("budget_items") or []:
            logging.debug(f"in update_vcm_pi_budget_usage 2 {pi_doc.budget_head}")
            if budget_item.budget_head == pi_doc.budget_head:
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                if PI_FLAG_WITH_PO:  
                    budget_item.unpaid_purchase_order += pi_doc.rounded_total
                    budget_item.unpaid_purchase_invoice -= pi_doc.rounded_total  
                    logging.debug(f"PI With PO revert , {budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total}")
                else:
                    #reduce and check budget for PI without PO
                    budget_item.used_budget -= pi_doc.rounded_total  # Update Used Budget
                    budget_item.balance_budget += pi_doc.rounded_total  # Adjust Remaining Budget
                    budget_item.unpaid_purchase_invoice -= pi_doc.rounded_total  # Adjust Remaining Budget
                    logging.debug(f"Direct PI revert W/O PO , {budget_item.unpaid_purchase_invoice},{pi_doc.rounded_total}") 
                budget_updated_flag = True          
                break
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    #if not budget_updated_flag:
    #    frappe.throw(f"Budget not found for Budget Head{pi_doc.budget_head}")
    #    return False
    return True
    
def update_vcm_budget_on_payment_submit(pe_doc):
    """Update budget used when a Payment Entry is submitted."""
    # Ensure this is a Payment Entry affecting budget (Outgoing Payment)
    if pe_doc.payment_type != "Pay": 
        return
    # Fetch related Purchase Invoice
    PAYMENT_FLAG_WITH_PI = True
    purchase_invoice = pe_doc.references[0].reference_name if pe_doc.references else None
    logging.debug(f" in Payment Entry: {purchase_invoice} {PAYMENT_FLAG_WITH_PI}")
    if not purchase_invoice:
        PAYMENT_FLAG_WITH_PI = False
   
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{pe_doc.cost_center}"
    # Fetch budget settings based on Cost Center or Project
    budget_doc = frappe.get_doc("VCM Budget", budget_name)
    if not budget_doc:
        frappe.throw(f"No budget found for Cost Center: {pe_doc.cost_center}")
    # Calculate the paid amount impacting budget
    total_paid_amount = flt(pe_doc.paid_amount)
    budget_updated_flag = False  
    for budget_item in budget_doc.get("budget_items") or []:
            if budget_item.budget_head == pe_doc.budget_head:
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                if PAYMENT_FLAG_WITH_PI: 
                    logging.debug(f"in update_vcm_pE_budget_usage 3 {total_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.unpaid_purchase_invoice -= total_paid_amount  #Decrease PI amount
                    budget_item.paid_payment_entry += total_paid_amount  
                else:
                    #reduce and check budget for PI without PO
                    if total_paid_amount > budget_item.balance_budget:
                        frappe.throw(f"Budget Exceeded for {pe_doc.budget_head}, Balance: {budget_item.balance_budget}, Request: {total_paid_amount}")
                        return False
                    budget_item.used_budget += total_paid_amount  # Update Used Budget
                    budget_item.balance_budget -= total_paid_amount  # Adjust Remaining Budget
                    budget_item.paid_payment_entry += total_paid_amount 
                    logging.debug(f"update_vcm_ w/O PI pi_budget_usage6, {budget_item.budget_head},{total_paid_amount}")  
                budget_updated_flag = True          
                break 
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()

def revert_vcm_budget_on_payment_submit(pe_doc):
    """Update budget used when a Payment Entry is submitted."""
    # Ensure this is a Payment Entry affecting budget (Outgoing Payment)
    if pe_doc.payment_type != "Pay":
        return
    # Fetch related Purchase Invoice
    PAYMENT_FLAG_WITH_PI = True
    purchase_invoice = pe_doc.references[0].reference_name if pe_doc.references else None
    logging.debug(f" in Payment Entry: {purchase_invoice} {PAYMENT_FLAG_WITH_PI}")
    if not purchase_invoice:
        PAYMENT_FLAG_WITH_PI = False

    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{pe_doc.cost_center}"
    # Fetch budget settings based on Cost Center or Project
    budget_doc = frappe.get_doc("VCM Budget", budget_name)
    if not budget_doc:
        frappe.throw(f"No budget found for Cost Center: {pe_doc.cost_center}")

    # Calculate the paid amount impacting budget
    total_paid_amount = flt(pe_doc.paid_amount)

    budget_updated_flag = False  
    for budget_item in budget_doc.get("budget_items") or []:            
            if budget_item.budget_head == pe_doc.budget_head:
                # Reduce unpaid purchase order amount **only if the PI is linked to a PO**
                if PAYMENT_FLAG_WITH_PI: 
                    logging.debug(f"revert update_vcm_pE_budget_usage 3 {total_paid_amount},{budget_item.paid_payment_entry}")
                    budget_item.unpaid_purchase_invoice += total_paid_amount  #Decrease PI amount
                    budget_item.paid_payment_entry -= total_paid_amount  
                else:                    
                    budget_item.used_budget -= total_paid_amount  # Update Used Budget
                    budget_item.balance_budget += total_paid_amount  # Adjust Remaining Budget
                    budget_item.paid_payment_entry -= total_paid_amount 
                    logging.debug(f"revert_PE_without PI usage6, {budget_item.budget_head},{total_paid_amount}") 

                logging.debug(f"revert_PE_without PI_budget_usage7, {budget_item.budget_head},{total_paid_amount}")  
                budget_updated_flag = True          
                break 
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()


def update_vcm_budget_from_jv(jv_doc):    
    """
    Update Budget Used when a Journal Entry (JV) is submitted.
    """
    #child table of JV, as Cost center is not in JV form, we need to pull from child table
    for account in jv_doc.accounts:  
        logging.debug(f"update_vcm_JV 2 {account.budget_head},{account.cost_center},{account.debit}")
        if account.cost_center and account.debit > 0:  # Consider only debit entries for expenses
            vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
            budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{account.cost_center}"
            # Fetch budget settings based on Cost Center or Project
            budget_doc = frappe.get_doc("VCM Budget", budget_name)
            if not budget_doc:
                frappe.throw(f"No budget found for JV Cost Center: {account.cost_center}")                
            for budget_item in budget_doc.get("budget_items") or []: 
                logging.debug(f"update_vcm_JV 3 {budget_item.budget_head}, {account.budget_head},{budget_item.balance_budget}") 
                if budget_item.budget_head == account.budget_head:
                    if account.debit > budget_item.balance_budget:
                        frappe.throw(f"Budget Exceeded for JV {jv_doc.name}, Balance: {budget_item.balance_budget}, Request: {account.debit}")
                        return False
                    else:
                        #logging.debug(f"in update_vcm_po_budget_usage 3 {po_doc.rounded_total}")
                        budget_item.used_budget += account.debit
                        budget_item.balance_budget -= account.debit
                        budget_item.additional_je += account.debit
                        logging.debug(f"revert_JV budget_usage6, {budget_item.used_budget},{account.debit}")
                budget_updated_flag = True
    budget_doc.save()
    frappe.db.commit()

def reverse_vcm_budget_from_jv(jv_doc):
    """
    Update Budget Used when a Journal Entry (JV) is submitted.
    """
    #child table of JV, as Cost center is not in JV form, we need to pull from child table
    for account in jv_doc.accounts:  
        logging.debug(f"revert update_JV 2 {account.budget_head},{account.cost_center},{account.debit}")
        if account.cost_center and account.debit > 0:  # Consider only debit entries for expenses
            vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
            budget_name = f"{vcm_budget_settings.financial_year}-BUDGET-{account.cost_center}"
            # Fetch budget settings based on Cost Center or Project
            budget_doc = frappe.get_doc("VCM Budget", budget_name)
            if not budget_doc:
                frappe.throw(f"No budget found for JV Cost Center: {account.cost_center}")
            for budget_item in budget_doc.get("budget_items") or []:
                logging.debug(f"update_vcm_JV 3 {budget_item.budget_head}, {account.budget_head},{budget_item.balance_budget}") 
                if budget_item.budget_head == account.budget_head:
                    if account.debit > budget_item.balance_budget:
                        frappe.throw(f"Budget Exceeded for JV {jv_doc.name}, Balance: {budget_item.balance_budget}, Request: {account.debit}")
                        return False
                    #logging.debug(f"in update_vcm_po_budget_usage 3 {po_doc.rounded_total}")
                    budget_item.used_budget -= account.debit
                    budget_item.balance_budget += account.debit
                    budget_item.additional_je -= account.debit
                    logging.debug(f"revert_JV budget_usage6, {budget_item.used_budget},{account.debit}")
                budget_updated_flag = True
    budget_doc.save()
    frappe.db.commit()
    #frappe.msgprint(f"Updated Budget Used for Cost Center: {account.cost_center}")
                
    