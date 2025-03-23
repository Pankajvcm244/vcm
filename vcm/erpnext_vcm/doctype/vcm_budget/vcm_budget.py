# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import logging
logging.basicConfig(level=logging.DEBUG)

class VCMBudget(Document):

    def autoname(self):
        if self.cost_center and self.company and self.fiscal_year:
            company_name = frappe.get_doc("Company", self.company)
            company_abbr = company_name.abbr
            self.name = f"{company_abbr}-{self.fiscal_year}-{self.location}-{self.cost_center}"

    # def before_save(self):
    #     if self.is_new():  # Ensures name change only on creation
    #         if self.cost_center and self.company and self.location and self.fiscal_year:
    #             company_name = frappe.get_doc("Company", self.company)
    #             company_abbr = company_name.abbr
    #             new_name = f"{company_abbr}-{self.fiscal_year}-{self.location}-{self.cost_center}"
    #             if not frappe.db.exists("VCM Budget", new_name):
    #                 self.name = new_name
    #             else:
    #                 frappe.throw(f"A VCM Budget with name {new_name} already exists.")
    def on_update(self):
            # Skip addiition or deletion validation for new documents
            # Fetch existing document from the database before modifications
            old_doc = frappe.get_doc("VCM Budget", self.name)

            # Extract budget item names before and after modification
            old_budget_items = {item.name for item in old_doc.get("budget_items") or []}
            new_budget_items = {item.name for item in self.get("budget_items") or []}

            # Identify deleted items (if present in old but not in new)
            deleted_items = old_budget_items - new_budget_items

            # Check if document is submitted and if any row is deleted
            if self.docstatus == 1 and deleted_items:
                frappe.throw("You cannot delete Budget Items after submission, but you can add new ones.")


    def validate(self):
        #logging.debug(f"in budget validate-1   ")
        # Check if budget already exists for new entry
        if self.is_new():
            #logging.debug(f"in budget validate-ID {self.name} , {self.total_amount}  ")
            if self.total_amount == 0:
                # This is new Budget creation as after this Orifgional amount will be non-zero              
                budget_exists = frappe.db.exists("VCM Budget", {
                    "company": self.company, 
                    "location": self.location,
                    "fiscal_year": self.fiscal_year,
                    "cost_center": self.cost_center
                    })
                if budget_exists:
                    frappe.throw(f"Budget exists for {self.company}-{self.fiscal_year}-{self.location}-{self.cost_center}")
               
        is_group = frappe.get_value("Cost Center", self.cost_center, "is_group")
        if is_group:
                frappe.throw(f"Cost Center {self.cost_center} is a folder. Please select a child Cost Center.")
        
        # we will check Budget Head in Child table row below
        
        budget_heads = set()
        for row in self.budget_items:
            # Check for duplicate budget heads
            if row.budget_head in budget_heads:
                frappe.throw(f"Duplicate Budget Head: {row.budget_head}. Each Budget Head must be unique.")

            is_head_group = frappe.get_value("Budget Head", row.budget_head, "is_group")
            if is_head_group:
                frappe.throw(f"Budget Head '{row.budget_head}' is a folder. Please select a child Budget Head.")
            budget_heads.add(row.budget_head)

           

@frappe.whitelist()
def get_budget_items(company, fiscal_year, location, cost_center):
    # Check if a budget exists
    #logging.debug(f"in get_budget_items-1   {company}, {fiscal_year}, {cost_center}  ")
    budget_exists = frappe.db.exists("VCM Budget", {"company": company, "location": location,"fiscal_year": fiscal_year, "cost_center": cost_center})
    if not budget_exists:
        return []  # Return an empty list if no budget found

    # Fetch all budget items for the given company and fiscal year
    budget_items = frappe.db.sql("""
        SELECT bci.budget_head, bci.original_amount, bci.amended_till_now, bci.current_budget, bci.used_budget, bci.balance_budget
        FROM `tabVCM Budget` b
        JOIN `tabVCM Budget Child Table` bci ON b.name = bci.parent
        WHERE b.company = %s AND b.location = %s AND b.fiscal_year = %s AND b.cost_center = %s
        """, (company, location, fiscal_year, cost_center), as_dict=True)
    #logging.debug(f"in get_budget_items-2   {budget_items}  ")
    return budget_items

