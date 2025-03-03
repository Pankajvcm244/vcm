# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.naming import getseries
from frappe.model.document import Document

import logging
logging.basicConfig(level=logging.DEBUG)

class VCMBudgetAmendment(Document):	
	def autoname(self):
		prefix = f"{self.fiscal_year}-BUDGET-AMEND-{self.cost_center}-"         
		self.name = prefix + getseries(prefix, 4)


	def on_submit(self):  
		logging.debug(f"in VCMBudgetAmendment on_submit  {self}  ")
        # Ensure the Budget Amendment is linked to a valid Budget document
		budget_exists = frappe.db.exists("VCM Budget", {
				"company": self.company, 
				"fiscal_year": self.fiscal_year,
					"cost_center": self.cost_center
					})
		if not budget_exists:
			frappe.throw("Budget does not exist for {self.fiscal_year}-BUDGET-{self.cost_center} .")

		budget_name = f"{self.fiscal_year}-BUDGET-{self.cost_center}"		
        # Fetch the Budget document 
		budget_doc = frappe.get_doc("VCM Budget", budget_name)
		#logging.debug(f"Budget Amend-1 Name:  {budget_name}, {budget_doc}") 		
	
        # Loop over each item in the Budget Amendment child table
		for amend_item in self.get("budget_amendment_items") or []:
            #logging.debug(f"Budget Amend-2  {amend_item} ")
			updated = False
		
			# Attempt to locate the corresponding child record in the Budget doc
			for budget_item in budget_doc.get("budget_items") or []:
				logging.debug(f"Budget Amend-3  {budget_item}, {budget_item.budget_head}, {amend_item.budget_head} ")
                # Use a unique identifier for matching (e.g., budget_head)
				if (budget_item.budget_head == amend_item.budget_head) and (amend_item.proposed_amendment != 0):
					#logging.debug(f"Budget Amend-1 {amend_item.proposed_amendment}")
                    # Update desired fields. For example:
					budget_item.current_budget += amend_item.proposed_amendment
					budget_item.amended_till_now += amend_item.proposed_amendment
					budget_item.balance_budget = budget_item.current_budget - budget_item.used_budget
					#update budget amendment child table to sync with Budget child table
					amend_item.current_budget = budget_item.current_budget
					amend_item.amended_till_now = budget_item.amended_till_now
					amend_item.balance_budget = budget_item.balance_budget
					budget_item.db_update() # Save individual Budget child row to DB
					amend_item.db_update() # Save amendment child table also
					logging.debug(f" Budget Amend-1-1 {budget_item.current_budget},{amend_item.proposed_amendment},{budget_item.balance_budget}")			
					updated = True
					break   

            # Optional: notify if a matching Budget Item was not found
			if not updated:
				#existing_heads = {item.budget_head for item in budget_doc.get("budget_items") or []}
				#if amend_item.budget_head not in existing_heads:
				#	logging.debug(f" Budget Amend-4 {existing_heads},{amend_item.budget_head}") 
				#	budget_doc.append("budget_items", {
				#		"budget_head": amend_item.budget_head,
				#		"current_budget": amend_item.proposed_amendment,
				#		"amended_till_now": amend_item.proposed_amendment,
				#		"balance_budget": amend_item.proposed_amendment,  # Assuming no used_budget yet
				#		"proposed_by": self.proposed_by
				#	})

				frappe.msgprint(f"New Budget Head added: {amend_item.budget_head}, {amend_item.proposed_amendment}")

        # Save the updated Budget document so the changes persist
		try:
			budget_doc.save(ignore_permissions=True)
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Budget Amendment Save Error: {str(e)}")
			logging.error(f"Error in budget amendment: {str(e)}")
