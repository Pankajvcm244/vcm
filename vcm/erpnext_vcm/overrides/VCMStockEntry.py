from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
import frappe
from frappe import _, throw
from frappe.model.docstatus import DocStatus
from frappe.utils import flt
from frappe.utils.data import getdate
from frappe.model.naming import getseries
import datetime

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



