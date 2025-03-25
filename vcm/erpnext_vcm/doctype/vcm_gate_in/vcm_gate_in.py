# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries
import datetime
from frappe.utils import now

class VCMGateIn(Document):
    def autoname(self):
        now = datetime.datetime.now()
        month = now.strftime("%m")
        year = now.strftime("%y")
        prefix = f"GateIn-{year}{month}-"         
        self.name = prefix + getseries(prefix, 5)

    def on_submit(self):
        self.gatein_date_time =  now() 
        self.db_update()  # Save the change in the database
        frappe.db.commit()  # Ensure the update is applied

@frappe.whitelist()
def update_gate_in_status(gate_in_name, new_status):
    # Check if the user is a System Manager
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to change the status.")

    # Fetch the Gate In document
    gate_in_doc = frappe.get_doc("VCM Gate-In", gate_in_name)
    
    # Allow only "Received" to "Pending" change
    if gate_in_doc.status == "Received" and new_status == "Pending":
        gate_in_doc.status = "Pending"
        gate_in_doc.save()
        frappe.msgprint(f"VCM Gate-In {gate_in_name} status changed to Pending.")
    else:
        frappe.throw("Invalid status change request.")

    return {"status": gate_in_doc.status}