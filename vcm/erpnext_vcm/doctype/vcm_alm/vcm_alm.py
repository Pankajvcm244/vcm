# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document



class VCMALM(Document):
	def autoname(self):        
		company_name = frappe.get_doc("Company", self.company)
		company_abbr = company_name.abbr
		self.name = f"ALM-{company_abbr}-{self.document}"
