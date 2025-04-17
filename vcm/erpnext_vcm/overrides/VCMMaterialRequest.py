import frappe
from frappe.model.naming import getseries
from erpnext.stock.doctype.material_request.material_request import MaterialRequest
import logging
logging.basicConfig(level=logging.DEBUG)

from vcm.erpnext_vcm.overrides.mr_alm.mralm import (
    assign_and_notify_mrn_next_authority,
    get_mrn_alm_level,
    check_approver_assigned,
)


class VCMMaterialRequest(MaterialRequest):
    def autoname(self):
        company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
        prefix = f"{company_abbr}-MAT-MR-2526-"
        self.name = prefix + getseries(prefix, 5)

    # def before_save(self):
    #     super().before_save()
        # super().before_save() #Since there is no before_insert in parent
        #logging.debug(f"in MR Before save")
        # if (self.material_request_type == "Purchase"):
        #     alm_level = get_mrn_alm_level(self)
        #     if alm_level is not None:
        #         self.refresh_alm()
    
    # def validate(self):
    #     super().validate()
		#logging.debug(f"in VCMStoreRequisition validate  {self}  ")
        # if (self.material_request_type == "Purchase"):
        #     alm_level = get_mrn_alm_level(self)
        #     if alm_level is not None:
        #         check_approver_assigned(self)
        

    # def on_update(self): 
    #     if (self.material_request_type == "Purchase"):
    #         alm_level = get_mrn_alm_level(self)
    #         if alm_level is not None:
    #             assign_and_notify_mrn_next_authority(self)

    def on_submit(self):
        super().on_submit()
        if self.material_request_type == "Material Issue":
            self.send_material_issue_email()
        # if (self.material_request_type == "Purchase"):
        #     alm_level = get_mrn_alm_level(self)
        #     #  in case of no approval flow set, on submit set workflow state as Final Approved
        #     if alm_level is None:
        #         logging.debug(f"in MR on_submit  {self}  ")
        #         self.workflow_state = "Final Level Approved"
        #

    def refresh_alm(self):
        if hasattr(self, "department") and self.department == "":
            frappe.throw("Department is not set.")
        #if hasattr(self, "location") and self.location == "":
        #    frappe.throw("Location is not set.")
        logging.debug(f"in MR refresh_alm  {self.department} ")
        alm_level = get_mrn_alm_level(self)
        if alm_level is not None:
            self.custom_l1_approver = alm_level.custom_l1_approver
            self.custom_l2_approver = alm_level.custom_l2_approver
            self.custom_final_approver = alm_level.custom_final_approver
            logging.debug(f"MR refresh_alm {self.custom_l1_approver} {self.custom_l2_approver} {self.custom_final_approver}")
        else:
            frappe.throw("Material Request approval Levels are not set, please set the same")

@frappe.whitelist()
def resend_approver_request(docname, method):
    frappe.only_for(["Purchase User", "Purchase Manager", "Stock Manager","Stock User"])
    doc = frappe.get_doc("Material Request", docname)
    assign_and_notify_mrn_next_authority(doc, method)

def send_material_issue_email(self):
        recipient_email = frappe.get_value("User", self.material_recipient, "email")
        if not recipient_email:
            return

        # Prepare item data list for the template
        items_list = [{
            "item_code": i.item_code,
            "item_name":i.item_name,
            "schedule_date": i.schedule_date,
            "qty": i.qty,
            "uom": i.uom,
            "warehouse": i.warehouse
        } for i in self.items]

        # Data for the template
        template_data = {
            "name": self.name,
            "company": self.company,
            "department": self.department,
            "material_request_type": self.material_request_type,
            "purpose": self.purpose,
            "transaction_date": self.transaction_date,
            "required_by": self.schedule_date or self.required_by,
            "material_recipient": self.material_recipient,
            "items": items_list
        }

        subject = f"Material Issue Notification: {self.name}"

        email_args = {
            "recipients": [recipient_email],
            "subject": subject,
            "message": frappe.render_template(
                "vcm/erpnext_vcm/utilities/email_templates/materialissue.html",
                template_data
            ),
            "reference_doctype": self.doctype,
            "reference_name": self.name,
            "delayed": False,
        }

        # Send the email async
        frappe.enqueue(
            method=frappe.sendmail,
            queue="short",
            timeout=300,
            is_async=True,
            **email_args
        )