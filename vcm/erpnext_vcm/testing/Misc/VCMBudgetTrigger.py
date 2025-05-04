import frappe
from frappe.utils import flt
import logging
logging.basicConfig(level=logging.DEBUG)


#def update_vcm_po_budget_usage(po_doc):
@frappe.whitelist()
def update_PO_Budget_new(company, location, fiscal_year, cost_center, budget_head):
#def update_PO_Budget(): 
# *****DONT RUN FOR HERE FOR ALL , USE Budget AUTO Update File  
# bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.VCMBudgetTrigger.update_PO_Budget_new    
    filters = {} 
    # vcm_company = "HARE KRISHNA MOVEMENT VRINDAVAN"
    # vcm_location = "NOI"
    # vcm_fiscal_year = "2025-2026"
    # vcm_cost_center = "YOGA FOR HAPPINESS - HKMV"
    # vcm_budget_head = "Food"
    vcm_company = company
    vcm_location = location
    vcm_fiscal_year = fiscal_year
    vcm_cost_center = cost_center
    vcm_budget_head = budget_head
    conditions = ["docstatus = 1"]  # Only consider approved POs
    """ Updates the used budget in VCM Budget when a PO is submitted """
    
    # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {"company": vcm_company,"location": vcm_location,"fiscal_year":vcm_fiscal_year,"cost_center":vcm_cost_center,"docstatus":1},
        "name")
    #logging.debug(f"in update_PO_Budget 1: {vcm_company}, {vcm_location}, {vcm_fiscal_year}, {vcm_cost_center}, {vcm_budget_head}")
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no budget for this cost center then just move on
        logging.debug(f"in validate_vcm_po No budget exists  {budget_name}, Cost Center {vcm_cost_center}, LOC {vcm_location}")
        return 0 
    filters = {
        "cost_center": vcm_cost_center,
        "company": vcm_company,
        "location": vcm_location,
        "fiscal_year": fiscal_year,
        "budget_head": vcm_budget_head,
        "from_date": "2025-04-01",  # Always check from April 1st
    }
    #logging.debug(f"in update_vcm_po_budget_usage 2 {po_doc.cost_center}, {po_doc.company},{po_doc.location} , {po_doc.budget_head}")
    date_field = "transaction_date"
    if filters["cost_center"]:
        conditions.append("cost_center = %(cost_center)s")
    if filters["company"]:
        conditions.append("company = %(company)s")
    if filters["location"]:
        conditions.append("location = %(location)s")
    if filters["fiscal_year"]:
        conditions.append("fiscal_year = %(fiscal_year)s")
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
    #logging.debug(f"in get po 2 {result} {total_used_budget}")
    total_po_amount = result[0].get("total_used_budget", 0) if result else 0
    
    for budget_item in budget_doc.get("budget_items") or []:
        budget_updated_flag = True
        #logging.debug(f"in update_vcm_po_budget_usage 2 {vcm_budget_head}")
        if budget_item.budget_head == vcm_budget_head:  
            budget_updated_flag = False     
            budget_item.unpaid_purchase_order = total_po_amount or 0 # Adjust Remaining Budget
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
            
            frappe.db.sql("""
                UPDATE `tabVCM Budget Child Table`
                SET unpaid_purchase_order = %s,
                    used_budget = %s,
                    balance_budget = %s
                WHERE name = %s
            """, (budget_item.unpaid_purchase_order, budget_item.used_budget, budget_item.balance_budget, budget_item.name))        
            frappe.db.commit()  
            break 

    if budget_updated_flag == True:
        # If the budget head does not match, log a message
        logging.debug(f"******* PO Budget head mismatch: NOT FOUND {vcm_budget_head}, {vcm_cost_center}, {vcm_company}, {vcm_location}, {fiscal_year}")  
    # Save and commit changes    
    # budget_doc.save(ignore_permissions=True)
    # frappe.db.commit()    
    return True


def update_PI_Budget(company, location, fiscal_year, cost_center, budget_head):
    #"Updated 4028, 0 PO.\n\n Errors: []."
    #"Updated 4086, 0 PO.\n\n Errors: []." 17/4/2024
    #*****DONT RUN FOR HERE FOR ALL , USE Budget AUTO Update File
    # bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.VCMBudgetTrigger.update_PI_Budget    
    filters = {}   
    alias = "pi_doc" 
    conditions = [
        f"{alias}.docstatus = 1", 
        f"{alias}.is_return = 0", 
        "(pii.purchase_order IS NULL OR pii.purchase_order = '')"
        ]  # Approved PIs without PO
    
    # vcm_company = "HARE KRISHNA MOVEMENT VRINDAVAN"
    # vcm_location = "VRN"
    # vcm_fiscal_year = "2025-2026"
    # vcm_cost_center = "REGIONAL PUBLIC RELATIONS - HKMV"
    # vcm_budget_head = "Miscellaneous"
    budget_updated_flag = True
    vcm_company = company
    vcm_location = location
    vcm_fiscal_year = fiscal_year
    vcm_cost_center = cost_center
    vcm_budget_head = budget_head

    
    """ Updates the used budget in VCM Budget when a PO is submitted """
    
    # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {
            "company": vcm_company,
            "location": vcm_location,
            "fiscal_year":vcm_fiscal_year,
            "cost_center":vcm_cost_center,
            "docstatus":1
        },
        "name"
    )
    #logging.debug(f"in update_PI_Budget 1: {vcm_company}, {vcm_location}, {vcm_fiscal_year}, {vcm_cost_center}, {vcm_budget_head}")
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        #If there is no budget for this cost center then just move on
        logging.debug(f"in PI validate_vcm_po No budget exists  {budget_name}, Cost Center {vcm_cost_center}, LOC {vcm_location}")
        return 0 
    filters = {
        "cost_center": vcm_cost_center,
        "company": vcm_company,
        "location": vcm_location,
        "fiscal_year": vcm_fiscal_year,
        "budget_head": vcm_budget_head,
        "from_date": "2025-04-01",  # Always check from April 1st
    }
    #logging.debug(f"in update_vcm_po_budget_usage 2 {po_doc.cost_center}, {po_doc.company},{po_doc.location} , {po_doc.budget_head}")
    date_field = "posting_date"
    if filters.get("cost_center"):
        conditions.append(f"{alias}.cost_center = %(cost_center)s")
    if filters.get("company"):
        conditions.append(f"{alias}.company = %(company)s")
    if filters.get("location"):
        conditions.append(f"{alias}.location = %(location)s")
    if filters.get("fiscal_year"):
        conditions.append(f"{alias}.fiscal_year = %(fiscal_year)s")
    if filters.get("budget_head"):
        conditions.append(f"{alias}.budget_head = %(budget_head)s")
    
   # Check all PIs from April 1st onward
    conditions.append(f"{alias}.{date_field} >= %(from_date)s")

    selected_table = "tabPurchase Invoice"
    amount_field = "grand_total"

    condition_string = " AND ".join(conditions)
    #logging.debug(f"in update_vcm_pi_budget 1 {condition_string}")
    query = f"""
    SELECT
        SUM(pi_amount) AS total_used_budget
    FROM (
        SELECT DISTINCT
            {alias}.name,
            {alias}.{amount_field} AS pi_amount
        FROM `{selected_table}` {alias}
        LEFT JOIN `tabPurchase Invoice Item` pii ON pii.parent = {alias}.name
        WHERE {condition_string}
    ) AS grouped
    """

    result = frappe.db.sql(query, filters, as_dict=True)
    #logging.debug(f"in get pi usage: {result}")
    total_pi_amount = result[0].get("total_used_budget", 0) if result else 0
    #logging.debug(f"in update_vcm_pi_budget 2 {total_pi_amount}")

    for budget_item in budget_doc.get("budget_items") or []:
        if budget_item.budget_head == vcm_budget_head: 
            budget_updated_flag = False       
            budget_item.unpaid_purchase_invoice = total_pi_amount or 0  # Adjust Remaining Budget
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
            frappe.db.sql("""
                UPDATE `tabVCM Budget Child Table`
                SET unpaid_purchase_invoice = %s,
                    used_budget = %s,
                    balance_budget = %s
                WHERE name = %s
            """, (budget_item.unpaid_purchase_invoice, budget_item.used_budget, budget_item.balance_budget, budget_item.name))        
            frappe.db.commit()  
            break   
    if budget_updated_flag:
        # If the budget head does not match, log a message
        logging.debug(f"******* PI Budget head mismatch: NOT FOUND {vcm_budget_head}, {vcm_cost_center}, {vcm_company}, {vcm_location}, {fiscal_year}")  
    # budget_doc.save(ignore_permissions=True)
    # frappe.db.commit()    
    return True


def update_PE_Budget(company, location, fiscal_year, cost_center, budget_head):
#def update_PE_Budget():
    # *****DONT RUN FOR HERE FOR ALL , USE Budget AUTO Update File
    # bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.VCMBudgetTrigger.update_PE_Budget    

    filters = {}   
    alias = "pe_doc" 
    conditions = [
        f"{alias}.docstatus = 1",  # Submitted Payment Entries only
        f"{alias}.payment_type = 'Pay'", # Only outgoing payments
         f"{alias}.posting_date >= %(from_date)s"  
    ]
    
    # vcm_company = "HARE KRISHNA MOVEMENT VRINDAVAN"
    # vcm_location = "VRN"
    # vcm_fiscal_year = "2025-2026"
    # vcm_cost_center = "GRIHASTHA ASHRAM - HKMV"
    # vcm_budget_head = "Land/Building Rentals"
    vcm_company = company
    vcm_location = location
    vcm_fiscal_year = fiscal_year
    vcm_cost_center = cost_center
    vcm_budget_head = budget_head
    budget_updated_flag = True    
    
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {
            "company": vcm_company,
            "location": vcm_location,
            "fiscal_year": vcm_fiscal_year,
            "cost_center": vcm_cost_center,
            "docstatus": 1
        },
        "name"
    )
    
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        # If there is no budget for this cost center then just move on
        logging.debug(f"in PE validate_vcm_po No budget exists  {budget_name}, Cost Center {vcm_cost_center}, LOC {vcm_location}")
        return 0 

    filters = {
        "cost_center": vcm_cost_center,
        "company": vcm_company,
        "location": vcm_location,
        "fiscal_year": vcm_fiscal_year,
        "budget_head": vcm_budget_head,
        "from_date": "2025-04-01",  # Always check from April 1st
    }

    date_field = "posting_date"
    if filters.get("cost_center"):
        conditions.append(f"{alias}.cost_center = %(cost_center)s")
    if filters.get("company"):
        conditions.append(f"{alias}.company = %(company)s")
    if filters.get("location"):
        conditions.append(f"{alias}.location = %(location)s")
    if filters.get("fiscal_year"):
        conditions.append(f"{alias}.fiscal_year = %(fiscal_year)s")
    if filters.get("budget_head"):
        conditions.append(f"{alias}.budget_head = %(budget_head)s")
    
    # Exclude PEs that have references to Purchase Orders or Purchase Invoices
    conditions.append(f"""
        NOT EXISTS (
            SELECT 1 FROM `tabPayment Entry Reference` per
            WHERE per.parent = {alias}.name
              AND per.reference_doctype IN ('Purchase Order', 'Purchase Invoice')
        )
    """)

    selected_table = "tabPayment Entry"
    amount_field = "paid_amount"  # or use `base_paid_amount` for consistency
    condition_string = " AND ".join(conditions)
    #logging.debug(f"in update_PE_Budget query condition: {condition_string}")
    
    query = f"""
        SELECT
            SUM({amount_field}) AS total_used_budget
        FROM `{selected_table}` {alias}
        WHERE {condition_string}
    """

    result = frappe.db.sql(query, filters, as_dict=True)
    #logging.debug(f"Payment Entry usage result: {result}")
    
    total_pe_amount = result[0].get("total_used_budget", 0) if result else 0
    #logging.debug(f"Total paid amount for PE: {total_pe_amount}, Budget Head: {vcm_budget_head}")

    for budget_item in budget_doc.get("budget_items") or []:
        if budget_item.budget_head == vcm_budget_head:
            budget_updated_flag = False
            budget_item.paid_payment_entry = total_pe_amount or 0 
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
            frappe.db.sql("""
                UPDATE `tabVCM Budget Child Table`
                SET paid_payment_entry = %s,
                    used_budget = %s,
                    balance_budget = %s
                WHERE name = %s
            """, (budget_item.paid_payment_entry, budget_item.used_budget, budget_item.balance_budget, budget_item.name))        
            frappe.db.commit() 
            break

    if budget_updated_flag:
        logging.debug(f"******* PE Budget head mismatch: NOT FOUND {vcm_budget_head}, {vcm_cost_center}, {vcm_company}, {vcm_location}, {fiscal_year}")  
    # budget_doc.save(ignore_permissions=True)
    # frappe.db.commit()
    return True

def update_JV_Budget(company, location, fiscal_year, cost_center, budget_head):
#def update_JV_Budget():
    # *****DONT RUN FOR HERE FOR ALL , USE Budget AUTO Update File
    # bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.VCMBudgetTrigger.update_JV_Budget    

    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")  
    fiscal_start = "2025-04-01"  # Hardcoded fiscal year start
    alias = "je" 
    filters = {}  
    # vcm_company = "HARE KRISHNA MOVEMENT VRINDAVAN"
    # vcm_location = "VRN"
    # vcm_fiscal_year = "2025-2026"
    # vcm_cost_center = "ONLINE COMMUNICATIONS - HKMV"
    # vcm_budget_head = "Vehicle Maintenance"
    vcm_company = company
    vcm_location = location
    vcm_fiscal_year = fiscal_year
    vcm_cost_center = cost_center
    vcm_budget_head = budget_head
    budget_updated_flag = True    
    
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {
            "company": vcm_company,
            "location": vcm_location,
            "fiscal_year": vcm_fiscal_year,
            "cost_center": vcm_cost_center,
            "docstatus": 1
        },
        "name"
    )
    
    if frappe.db.exists("VCM Budget", budget_name):
        budget_doc = frappe.get_doc("VCM Budget", budget_name)
    else:
        # If there is no budget for this cost center then just move on
        logging.debug(f"in JV validate_vcm_po No budget exists  {budget_name}, Cost Center {vcm_cost_center}, LOC {vcm_location}")
        return 0  
    filters = {
        "cost_center": vcm_cost_center,
        "company": vcm_company,
        "location": vcm_location,
        "fiscal_year": vcm_fiscal_year,
        "budget_head": vcm_budget_head,
        "from_date": fiscal_start,  # Always check from April 1st
    }
    date_field = "posting_date"

    conditions = [
        f"{alias}.docstatus = 1",
        f"{alias}.posting_date >= %(from_date)s",
        f"{alias}.company = %(company)s",
        f"jea.cost_center = %(cost_center)s",
        f"jea.location = %(location)s",
        f"jea.fiscal_year = %(fiscal_year)s",
        f"jea.budget_head = %(budget_head)s",
        "acc.root_type = 'Expense'",
    ]
    conditions.append("""
        (
            jea.reference_type IS NULL 
            OR jea.reference_type NOT IN ('Purchase Order', 'Purchase Invoice')
        )
    """)
    condition_string = " AND ".join(conditions)
    selected_table = "tabJournal Entry"
    #amount_field = "total_debit"  # or use `base_paid_amount` for consistency      
    query = f"""
                SELECT
                    {alias}.name,                    
                    SUM(jea.debit - jea.credit) AS net_budget_change,
                    CASE 
                        WHEN SUM(jea.debit) > SUM(jea.credit) THEN 'Debit'
                        WHEN SUM(jea.credit) > SUM(jea.debit) THEN 'Credit'
                        ELSE 'Neutral'
                    END AS entry_type,            
                    acc.root_type AS root_type
                FROM `{selected_table}` {alias}
                LEFT JOIN `tabJournal Entry Account` jea ON jea.parent = {alias}.name
                LEFT JOIN `tabAccount` acc ON acc.name = jea.account
                WHERE {condition_string}                
            """
    result = frappe.db.sql(query, filters, as_dict=True)
    #logging.debug(f"Payment Entry usage result: {result}")    
    total_jv_amount = result[0].get("net_budget_change", 0) or 0 if result else 0
    #logging.debug(f"Total paid amount for JV: {total_jv_amount}, Budget Head: {vcm_budget_head}")
    for budget_item in budget_doc.get("budget_items") or []:
        if budget_item.budget_head == vcm_budget_head:
            budget_updated_flag = False
            budget_item.additional_je = total_jv_amount or 0 
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
            frappe.db.sql("""
                UPDATE `tabVCM Budget Child Table`
                SET additional_je = %s,
                    used_budget = %s,
                    balance_budget = %s
                WHERE name = %s
            """, (total_jv_amount, budget_item.used_budget, budget_item.balance_budget, budget_item.name))        
            frappe.db.commit()
            break
    if budget_updated_flag:
        logging.debug(f"******* JV Budget head mismatch: NOT FOUND {vcm_budget_head}, {vcm_cost_center}, {vcm_company}, {vcm_location}, {fiscal_year}")  
    # budget_doc.save(ignore_permissions=True)
    # frappe.db.commit()
    return True