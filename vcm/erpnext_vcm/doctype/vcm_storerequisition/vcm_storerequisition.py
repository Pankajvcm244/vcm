# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
import datetime
from frappe.model.naming import getseries

from frappe.workflow.doctype.workflow_action.workflow_action import (
    get_doc_workflow_state,
)

import logging
logging.basicConfig(level=logging.DEBUG)

from vcm.erpnext_vcm.doctype.vcm_storerequisition.vcm_storereq_approval_flow import (
    assign_and_notify_next_authority,
    get_vcm_storereq_approval_level,
	check_approver_assigned,
)
class VCMStoreRequisition(Document):
	def __init__(self, *args, **kwargs):
		super(VCMStoreRequisition, self).__init__(*args, **kwargs)
          
	def before_save(self):
        # super().before_save() #Since there is no before_insert in parent
		#logging.debug(f"in VCMStoreRequisition before_save  {self}  ")
		self.refresh_alm()

	def on_update(self):
		#logging.debug(f"in VCMStoreRequisition on_update  -1  {self}  ")
		assign_and_notify_next_authority(self)
	
	def autoname(self):
		now = datetime.datetime.now()
		month = now.strftime("%m")
		
		year = now.strftime("%y")
		prefix = f"VCMStoreReq-{year}{month}-"         
		self.name = prefix + getseries(prefix, 5)

	def refresh_alm(self):
		#logging.debug(f"in VCMStoreRequisition refresh_alm  {self}  ")
		if hasattr(self, "department") and self.department == "":
			frappe.throw("Department is not set.")
		alm_level = get_vcm_storereq_approval_level(self)
		if alm_level is not None:
			self.custom_l1_approver = alm_level.custom_l1_approver
			self.custom_l2_approver = alm_level.custom_l2_approver
			self.custom_final_approver = alm_level.custom_final_approver
			#logging.debug(f"in VCMStoreRequisition refresh_alm  {self.l1_approver}, {self.l2_approver}, {self.final_approver}  ")
		else:
			frappe.message("VCM DEPT approval flow levels are not set for this document type ")

	def validate(self):
		#logging.debug(f"in VCMStoreRequisition validate  {self}  ")
		check_approver_assigned(self)
		return
	
	

@frappe.whitelist()
def resend_approver_request(docname, method):
	#logging.debug(f"in VCMStoreRequisition resend_approver_request  {docname}  ")
	frappe.only_for(["Stock User", "Purchase User", "Purchase Manager", "Stock Manager"])
	doc = frappe.get_doc("VCM StoreRequisition", docname)
	assign_and_notify_next_authority(doc, method)
