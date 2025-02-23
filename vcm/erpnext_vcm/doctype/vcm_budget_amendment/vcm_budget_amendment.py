# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

import logging
logging.basicConfig(level=logging.DEBUG)

class VCMBudgetAmendment(Document):		
	def on_submit(self):  # Pankaj change it later to on_submit
		logging.debug(f"in VCMBudgetAmendment on_submit  {self}  ")
        # Ensure the Budget Amendment is linked to a valid Budget document
		budget_exists = frappe.db.exists("VCM Budget", {"company": self.company, "fiscal_year": self.fiscal_year, "cost_center": self.cost_center})
		if not budget_exists:
			frappe.throw("Budget does not exist for {self.fiscal_year}-BUDGET-{self.cost_center} .")

		budget_name = f"{self.fiscal_year}-BUDGET-{self.cost_center}"		
        # Fetch the Budget document 
		budget_doc = frappe.get_doc("VCM Budget", budget_name)
		logging.debug(f"Budget Amend-1 Name:  {budget_name}, {budget_doc}") 		
	
        # Loop over each item in the Budget Amendment child table
		for amend_item in self.get("budget_amendment_items") or []:
            # Attempt to locate the corresponding child record in the Budget doc
			logging.debug(f"Budget Amend-2  {amend_item} ")
			updated = False
			for budget_item in budget_doc.get("budget_items") or []:
				logging.debug(f"Budget Amend-3  {budget_item}, {budget_item.budget_head}, {amend_item.budget_head} ")
                # Use a unique identifier for matching (e.g., budget_head)
				if budget_item.budget_head == amend_item.budget_head:
                    # Update desired fields. For example:
					budget_item.current_budget += amend_item.proposed_amendment
					budget_item.amended_till_now += amend_item.proposed_amendment
					budget_item.balance_budget += amend_item.proposed_amendment					
					updated = True
					logging.debug(f"in Budget Amend  -1  {budget_item.current_budget}, {budget_item.amended_till_now},	{budget_item.balance_budget}, {budget_item.current_budget}") 
					break
            
            # Optional: notify if a matching Budget Item was not found
			if not updated:
				frappe.msgprint(f"No matching Budget Item found for {amend_item.budget_head}")

        # Save the updated Budget document so the changes persist
		budget_doc.save(ignore_permissions=True)
		logging.debug(f"in Budget Amend  -10 save  ")
		frappe.db.commit()
		logging.debug(f"in Budget Amend  -10 dbcommit  ")
