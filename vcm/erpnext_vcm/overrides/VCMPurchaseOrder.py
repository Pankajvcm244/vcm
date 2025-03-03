import logging
logging.basicConfig(level=logging.DEBUG)

from hkm.erpnext___custom.overrides.purchase_order.alm import (
    assign_and_notify_next_authority,
    get_alm_level,
)
from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
import frappe, re
from hkm.erpnext___custom.extend.accounts_controller import validate_gst_entry
from hkm.erpnext___custom.overrides.buying_validations import (
    check_items_are_not_from_template,
    validate_buying_dates,
    validate_work_order_item,
    validate_one_time_vendor,
)
from datetime import date
from frappe.utils.background_jobs import enqueue
from frappe.workflow.doctype.workflow_action.workflow_action import (
    get_doc_workflow_state,
)

from vcm.erpnext_vcm.utilities.vcm_budget_update_usage import (
    update_vcm_po_budget_usage,
    revert_vcm_po_budget_usage,
)

from vcm.erpnext_vcm.utilities.vcm_budget_logs import (
    create_vcm_transaction_log,
    delete_vcm_transaction_log,
)

# from hkm.erpnext___custom.po_approval.po_workflow_trigger import check_alm


class VCMPurchaseOrder(PurchaseOrder):
    def __init__(self, *args, **kwargs):
        super(VCMPurchaseOrder, self).__init__(*args, **kwargs)

    def before_save(self):
        # super().before_save() #Since there is no before_insert in parent
        validate_gst_entry(self)
        self.update_extra_description_from_mrn()
        self.refresh_alm()

    def on_update(self):
        super().on_update()
        assign_and_notify_next_authority(self)

    def refresh_alm(self):
        if hasattr(self, "department") and self.department == "":
            frappe.throw("Department is not set.")
        alm_level = get_alm_level(self)
        if alm_level is not None:
            self.recommended_by = alm_level.recommender
            self.first_approving_authority = alm_level.first_approver
            self.final_approving_authority = alm_level.final_approver
        else:
            frappe.throw("ALM Levels are not set for this ALM Center in this document")

    def validate(self):
        super().validate()
        check_items_are_not_from_template(self)
        validate_work_order_item(self)
        validate_one_time_vendor(self)
        self.validate_mrn_availble()
        validate_buying_dates(self)
        return
    
    def before_submit(self):
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        logging.debug(f"HKM PO Submit-1 {vcm_budget_settings.po_budget_enabled}")
        if vcm_budget_settings.po_budget_enabled == "Yes":
            logging.debug(f"HKM PO Submit-2 calling update budget")
            update_vcm_po_budget_usage(self)

    def on_submit(self):
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        logging.debug(f"HKM PO Submit-1 {vcm_budget_settings.po_budget_enabled}")
        if vcm_budget_settings.po_budget_enabled == "Yes":
            create_vcm_transaction_log(self, "PO Submitted") 

    def on_cancel(self):
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        logging.debug(f"HKM PO Submit-1 {vcm_budget_settings.po_budget_enabled}")
        if vcm_budget_settings.po_budget_enabled == "Yes":
            logging.debug(f"HKM PO Submit-2 calling revert budget")
            revert_vcm_po_budget_usage(self)
            delete_vcm_transaction_log(self,"PO Cancelled")


    def update_extra_description_from_mrn(self):
        descriptions = []
        mrns = frappe.db.get_all(
            "Purchase Order Item",
            pluck="material_request",
            filters={"parent": self.name},
        )
        mrns = set(mrns)
        for mrn in mrns:
            if mrn is not None:
                mrn_doc = frappe.get_doc("Material Request", mrn)
                if mrn_doc.purpose:
                    descriptions.append(mrn_doc.purpose + "\n")
                if mrn_doc.description:
                    descriptions.append(mrn_doc.description + "\n")
        description = ", ".join(descriptions)
        if self.extra_description == None or self.extra_description.strip() == "":
            self.extra_description = description
        return

    def validate_mrn_availble(self):
        for item in self.items:
            if item.material_request is None:
                frappe.throw(
                    f"Item {item.item_name} doesn't have a linked MRN. Seems this Purchase Order is not linked from any MRN."
                )
        return

    def before_insert(self):
        # super().before_insert() #Since there is no before_insert in parent
        self.set_naming_series()
        self.validate_work_request_status()

    def set_naming_series(self):
        if self.meta.get_field("for_a_work_order") and self.for_a_work_order:
            self.naming_series = "WO-.YY..MM.-"
        else:
            self.naming_series = "PO-.YY..MM.-"

    def validate_work_request_status(self):
        if not (self.meta.get_field("for_a_work_order") and self.for_a_work_order == 1):
            return
        mrns = []
        for row in self.get("items"):
            mrn = row.material_request
            if mrn is not None and mrn not in mrns:
                mrns.append(mrn)
        for mrn in mrns:
            mrn_doc = frappe.get_doc("Material Request", mrn)
            if mrn_doc.completed == 1:
                frappe.throw(
                    "<p> Work Order is not allowed in respect to this work request ({}) because it has been marked as <b class='text-danger'>COMPLETED</b> by the User (MRN Approver).</p>".format(
                        mrn_doc.name
                    )
                )
        return


@frappe.whitelist()
def resend_approver_request(docname, method):
    frappe.only_for(["Purchase User", "Purchase Manager"])
    doc = frappe.get_doc("Purchase Order", docname)
    assign_and_notify_next_authority(doc, method)
