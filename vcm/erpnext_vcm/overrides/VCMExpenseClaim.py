
#from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
#import frappe


##from vcm.erpnext_vcm.utilities.vcm_budget_update_usage import (
 #   update_vcm_expense_budget_usage,
#)

#from erpnext.accounts.doctype.pos_invoice.pos_invoice import (
#    POSInvoice,
#    get_stock_availability,
#)

#class VCMExpenseClaim(Document):
#    def on_submit(self):
#        super().on_submit()
#        vcm_budget_settings = frappe.get_doc("VCM Budget Settings")
#        if vcm_budget_settings.expense_budget_enabled == "Yes":
#            update_vcm_expense_budget_usage(self)