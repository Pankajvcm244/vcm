import frappe
from frappe.utils import flt
import logging
logging.basicConfig(level=logging.DEBUG)


#def update_vcm_po_budget_usage(po_doc):
def update_PO_Budget():
# bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.VCMBudgetTrigger.update_PO_Budget    
    filters = {} 
    vcm_company = "HARE KRISHNA MOVEMENT VRINDAVAN"
    vcm_location = "VRN"
    vcm_fiscal_year = "2025-2026"
    vcm_cost_center = "RAM NAVAMI - HKMV"
    vcm_budget_head = "Food"


    conditions = ["docstatus = 1"]  # Only consider approved POs
    """ Updates the used budget in VCM Budget when a PO is submitted """
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {"company": vcm_company,"location": vcm_location,"fiscal_year":vcm_fiscal_year,"cost_center":vcm_cost_center,"docstatus":1},
        "name")
    logging.debug(f"in update_PO_Budget 1: {vcm_company}, {vcm_location}, {vcm_fiscal_year}, {vcm_cost_center}, {vcm_budget_head}")
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no budget for this cost center then just move on
        logging.debug(f"in validate_vcm_po No budget exists  {budget_name}")
        return 0 
    filters = {
        "cost_center": vcm_cost_center,
        "company": vcm_company,
        "location": vcm_location,
        "budget_head": vcm_budget_head,
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
        if budget_item.budget_head == vcm_budget_head:        
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