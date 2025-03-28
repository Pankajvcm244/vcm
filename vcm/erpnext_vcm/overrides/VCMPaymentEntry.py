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
        super().on_submit()     
        vcm_budget_settings = frappe.get_cached_doc("VCM Budget Settings")
        #logging.debug(f"VCM PE on_Submit {vcm_budget_settings.payment_entry_budget_enabled}")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            vcm_cost_center = frappe.get_doc("Cost Center", self.cost_center)
            if vcm_cost_center.custom_vcm_budget_applicable == "Yes":
                if validate_budget_head_n_location_mandatory(self) == True:
                    #logging.debug(f"VCM PE on_Submit -2 ")
                    update_vcm_budget_on_payment_submit(self)
                    #create_vcm_pe_transaction_log(self, "PE Submitted")

        vcm_whatsapp_settings = frappe.get_doc("VCM WhatsAPP Settings") 
        #logging.debug(f"VCM Payment Entry after_submit {vcm_whatsapp_settings.payment_entry_whatsapp_enabled} ")
        # this  Flag payment_entry_whatsapp_enabled is for Purchase person
        if vcm_whatsapp_settings.payment_entry_whatsapp_enabled:
            purchase_person_email = self.custom_purchase_person 
            mobile_no = frappe.db.get_value("User", {"email": purchase_person_email}, "mobile_no")  # Get mobile from Email 
            purchase_person_name = frappe.db.get_value("User", {"email": purchase_person_email}, "first_name")  # Get mobile from Email                     
            #logging.debug(f"VCM Payment Entry after_submit {purchase_person_email}, {mobile_no}")
            if purchase_person_email is None:
                #logging.debug(f"No Purchase user defined for Payment Entry {self.name}")
                return
            else:
                #mobile_no = frappe.get_value("User", user, "mobile_no")
                #purchase_person_email = frappe.get_value("User", user, "email")
                if mobile_no:
                    #logging.debug(f"VCM Payment Entry after_submit calling send whatsapp {purchase_person_name},{mobile_no}")
                    send_whatsapp_to_person(self, mobile_no, purchase_person_name)
                if purchase_person_email:
                    #logging.debug(f"VCM Payment Entry after_submit calling send email {purchase_person_name},{purchase_person_email}")
                    send_email_to_person(self, purchase_person_email, purchase_person_name) 
        # this  Flag payment_entry_whatsapp_enabled is for Supplier email and whatsup
        if vcm_whatsapp_settings.supplier_whatsapp_enabled:
            vcm_party_name = self.party_name             
            if vcm_party_name is None:
                #logging.debug(f"No Supplier is defined for Payment Entry {self.name}")
                return
            else:
                billing_address_name = f"{vcm_party_name}-Billing"
                supplier_mobile = frappe.db.get_value("Address", {"name": billing_address_name}, "phone")
                supplier_emailid = frappe.db.get_value("Address", {"name": billing_address_name}, "email_id")
                #logging.debug(f"VCM Payment Entry after_submit {billing_address_name}, {supplier_mobile}, {supplier_emailid}")
                if supplier_mobile:
                    #logging.debug(f"VCM Payment Entry 2 after_submit calling send whatsapp {vcm_party_name},{supplier_mobile}")
                    send_whatsapp_to_person(self, supplier_mobile, vcm_party_name)
                if supplier_emailid:
                    #logging.debug(f"VCM Payment Entry  2 after_submit calling send email {self},{supplier_emailid}")
                    send_email_to_person(self, supplier_emailid, vcm_party_name) 
         

    def on_cancel(self):
        super().on_cancel()
        vcm_budget_settings = frappe.get_cached_doc("VCM Budget Settings")
        #logging.debug(f"HKM PE on cancel Submit-1 {vcm_budget_settings.payment_entry_budget_enabled}")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            vcm_cost_center = frappe.get_doc("Cost Center", self.cost_center)
            if vcm_cost_center.custom_vcm_budget_applicable == "Yes":
                #logging.debug(f"VCM PE Submit-2 calling revert budget")
                if validate_budget_head_n_location_mandatory(self) == True:
                    revert_vcm_budget_on_payment_submit(self) 
                    #delete_vcm_transaction_log(self,"PE Cancelled")
        

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


def send_email_to_person(self, person_email, person_name):
        #logging.debug(f"**in send_email_to_purchase_person  {self.name} , {person_email} ************* ")
        company_abbr = frappe.get_value("Company", self.company, "abbr") 
        template_data = { 
            "payer": self.company,
            "party_name": self.party_name,
            "name": self.name,
            "paid_amount": self.paid_amount,
            "reference_no": self.reference_no,
            "reference_date": self.reference_date.strftime("%d-%m-%Y") if hasattr(self, "reference_date") and self.reference_date else None,
            "custom_purchase_person": person_name,  # Purchase person name
            "company_abbr": company_abbr
        }
        email_args = {
            "recipients": [person_email],
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

def send_whatsapp_to_person(self, mobile_no, whatapp_person_name):
    #logging.debug(f"**in send_whatsapp_to_purchase_person  {whatapp_person_name} ************* ")
    whatsupsettings = frappe.get_cached_doc("VCM WhatsAPP Settings")    
    doctype = "VCM WhatsAPP Settings"  # Example of a singleton DocType
    fieldname = "token" 
    decrypted_value = get_decrypted_password(doctype, doctype, fieldname)
    #logging.debug(f"whatsup {name},{mobile}, {hall_name}, {booking_status},  {booking_id}, {whatsupsettings.template}, {date}, {from_time}, {to_time} ") 
    company_abbr = frappe.get_value("Company", self.company, "abbr") 
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
                whatapp_person_name,
                self.party_name,
                self.company,
                self.paid_amount,
                self.reference_no,
                self.reference_date.strftime("%d-%m-%Y") if hasattr(self, "reference_date") and self.reference_date else None,
                self.name,
                company_abbr
            ]
        }        
    }
    try:
        response = requests.post(whatsupsettings.url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        #logging.debug(f"****************** payment whatsup message sent {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.debug(f"whatsup message sent error  {response.json()}, {str(e)}")
        frappe.throw(f"Error sending Payment Entry WhatsApp message: {str(e)}")
    