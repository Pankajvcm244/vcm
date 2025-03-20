# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BudgetHead(Document):
	def autoname(self):
		self.name = f"{self.budget_head_number}-{self.budget_head_name}"
