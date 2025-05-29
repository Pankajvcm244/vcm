# # Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# # For license information, please see license.txt


from frappe import _
import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries
from frappe.utils import get_url
from frappe.utils.jinja import render_template
import datetime

class GuestHouseFOC(Document):

    def autoname(self):
        now = datetime.datetime.now()
        month = now.strftime("%m")
        year = now.strftime("%y")
        prefix = f"GH-FOC-{year}{month}-"
        self.name = prefix + getseries(prefix, 5)

    def after_insert(self):
        if self.booking_status == "Pending":
            recipient_email = frappe.db.get_value("Devotee Details", self.devotee_ref, "email_id")

            if not recipient_email:
                frappe.log_error(f"No email found for Devotee: {self.devotee_ref}", "Email Sending Failed")
                return

            # Generate approve/reject URLs
            approve_link = get_url(f"/api/method/vcm.erpnext_vcm.doctype.guest_house_foc.guest_house_foc.approve_reservation?docname={self.name}&action=approve")
            reject_link = get_url(f"/api/method/vcm.erpnext_vcm.doctype.guest_house_foc.guest_house_foc.approve_reservation?docname={self.name}&action=reject")

            # Context to render HTML email
            context = {
                "devotee_name": self.devotee_name,
                "name": self.name,
                "guest_name": self.guest_name,
                "mobile_no": self.mobile_no,
                "check_in": self.check_in,
                "check_out": self.check_out,
                "number_of_rooms": self.number_of_rooms,
                "pax": self.pax,
                "remarks": self.remarks,
                "approve_link": approve_link,
                "reject_link": reject_link
            }

            # Render HTML template
            message = render_template("vcm/erpnext_vcm/utilities/email_templates/guesthouse_foc.html", context)

            # Send the email
            frappe.sendmail(
                recipients=[recipient_email],
                subject="🛏️ Guest House FOC Approval Needed",
                message=message
            )


@frappe.whitelist(allow_guest=True)
def approve_reservation(docname, action=None):
    try:
        doc = frappe.get_doc("Guest House FOC", docname)

        if doc.booking_status != "Pending":
            return _("Reservation is already processed.")

        if action == "approve":
            doc.booking_status = "Approved"
            doc.submit()
            frappe.db.commit()
            return _("Reservation Approved Successfully.")

        elif action == "reject":
            doc.booking_status = "Rejected"
            doc.save()
            frappe.db.commit()
            return _("Reservation Rejected.")

        else:
            return _("Invalid action.")

    except Exception as e:
        frappe.log_error(f"Error approving reservation: {str(e)}", "Reservation Approval")
        return _("There was an error processing the reservation.")
