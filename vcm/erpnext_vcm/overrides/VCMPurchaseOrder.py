import logging
logging.basicConfig(level=logging.DEBUG)

from frappe.utils.password import get_decrypted_password

from vcm.erpnext_vcm.overrides.po_alm.poalm import (
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
    validate_vcm_po_budget_amount_budgethead,
    validate_budget_head_n_location_mandatory,
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
        #if hasattr(self, "location") and self.location == "":
        #    frappe.throw("Location is not set.")
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
        validate_cost_center(self)
        # Disable this as at VCM MRN is not mandatory for all items 
        # self.validate_mrn_availble()
        validate_buying_dates(self)
        self.validate_mrn_quantity()
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        if vcm_budget_settings.po_budget_enabled == "Yes":
            vcm_cost_center = frappe.get_doc("Cost Center", self.cost_center)
            if vcm_cost_center.custom_vcm_budget_applicable == "Yes":
                if validate_budget_head_n_location_mandatory(self) == True:
                    validate_vcm_po_budget_amount_budgethead(self)            
            #logging.debug(f"in PO Validate 3 {self.workflow_state}")
        return        

    def on_submit(self):
        super().on_submit()          
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        #logging.debug(f"VCM PO on_Submit-1 {vcm_budget_settings.po_budget_enabled}")
        if vcm_budget_settings.po_budget_enabled == "Yes":
            vcm_cost_center = frappe.get_doc("Cost Center", self.cost_center)
            if vcm_cost_center.custom_vcm_budget_applicable == "Yes":
                if validate_budget_head_n_location_mandatory(self) == True:
                    #logging.debug(f"VCM PO on_Submit-2 calling update_vcm_po_budget_usage")
                    update_vcm_po_budget_usage(self, True)             
                    
        

    def on_cancel(self):          
        linked_pi = frappe.get_all(
            "Purchase Invoice Item",
            filters={
                "purchase_order": self.name,
                "docstatus": ["!=", 2]  # Exclude Cancelled Purchase Invoices
            },
            pluck="parent"  # Get the names of the linked Purchase Invoices
        )
        if linked_pi:
            frappe.throw(f"Cannot cancel Purchase Order {self.name}. It is linked to active Purchase Invoice(s): {', '.join(linked_pi)}.")
        super().on_cancel()      
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        #logging.debug(f"VCM PO on cancel -1 {vcm_budget_settings.po_budget_enabled}")
        if vcm_budget_settings.po_budget_enabled == "Yes":
            vcm_cost_center = frappe.get_doc("Cost Center", self.cost_center)
            if vcm_cost_center.custom_vcm_budget_applicable == "Yes":
                # lets not chekc while cancellation Accoutingdimesion fields
                #if validate_budget_head_n_location_mandatory(self) == True:
                update_vcm_po_budget_usage(self,False) 
                    #logging.debug(f"VCM PO on_cancell-2 created log")
        
    
    def before_insert(self):
        # super().before_insert() #Since there is no before_insert in parent
        self.set_naming_series()
        self.validate_work_request_status()

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

    def validate_mrn_quantity(self):
        default_tolerance = frappe.db.get_single_value("Stock Settings", "over_delivery_receipt_allowance") or 0

        for item in self.items:
            if item.material_request and item.material_request_item:
                mr_qty = frappe.db.get_value("Material Request Item", item.material_request_item, "qty") or 0

                # Get all other submitted PO quantities against this MR item (excluding current doc if resubmitting)
                #AND po.docstatus IN (0, 1)  -- include draft + submitted 
                existing_po_qty = frappe.db.sql("""
                    SELECT SUM(qty) FROM `tabPurchase Order Item` poi
                    INNER JOIN `tabPurchase Order` po ON po.name = poi.parent
                    WHERE poi.material_request_item = %s
                    AND po.docstatus IN (0, 1)                     
                    AND po.name != %s
                """, (item.material_request_item, self.name))[0][0] or 0

                # Optional: get item-specific tolerance
                try:
                    tolerance = frappe.db.get_value("Item", item.item_code, "over_delivery_receipt_tolerance") or default_tolerance
                except Exception:
                    tolerance = default_tolerance

                allowed_qty = mr_qty + (mr_qty * tolerance / 100)
                total_po_qty = existing_po_qty + item.qty  # Including this PO

                if total_po_qty > allowed_qty:
                    frappe.throw((f"Item <b>{item.item_code}</b> exceeds total allowed quantity for linked Material Request.<br>"
                        f"Requested: {mr_qty}, Allowed: {allowed_qty}, Already Ordered: {existing_po_qty}, "
                        f"This PO: {item.qty}, Total: {total_po_qty}"),
                        title="Over-Allowance Detected"
                    )


    def set_naming_series(self):
        company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
        if self.meta.get_field("for_a_work_order") and self.for_a_work_order:
            self.naming_series = f"{company_abbr}-WO-.YY..MM.-"
        else:
            self.naming_series = f"{company_abbr}-PO-.YY..MM.-"

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

@frappe.whitelist()
def validate_cost_center(self):
    if not self.cost_center:
         frappe.throw( f"Cost Center is mandatory in Purchase Order " )
    if not self.set_warehouse:
         frappe.throw( f"Target Warehouse is mandatory in Purchase Order " )
