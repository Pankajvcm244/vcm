# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import logging
logging.basicConfig(level=logging.DEBUG)

class VCMBudget(Document):

    def autoname(self):
        if self.cost_center and self.company and self.fiscal_year:
            self.name = f"{self.fiscal_year}-BUDGET-{self.cost_center}"

    def before_save(self):
        if self.is_new():  # Ensures name change only on creation
            if self.cost_center and self.company and self.fiscal_year:
                new_name = f"{self.fiscal_year}-BUDGET-{self.cost_center}"

                if not frappe.db.exists("VCM Budget", new_name):
                    self.name = new_name
                else:
                    frappe.throw(f"A VCM Budget with name {new_name} already exists.")



@frappe.whitelist()
def get_budget_items(company, fiscal_year, cost_center):
    # Check if a budget exists
    #logging.debug(f"in get_budget_items-1   {company}, {fiscal_year}, {cost_center}  ")
    budget_exists = frappe.db.exists("VCM Budget", {"company": company, "fiscal_year": fiscal_year, "cost_center": cost_center})
    if not budget_exists:
        return []  # Return an empty list if no budget found

    # Fetch all budget items for the given company and fiscal year
    budget_items = frappe.db.sql("""
        SELECT bci.budget_head, bci.original_amount, bci.amended_till_now,bci.current_budget, bci.used_budget, bci.balance_budget
        FROM `tabVCM Budget` b
        JOIN `tabVCM Budget Child Table` bci ON b.name = bci.parent
        WHERE b.company = %s AND b.fiscal_year = %s AND b.cost_center = %s
        """, (company, fiscal_year, cost_center), as_dict=True)
    #logging.debug(f"in get_budget_items-2   {budget_items}  ")
    return budget_items

