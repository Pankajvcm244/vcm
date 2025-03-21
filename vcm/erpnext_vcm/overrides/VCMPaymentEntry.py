import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry

import logging
logging.basicConfig(level=logging.DEBUG)

from vcm.erpnext_vcm.utilities.vcm_budget_update_usage import (
    update_vcm_budget_on_payment_submit,
    revert_vcm_budget_on_payment_submit,
    validate_vcm_budget_on_payment_entry,
    validate_budget_head_mandatory,
)
# from vcm.erpnext_vcm.utilities.vcm_budget_logs import (
#     create_vcm_pe_transaction_log,
#     delete_vcm_transaction_log,
# )

class VCMPaymentEntry(PaymentEntry):        
    def on_submit(self):        
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        #logging.debug(f"VCM PE on_Submit {vcm_budget_settings.payment_entry_budget_enabled}")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            if validate_budget_head_mandatory(self) == True:
                #logging.debug(f"VCM PE on_Submit -2 ")
                update_vcm_budget_on_payment_submit(self)
                #create_vcm_pe_transaction_log(self, "PE Submitted")
        super().on_submit() 

    def on_cancel(self):
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        #logging.debug(f"HKM PE on cancel Submit-1 {vcm_budget_settings.payment_entry_budget_enabled}")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            #logging.debug(f"VCM PE Submit-2 calling revert budget")
            if validate_budget_head_mandatory(self) == True:
                revert_vcm_budget_on_payment_submit(self) 
                #delete_vcm_transaction_log(self,"PE Cancelled")
        super().on_cancel()

    def validate(self):
        super().validate()
        #logging.debug(f"VCM PE validate")
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            if validate_budget_head_mandatory(self) == True:
                validate_budget_head_mandatory(self)
                validate_vcm_budget_on_payment_entry(self)
        return