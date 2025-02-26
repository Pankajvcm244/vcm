import frappe
from frappe.utils import flt
import logging
logging.basicConfig(level=logging.DEBUG)

@frappe.whitelist()
def update_vcm_po_budget_usage(po_doc):
    """ Updates the used budget in VCM Budget when a PO is submitted """
    budget_name = f"2024-2025-BUDGET-{po_doc.cost_center}"
    budget_doc = frappe.get_doc("VCM Budget", budget_name)
    if not budget_doc:
        #frappe.throw(f"Budget not found for {po_doc.name}, {po_doc.cost_center}")
        return False
    budget_updated_flag = False
    for budget_item in budget_doc.get("budget_items") or []:
        logging.debug(f"in update_vcm_po_budget_usage 2 {po_doc.budget_head}")
        if budget_item.budget_head == po_doc.budget_head:
            if po_doc.rounded_total > budget_item.balance_budget:
                frappe.throw(f"Budget Exceeded for {po_doc.budget_head}")
                return False
            #logging.debug(f"in update_vcm_po_budget_usage 3 {po_doc.rounded_total}")
            budget_item.used_budget += po_doc.rounded_total  # Update Used Budget
            budget_item.balance_budget -= po_doc.rounded_total  # Adjust Remaining Budget
            budget_item.unpaid_purchase_order += po_doc.rounded_total  # Adjust Remaining Budget
            budget_doc.total_unpaid_purchase_invoice += po_doc.rounded_total
            #logging.debug(f"update_vcm_po_budget_usage6, {budget_item.budget_head},{po_doc.rounded_total}")  
            budget_updated_flag = True           
            break
    # Save and commit changes
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    if not budget_updated_flag:
        frappe.throw(f"Budget not found for Budget Head{po_doc.budget_head}")
        return False
    return True

@frappe.whitelist()
def revert_vcm_po_budget_usage(po_doc):
    """ Reverts budget usage when PO is canceled """
    budget_name = f"2024-2025-BUDGET-{po_doc.cost_center}"
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
            budget_doc.total_unpaid_purchase_invoice -= po_doc.rounded_total
            #logging.debug(f"revert vcm_po_budget -1, {budget_item.budget_head},{po_doc.rounded_total}")
            budget_updated_flag = True
            break
    budget_doc.save(ignore_permissions=True)
    frappe.db.commit()
    if not budget_updated_flag:
        frappe.throw(f"Budget Head not found for {po_doc.budget_head}")
        return False
    return True

@frappe.whitelist()
def update_vcm_PI_budget_usage(pi_doc_id):
    pass

@frappe.whitelist()
def update_vcm_expense_budget_usage(expense_doc_id):
    pass

def update_budget_from_jv(doc, method):
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    if vcm_budget_settings.jv_budget_enabled == "Yes":
        """
        Update Budget Used when a Journal Entry (JV) is submitted.
        """
        for account in doc.accounts:
            if account.cost_center and account.debit > 0:  # Consider only debit entries for expenses
                budget = frappe.get_value("VCM Budget", 
                                        {"cost_center": account.cost_center, 
                                        "fiscal_year": frappe.defaults.get_user_default("fiscal_year")},
                                        "name")

                if budget:
                    budget_doc = frappe.get_doc("VCM Budget", budget)
                    for budget_account in budget_doc.accounts:
                        if budget_account.account == account.account:
                            budget_account.budget_used = flt(budget_account.budget_used) + flt(account.debit)
                            budget_doc.save()
                            frappe.db.commit()
                            frappe.msgprint(f"Updated Budget Used for Cost Center: {account.cost_center}")

def reverse_budget_from_jv(doc, method):
    vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
    if vcm_budget_settings.jv_budget_enabled == "Yes":
        """
        Reverse Budget Used when a Journal Entry (JV) is canceled.
        """
        for account in doc.accounts:
            if account.cost_center and account.debit > 0:
                budget = frappe.get_value("VCM Budget", 
                                        {"cost_center": account.cost_center, 
                                        "fiscal_year": frappe.defaults.get_user_default("fiscal_year")},
                                        "name")

                if budget:
                    budget_doc = frappe.get_doc("VCM Budget", budget)
                    for budget_account in budget_doc.accounts:
                        if budget_account.account == account.account:
                            budget_account.budget_used = max(0, flt(budget_account.budget_used) - flt(account.debit))
                            budget_doc.save()
                            frappe.db.commit()
                            frappe.msgprint(f"Reversed Budget Used for Cost Center: {account.cost_center}")