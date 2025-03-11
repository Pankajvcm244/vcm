# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
from frappe.model.naming import getseries

class VCMDEPTApproval(Document):
    def autoname(self):
        now = datetime.datetime.now()
        month = now.strftime("%m")
        year = now.strftime("%y")
        company_abbr = frappe.get_value("Company", self.company, "abbr")
        prefix = f"{company_abbr}-{year}{month}-"         
        self.name = prefix + getseries(prefix, 5)
