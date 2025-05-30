# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.model.document import Document
from frappe.model.naming import getseries
import datetime



class AutoReorderLog(Document):
    def autoname(self):
        now = datetime.datetime.now()
        month = now.strftime("%m")
        year = now.strftime("%y")
        prefix = f"MRO-{year}{month}-"         
        self.name = prefix + getseries(prefix, 5)
        
