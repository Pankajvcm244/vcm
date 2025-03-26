import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from frappe.utils.background_jobs import enqueue
from frappe.utils.password import get_decrypted_password
from frappe.utils import cstr
import frappe, requests

import logging
logging.basicConfig(level=logging.DEBUG)

from vcm.erpnext_vcm.utilities.vcm_budget_update_usage import (
    update_vcm_budget_on_payment_submit,
    revert_vcm_budget_on_payment_submit,
    validate_vcm_budget_on_payment_entry,
    validate_budget_head_n_location_mandatory,
)
# from vcm.erpnext_vcm.utilities.vcm_budget_logs import (
#     create_vcm_pe_transaction_log,
#     delete_vcm_transaction_log,
# )

class VCMPaymentEntry(PaymentEntry):        
    def on_submit(self):        
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        logging.debug(f"VCM PE on_Submit {vcm_budget_settings.payment_entry_budget_enabled}")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            vcm_cost_center = frappe.get_doc("Cost Center", self.cost_center)
            if vcm_cost_center.custom_vcm_budget_applicable == "Yes":
                if validate_budget_head_n_location_mandatory(self) == True:
                    #logging.debug(f"VCM PE on_Submit -2 ")
                    update_vcm_budget_on_payment_submit(self)
                    #create_vcm_pe_transaction_log(self, "PE Submitted")

        vcm_whatsapp_settings = frappe.get_doc("VCM WhatsAPP Settings") 
        logging.debug(f"VCM Payment Entry after_submit {vcm_whatsapp_settings.payment_entry_whatsapp_enabled} ")
        if vcm_whatsapp_settings.payment_entry_whatsapp_enabled:
            purchase_person_email = self.custom_purchase_person 
            mobile_no = frappe.db.get_value("User", {"email": purchase_person_email}, "mobile_no")  # Get mobile from Email 
            purchase_person_name = frappe.db.get_value("User", {"email": purchase_person_email}, "first_name")  # Get mobile from Email                     
            logging.debug(f"VCM Payment Entry after_submit {purchase_person_email}, {mobile_no}")
            if purchase_person_email is None:
                logging.debug(f"No Purchase user defined for Payment Entry {self.name}")
                return
            else:
                #mobile_no = frappe.get_value("User", user, "mobile_no")
                #purchase_person_email = frappe.get_value("User", user, "email")
                if mobile_no:
                    logging.debug(f"VCM Payment Entry after_submit calling send whatsapp {self},{mobile_no}")
                    send_whatsapp_to_purchase_person(self, mobile_no, purchase_person_name)
                if purchase_person_email:
                    logging.debug(f"VCM Payment Entry after_submit calling send email {self},{purchase_person_email}")
                    send_email_to_purchase_person(self, purchase_person_email, purchase_person_name) 
        super().on_submit() 

    def on_cancel(self):
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        #logging.debug(f"HKM PE on cancel Submit-1 {vcm_budget_settings.payment_entry_budget_enabled}")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            vcm_cost_center = frappe.get_doc("Cost Center", self.cost_center)
            if vcm_cost_center.custom_vcm_budget_applicable == "Yes":
                #logging.debug(f"VCM PE Submit-2 calling revert budget")
                if validate_budget_head_n_location_mandatory(self) == True:
                    revert_vcm_budget_on_payment_submit(self) 
                    #delete_vcm_transaction_log(self,"PE Cancelled")
        super().on_cancel()

    def validate(self):
        super().validate()
        #logging.debug(f"VCM PE validate")
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            vcm_cost_center = frappe.get_doc("Cost Center", self.cost_center)
            if vcm_cost_center.custom_vcm_budget_applicable == "Yes":
                if validate_budget_head_n_location_mandatory(self) == True:
                    validate_vcm_budget_on_payment_entry(self)
        return


def send_email_to_purchase_person(self, purchase_person_email, purchase_person_name):
        logging.debug(f"**in send_email_to_purchase_person  {self.name} , {purchase_person_email} ************* ")
        template_data = { 
            "party_name": self.party_name,
            "name": self.name,
            "paid_amount": self.paid_amount,
            "reference_no": self.reference_no,
            "reference_date": self.reference_date,
            "custom_purchase_person": purchase_person_name  # Purchase person name
        }
        email_args = {
            "recipients": [purchase_person_email],
            "message": frappe.render_template(
                "vcm/erpnext_vcm/utilities/email_templates/paymententry_email.html",
                template_data,
            ),
            "subject": "Payment to Supplier {} status".format(self.party_name),
            "reference_doctype": self.doctype,
            "delayed": False,
        }
        enqueue(
            method=frappe.sendmail, queue="short", timeout=300, is_async=True, **email_args
        )
        return

def send_whatsapp_to_purchase_person(self, mobile_no, purchase_person_name):
    logging.debug(f"**in send_whatsapp_to_purchase_person  {self.name} ************* ")

    whatsupsettings = frappe.get_doc("VCM WhatsAPP Settings")
    # Fetch the booking document
    #booking = frappe.get_doc("booking", booking_id)
    
    doctype = "VCM WhatsAPP Settings"  # Example of a singleton DocType
    fieldname = "token" 
    decrypted_value = get_decrypted_password(doctype, doctype, fieldname)
    #logging.debug(f"whatsup {name},{mobile}, {hall_name}, {booking_status},  {booking_id}, {whatsupsettings.template}, {date}, {from_time}, {to_time} ")
    # settings = frappe.get_cached_doc("VCM WhatsAPP Settings")
    #po_approval_settings = frappe.get_cached_doc("HKM General Settings")
    
    site_name = cstr(frappe.local.site)
    po_name  = self.name    

    headers = {
         "Content-Type": "application/json",
         "Authorization": f"Basic {decrypted_value}"
    }
    data =  {
        "countryCode": "+91",
        "fullPhoneNumber": f"+91{mobile_no}",
        "callbackData": "some text here",
        "type": "Template",
        "template": {
            "name": f"{whatsupsettings.payment_entry_template}",
            "languageCode": "en",
            "headerValues": [
                self.party_name
            ],            
            "bodyValues": [
                purchase_person_name,
                self.party_name,
                self.paid_amount,
                self.reference_no,
                str(self.posting_date) if hasattr(self, "posting_date") else None,  # Convert to string
                self.name
            ]
        }        
    }

    try:
        response = requests.post(whatsupsettings.url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        logging.debug(f"****************** payment whatsup message sent {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        #logging.debug(f"whatsup message sent error  {response.json()}, {str(e)}")
        frappe.throw(f"Error sending Payment Entry WhatsApp message: {str(e)}")
    