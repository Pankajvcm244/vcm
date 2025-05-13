import frappe
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from frappe import _, throw
from frappe.model.docstatus import DocStatus
from frappe.utils import flt
from frappe.utils.data import getdate
from frappe.model.naming import getseries
import datetime
import logging
logging.basicConfig(level=logging.DEBUG)

from vcm.erpnext_vcm.overrides.stock_alm.stockalm import (
    assign_and_notify_next_authority,
    get_stock_alm_level,
)
from datetime import date

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

    # def validate(self):
    #     super().validate()
    #     if self.stock_entry_type == "Material Transfer":
    #         self.validate_stock_qty()

    # def correct_qty_exceeding_actual(self):
    #     for row in self.items:
    #         # Get actual stock from Bin (current stock in warehouse)
    #         actual_qty = frappe.db.get_value(
    #             "Bin", 
    #             {"item_code": row.item_code, "warehouse": row.s_warehouse}, 
    #             "actual_qty"
    #         ) or 0

    #         if row.qty > actual_qty:
    #             frappe.msgprint({
    #                 "title": "Auto-Corrected Quantity",
    #                 "message": f"Row #{row.idx} — Quantity ({row.qty}) exceeds available stock ({actual_qty}). Automatically set to {actual_qty}.",
    #                 "indicator": "orange"
    #             })
    #             row.qty = actual_qty
    #             row.transfer_qty = actual_qty  # also update transfer_qty if needed

    def correct_qty_exceeding_actual(self):
        for row in self.items:
            actual_qty = frappe.db.get_value(
                "Bin",
                {"item_code": row.item_code, "warehouse": row.s_warehouse},
                "actual_qty"
                ) or 0

        if row.qty > actual_qty:
            frappe.msgprint(
                f"Row #{row.idx} — Quantity ({row.qty}) exceeds available stock ({actual_qty}). Automatically set to {actual_qty}.",
                title="Auto-Corrected Quantity",
                indicator="orange"
            )
            row.qty = actual_qty
            row.transfer_qty = actual_qty

        
    def on_submit(self):
        # self.validate_stock_qty()
        super().on_submit()
        #self.validate_stock_qty()
        if self.stock_entry_type == "Material Issue":
            self.send_material_issue_email()
            if hasattr(self, "stock_entry_type") and self.stock_entry_type == "Material Transfer":
                alm_level = get_stock_alm_level(self)
                if alm_level is None:
                    self.workflow_state = "Final Level Approved"

    
    def before_submit(self):
        if self.stock_entry_type == "Material Transfer":
            self.correct_qty_exceeding_actual()

    def before_save(self):
        #self.update_extra_description_from_mrn()
        self.refresh_alm()
        

    def on_update(self):
        super().on_update()
        assign_and_notify_next_authority(self)



    def refresh_alm(self):
        if self.stock_entry_type != "Material Transfer":
            return  # Skip if it's not a stock transfer
      
        alm_level = get_stock_alm_level(self)

        if alm_level is not None:
            self.recommended_by = alm_level.recommender
            self.first_approver = alm_level.first_approver
            self.final_approver = alm_level.final_approver
        else:
            frappe.msgprint("ALM Levels are not set for this ALM Center in this document")

            

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

 















