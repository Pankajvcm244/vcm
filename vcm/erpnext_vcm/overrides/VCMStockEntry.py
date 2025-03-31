from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
import frappe
from frappe import _, throw
from frappe.model.docstatus import DocStatus
from frappe.utils import flt
from frappe.utils.data import getdate
from frappe.model.naming import getseries

class VCMStockEntry(StockEntry):
    def autoname(self):
        # based upon creation date
        company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
        #year = dateF.strftime("%y")
        #month = dateF.strftime("%m")
        prefix = f"{company_abbr}-STE-2526-"
        self.name = prefix + getseries(prefix, 6)



