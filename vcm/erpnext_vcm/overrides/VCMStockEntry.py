from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
import frappe
from frappe import _, throw
from frappe.model.docstatus import DocStatus
from frappe.utils import flt
from frappe.utils.data import getdate
from frappe.model.naming import getseries
import datetime

class VCMStockEntry(StockEntry):
    def autoname(self):
        # based upon creation date
        company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
        postingdate = datetime.datetime.now()
        postingyear = postingdate.year
        postingmonth = postingdate.month
         # Determine fiscal year
        if postingmonth < 4:  # If before April, it's part of the previous fiscal year
            fiscal_year = f"{(postingyear-1)% 100}{postingyear % 100}"
        else:
            fiscal_year = f"{postingyear % 100}{(postingyear + 1) % 100}"
        prefix = f"{company_abbr}-STE-{fiscal_year}-"
        self.name = prefix + getseries(prefix, 6)


    def on_submit(self):
        super().on_submit()
        if self.stock_entry_type == "Material Issue":
            self.send_material_issue_email()

    def send_material_issue_email(self):
        # Get recipient email from User doctype
        recipient_email = frappe.get_value("User", self.material_recipient, "email")
        if not recipient_email:
            frappe.log_error("Material recipient email not found.", self.material_recipient)
            return

        # Prepare item data list
        items_list = [{
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "uom": item.uom
        } for item in self.items]

        # Prepare template data
        template_data = {
            "name": self.name,
            "company": self.company,
            "cost_center": self.cost_center,
            "stock_entry_type": self.stock_entry_type,
            "posting_date": self.posting_date,
            "material_recipient": self.material_recipient,
            "items": items_list
        }

        subject = f" Material Issue Notification: {self.name}"

        email_args = {
            "recipients": [recipient_email],
            "subject": subject,
            "message": frappe.render_template(
                "vcm/erpnext_vcm/utilities/email_templates/materialissue.html",
                template_data
            ),
            "reference_doctype": self.doctype,
            "reference_name": self.name,
        }

        # Send the email asynchronously
        frappe.enqueue(
            method=frappe.sendmail,
            queue="short",
            timeout=300,
            is_async=True,
            **email_args
        )


    








