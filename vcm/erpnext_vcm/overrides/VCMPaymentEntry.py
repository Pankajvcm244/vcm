import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry

import logging
logging.basicConfig(level=logging.DEBUG)

from vcm.erpnext_vcm.utilities.vcm_budget_update_usage import (
    update_vcm_budget_on_payment_submit,
    revert_vcm_budget_on_payment_submit,
)

class VCMPaymentEntry(PaymentEntry):
    
    def before_submit(self):     
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        logging.debug(f"HKM PE Submit-1 {vcm_budget_settings.payment_entry_budget_enabled}")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            logging.debug(f"VCM PE Submit-2 calling budget")
            update_vcm_budget_on_payment_submit(self)
    
    def on_cancel(self):
        super().on_cancel()
        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
        logging.debug(f"HKM PE on cancel Submit-1 {vcm_budget_settings.payment_entry_budget_enabled}")
        if vcm_budget_settings.payment_entry_budget_enabled == "Yes":
            logging.debug(f"VCM PE Submit-2 calling revert budget")
            revert_vcm_budget_on_payment_submit(self)