
import frappe, erpnext
from frappe.utils.data import getdate
from frappe.model.naming import getseries
import datetime

from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt

class VCMPurchaseReceipt(PurchaseReceipt):
    def autoname(self):
        #dateF = getdate(self.posting_date)
        # based upn creation date
        dateF = datetime.datetime.now()
        company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
        year = dateF.strftime("%y")
        month = dateF.strftime("%m")
        prefix = f"{company_abbr}-PR-{year}{month}-"
        if self.is_return:
            prefix = f"{company_abbr}-PRRET-{year}{month}-"
        self.name = prefix + getseries(prefix, 5)