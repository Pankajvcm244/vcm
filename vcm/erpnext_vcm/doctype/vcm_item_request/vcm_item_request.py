# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import logging
logging.basicConfig(level=logging.DEBUG)

from vcm.erpnext_vcm.doctype.vcm_item_request.vcm_item_alm import (
    assign_and_notify_next_authority,
    get_vcm_item_alm_level,
)

import frappe
from frappe.model.document import Document
from datetime import date
from frappe.utils.background_jobs import enqueue
from frappe.workflow.doctype.workflow_action.workflow_action import (
    get_doc_workflow_state,
)


class VCMItemRequest(Document):
	def __init__(self, *args, **kwargs):
		super(VCMItemRequest, self).__init__(*args, **kwargs)
          
	def before_save(self):
        # super().before_save() #Since there is no before_insert in parent
		logging.debug(f"in item request before_save  {self}  ")
		self.refresh_alm()

	def on_update(self):
		logging.debug(f"in item request on_update  -1  {self}  ")
		assign_and_notify_next_authority(self)

	def refresh_alm(self):
		logging.debug(f"in item request refresh_alm  {self}  ")
		if hasattr(self, "department") and self.department == "":
			frappe.throw("Department is not set.")
		alm_level = get_vcm_item_alm_level(self)
		if alm_level is not None:
			self.l1_approver = alm_level.l1_approver
			self.l2_approver = alm_level.l2_approver
			self.final_approver = alm_level.final_approver
			logging.debug(f"in item request refresh_alm  {self.l1_approver}, {self.l2_approver}, {self.final_approver}  ")
		else:
			frappe.throw("VCM Item Req ALM Levels are not set for this ALM Center in this document")

	def validate(self):
		logging.debug(f"in item request validate  {self}  ")
		#check_items_are_not_from_template(self)
		#validate_work_order_item(self)
		#validate_one_time_vendor(self)
		#self.validate_mrn_availble()
		#validate_buying_dates(self)
		return

	


@frappe.whitelist()
def resend_approver_request(docname, method):
	logging.debug(f"in item request resend_approver_request  {docname}  ")
	frappe.only_for(["Purchase User", "Purchase Manager"])
	doc = frappe.get_doc("Purchase Order", docname)
	assign_and_notify_next_authority(doc, method)