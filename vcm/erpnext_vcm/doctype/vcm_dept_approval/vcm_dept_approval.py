# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from datetime import datetime

class VCMDEPTApproval(Document):
    def autoname(self):
        company_abbr = frappe.get_value("Company", self.company, "abbr")
        date_prefix = datetime.today().strftime("%y%m")  # Get YYMM format
        self.name = make_autoname(f"{company_abbr}-{date_prefix}-####")
