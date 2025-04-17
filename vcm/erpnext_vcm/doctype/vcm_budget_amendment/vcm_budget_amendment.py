# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.naming import getseries
from frappe.model.document import Document
import logging
logging.basicConfig(level=logging.DEBUG)

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
		#logging.debug(f"in VCMBudgetAmendment validate ")
        # Check if budget_head is a folder (is_group = 1)
		is_group = frappe.get_value("Cost Center", self.cost_center, "is_group")
		if is_group:
				frappe.throw(f"Cost Center'{self.cost_center}' is a folder. Please select a child Cost Center.")				
		budget_heads = set()
		for row in self.budget_amendment_items:
			# Check for duplicate budget heads
			if row.budget_head in budget_heads:
				frappe.throw(f"Duplicate Budget Head: {row.budget_head}. Each Budget Head must be unique.")
			is_head_group = frappe.get_value("Budget Head", row.budget_head, "is_group")
			if is_head_group:
				frappe.throw(f"Budget Head {row.budget_head} is a folder. Please select a child Budget Head.")
			budget_heads.add(row.budget_head)
		        # Ensure the Budget Amendment is linked to a valid Budget document
		
		# Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
		budget_name = frappe.db.get_value(
			"VCM Budget", 
			{"company": self.company, "location": self.location, "fiscal_year": self.fiscal_year, "cost_center": self.cost_center, "docstatus": 1},
			"name")
		if not budget_name:
			frappe.throw(f"VCM Budget not found for {self.company}, {self.location}, {self.cost_center}")
		# Fetch the Budget document only if it's in Submit state and not Cancelled
		budget_doc = frappe.get_doc("VCM Budget", budget_name)     
		if not budget_doc:
			frappe.throw(f"No submitted VCM Budget found for {budget_name}")
		# Create a dictionary for quick lookup of budget heads
		budget_items_map = {item.budget_head: item for item in budget_doc.get("budget_items") or []}
		# Loop over each item in the Budget Amendment child table
		for amend_item in self.get("budget_amendment_items") or []:
			budget_item = budget_items_map.get(amend_item.budget_head)
			# Attempt to locate the corresponding child record in the Budget doc
			if not budget_item:
				frappe.throw(f"Budget Head {amend_item.budget_head} not found in VCM Budget {budget_name}, please remove it or contact ERP team to add budget Head in Budget before submitting again.")


	def on_submit(self): 
		#logging.debug(f"in VCMBudgetAmendment on_submit")
		# Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
		budget_name = frappe.db.get_value(
			"VCM Budget", 
			{"company": self.company, "location": self.location, "fiscal_year": self.fiscal_year, "cost_center": self.cost_center, "docstatus": 1},
			"name")

		# Fetch the Budget document only if it's in Submit state and not Cancelled
		budget_doc = frappe.get_doc("VCM Budget", budget_name)    
		if not budget_doc:
			frappe.throw(f"No submitted VCM Budget found for {budget_name}")
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
				#logging.debug(f"Budget Amend-3  {budget_item} ")
				#logging.debug(f"Budget Amend-4   {budget_item.budget_head}, {amend_item.budget_head} ")
				# Update desired fields. For example:
				budget_item.current_budget += amend_item.proposed_amendment
				budget_item.amended_till_now += amend_item.proposed_amendment
				budget_item.balance_budget = budget_item.current_budget - budget_item.used_budget
			#update budget amendment child table to sync with Budget child table
			amend_item.current_budget = budget_item.current_budget
			amend_item.amended_till_now = budget_item.amended_till_now
			amend_item.balance_budget = budget_item.balance_budget
			#logging.debug(f" Budget Item-1-1 {budget_item.original_amount}, {budget_item.amended_till_now},{budget_item.current_budget} ,{budget_item.proposed_amendment},{budget_item.balance_budget}, {budget_item.used_budget}")
			#logging.debug(f" Budget Amend Item-1-1 {amend_item.original_amount}, {amend_item.amended_till_now},{amend_item.current_budget} ,{amend_item.proposed_amendment},{amend_item.balance_budget}, {amend_item.used_budget}")			
		try:
			budget_doc.add_comment("Comment", text=f"Budget amended for {amend_item.budget_head} by Rs {amend_item.proposed_amendment }")
			budget_doc.save(ignore_permissions=True)
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Budget Amendment Save Error: {str(e)}")
			logging.error(f"Error in budget amendment: {str(e)}")
