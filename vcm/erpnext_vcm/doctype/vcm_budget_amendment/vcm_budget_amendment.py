# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.naming import getseries
from frappe.model.document import Document

import logging
logging.basicConfig(level=logging.DEBUG)
from frappe.model.naming import getseries
import datetime

class VCMBudgetAmendment(Document):	
	def autoname(self):
		now = datetime.datetime.now()
		month = now.strftime("%m")
		year = now.strftime("%y")
		company_name = frappe.get_doc("Company", self.company)
		company_abbr = company_name.abbr
		# Ensure cost center is only 10 characters
		cost_center_trimmed = self.cost_center[:10] if self.cost_center else ""
		prefix = f"A-{company_abbr}-{self.location}-{cost_center_trimmed}-{year}{month}-"         
		self.name = prefix + getseries(prefix, 4)

	def validate(self):
		logging.debug(f"in VCMBudgetAmendment validate ")
        # Check if budget_head is a folder (is_group = 1)
		is_group = frappe.get_value("Cost Center", self.cost_center, "is_group")
		if is_group:
				frappe.throw(f"Cost Center'{self.cost_center}' is a folder. Please select a child Cost Center.")			

		budget_exists = frappe.db.exists("VCM Budget", {
			"company": self.company, 
			"location": self.location,
			"fiscal_year": self.fiscal_year,
			"cost_center": self.cost_center
			})
		if not budget_exists:
			frappe.throw(f"Budget does not exist for {self.company}-{self.fiscal_year}-{self.location}-{self.cost_center}")
		
		budget_heads = set()
		for row in self.budget_amendment_items:
			# Check for duplicate budget heads
			if row.budget_head in budget_heads:
				frappe.throw(f"Duplicate Budget Head: {row.budget_head}. Each Budget Head must be unique.")

			is_head_group = frappe.get_value("Budget Head", row.budget_head, "is_group")
			if is_head_group:
				frappe.throw(f"Budget Head {row.budget_head} is a folder. Please select a child Budget Head.")
			budget_heads.add(row.budget_head)

	def on_submit(self): 
		logging.debug(f"in VCMBudgetAmendment on_submit")
        # Ensure the Budget Amendment is linked to a valid Budget document
		company_name = frappe.get_doc("Company", self.company)
		company_abbr = company_name.abbr
		budget_name = f"{company_abbr}-{self.fiscal_year}-{self.location}-{self.cost_center}"

	
		
        # Fetch the Budget document 
		budget_doc = frappe.get_doc("VCM Budget", budget_name)
		#logging.debug(f"Budget Amend-1 Name:  {budget_name}, {budget_doc}") 		

		# Create a dictionary for quick lookup of budget heads
		budget_items_map = {item.budget_head: item for item in budget_doc.get("budget_items") or []}

        # Loop over each item in the Budget Amendment child table
		for amend_item in self.get("budget_amendment_items") or []:
            #logging.debug(f"Budget Amend-2  {amend_item} ")
			updated = False
			if amend_item.proposed_amendment == 0:
				continue  # Skip if no amendment is proposed
			
			budget_item = budget_items_map.get(amend_item.budget_head)
			# Attempt to locate the corresponding child record in the Budget doc
			if budget_item:
				#logging.debug(f"Budget Amend-3  {budget_item}, {budget_item.budget_head}, {amend_item.budget_head} ")
				# Update desired fields. For example:
				budget_item.current_budget += amend_item.proposed_amendment
				budget_item.amended_till_now += amend_item.proposed_amendment
				budget_item.balance_budget = budget_item.current_budget - budget_item.used_budget
			else:
				# Add new budget item if the budget head doesn't exist
				budget_item = budget_doc.append("budget_items", {
					"budget_head": amend_item.budget_head,
					"current_budget": amend_item.proposed_amendment,
					"amended_till_now": amend_item.proposed_amendment,
					"balance_budget": amend_item.proposed_amendment,
					"proposed_by": amend_item.proposed_by
				})
				frappe.msgprint(f"New Budget Head added: {amend_item.budget_head}, {amend_item.budget_head}, {amend_item.proposed_amendment}")
			#update budget amendment child table to sync with Budget child table
			amend_item.current_budget = budget_item.current_budget
			amend_item.amended_till_now = budget_item.amended_till_now
			amend_item.balance_budget = budget_item.balance_budget					
			#logging.debug(f" Budget Amend-1-1 {amend_item.budget_head}, {budget_item.current_budget},{amend_item.proposed_amendment},{budget_item.balance_budget}")			
  
		try:
			budget_doc.save(ignore_permissions=True)
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Budget Amendment Save Error: {str(e)}")
			logging.error(f"Error in budget amendment: {str(e)}")
