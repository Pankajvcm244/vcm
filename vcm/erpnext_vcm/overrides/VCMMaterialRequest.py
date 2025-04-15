import frappe
from frappe.model.naming import getseries
from erpnext.stock.doctype.material_request.material_request import MaterialRequest

class VCMMaterialRequest(MaterialRequest):
    def autoname(self):
        company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
        prefix = f"{company_abbr}-MAT-MR-2526-"
        self.name = prefix + getseries(prefix, 5)

    def on_submit(self):
        super().on_submit()

        if self.material_request_type == "Material Issue":
            self.send_material_issue_email()

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
