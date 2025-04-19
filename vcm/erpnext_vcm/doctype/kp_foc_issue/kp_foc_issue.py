# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries
import datetime

class KPFOCIssue(Document): 
	
    def on_submit(self):
        create_stock_entry(self, "on_submit")  # Create Stock Entry
        send_email_notification(self)  # Send email notification
        

    def on_cancel(self):
        cancel_stock_entry(self)  # Cancel linked Stock Entry
        
	
    def autoname(self):
        now = datetime.datetime.now()
        month = now.strftime("%m")
        year = now.strftime("%y")
        prefix = f"KP-FOC-{year}{month}-"         
        self.name = prefix + getseries(prefix, 5)
        


def create_stock_entry(doc, method=None):
    """Create a Stock Entry (Material Issue) when VcmFocBilling is submitted."""
    
    if not doc.items:
        frappe.throw("No items found to create a Stock Entry.")

    try:
        stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Issue",
            "company": doc.company or frappe.defaults.get_global_default("company"),
            "posting_date": frappe.utils.nowdate(),
            "material_recipient": doc.material_recipient,
            "cost_center": getattr(doc, "cost_center", None),
            "items": []
        })

        for item in doc.items:
            stock_entry.append("items", {
                "item_code": item.item_code,
                "qty": item.quantity,
                "uom": item.uom,
                "stock_uom": item.uom,
                "conversion_factor": 1,
                "s_warehouse": getattr(item, "source_warehouse", None)
            })

        stock_entry.insert(ignore_permissions=True)
        stock_entry.submit()

        # Link Stock Entry to VcmFocBilling
        doc.stock_entry_reference = stock_entry.name
        doc.db_set("stock_entry_reference", stock_entry.name)  # Save reference in DB

        frappe.msgprint(f"<b>Stock Entry <span style='color: green;'>{stock_entry.name}</span> created successfully.</b>", alert=True)

    except Exception as e:
        frappe.log_error(f"Error creating Stock Entry for {doc.name}: {str(e)}", "Stock Entry Creation Error")
        frappe.throw(f"<b style='color: red;'>Failed to create Stock Entry.</b><br><br><b>Error:</b> {str(e)}")

def cancel_stock_entry(doc):
    """Cancel the Stock Entry when VcmFocBilling is canceled."""

    if not doc.stock_entry_reference:
        frappe.msgprint("<b>No Stock Entry linked to this document.</b>", alert=True)
        return

    try:
        stock_entry = frappe.get_doc("Stock Entry", doc.stock_entry_reference)

        if stock_entry.docstatus == 1:  # Check if it's submitted
            stock_entry.cancel()
            frappe.msgprint(f"<b>Stock Entry <span style='color: red;'>{stock_entry.name}</span> canceled successfully.</b>", alert=True)
        else:
            frappe.msgprint(f"Stock Entry {stock_entry.name} is already in Draft or Cancelled state.", alert=True)

    except Exception as e:
        frappe.log_error(f"Error canceling Stock Entry {doc.stock_entry_reference}: {str(e)}", "Stock Entry Cancellation Error")
        frappe.throw(f"<b style='color: red;'>Failed to cancel Stock Entry.</b><br><br><b>Error:</b> {str(e)}")

def send_email_notification(doc):
    """Send a modern email notification after submission of VcmFocBilling."""

    # Fetch email from "Devotee Details" based on Devotee ID
    recipient_email = frappe.db.get_value("Devotee Details", {"name": doc.foc_devotee_email}, "email_id")

    if not recipient_email:
        frappe.throw(f"No email found for Devotee ID: {doc.foc_devotee_email}. Please check Devotee Details.")

    subject = f"🧾 Your FOC Billing {doc.name} has been Submitted ✅"

    message = f"""
    <div style="font-family: 'Arial', sans-serif; padding: 20px; background-color: #f4f4f4; border-radius: 10px;">
        <div style="background-color: #007bff; color: white; padding: 15px; border-radius: 10px 10px 0 0; text-align: center;">
            <h2 style="margin: 0;">Hare Krishna, {doc.foc_devotee_name} 🙏</h2>
        </div>

        <div style="background: white; padding: 20px; border-radius: 0 0 10px 10px;">
            <p style="font-size: 16px; color: #333;">
                A Free-of-Cost (FOC) billing for <strong style="color: #28a745;">₹{doc.grand_total}</strong> has been processed in your name at <strong style="color: #007bff;">Krishna Prasadam Counter</strong>.
            </p>

            <div style="background-color: #fffbcc; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                <strong>📌 Remarks:</strong> {doc.remarks}
            </div>

            <h3 style="color: #007bff;">📜 Billing Details</h3>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr style="background-color: #007bff; color: white;">
                    <th style="padding: 10px; border: 1px solid #ddd;">Invoice No.</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Total Amount</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Date</th>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">{doc.name}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">₹{doc.grand_total}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{doc.posting_date}</td>
                </tr>
            </table>

            <h3 style="color: #28a745;">🛍️ Items Purchased</h3>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr style="background-color: #28a745; color: white;">
                    <th style="padding: 10px; border: 1px solid #ddd;">Item Name</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Quantity</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">UOM</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Rate</th>
                </tr>"""

    for item in doc.items:
        message += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">{item.item_name}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{item.quantity}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{item.uom}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">₹{item.rate}</td>
                </tr>
        """

    message += """
            </table>

           

            <div style="margin-top: 20px; background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545;">
                <strong>📞 Need Help?</strong><br>
                Contact Krishna Prasadam Counter:<br>
                <strong>Devdutt:</strong> 7500003865 | <strong>Bhura:</strong> 9720639844
            </div>

            <p style="margin-top: 20px; font-size: 14px; color: #777;">
                Regards,<br>
                <strong>ERP Systems & Process Team</strong><br>
                <span style="color: #007bff;">VCM ERP</span>
            </p>
        </div>
    </div>
    """

    try:
        frappe.sendmail(
            recipients=[recipient_email],
            subject=subject,
            message=message
        )
        frappe.msgprint("✅ Email notification sent successfully!", alert=True)
    except Exception as e:
        error_message = f"❌ Error sending email for {doc.name}: {str(e)}"
        frappe.log_error(error_message, "Email Notification Error")
        frappe.throw(f"Failed to send email. Please contact the ERP team. Error: {str(e)}")


