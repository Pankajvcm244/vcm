import frappe
from frappe.model.naming import getseries
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import StockReconciliation
from frappe.utils.data import getdate
from frappe.model.naming import getseries
import datetime

class VCMStockRecon(StockReconciliation):
    
    def autoname(self):
        # based upon creation date
        company_abbr = frappe.get_cached_value("Company", self.company, "abbr")   
        #postingdate = getdate(self.posting_date)
        postingdate = datetime.datetime.now()
        postingyear = postingdate.year
        postingmonth = postingdate.month
         # Determine fiscal year
        if postingmonth < 4:  # If before April, it's part of the previous fiscal year
            fiscal_year = f"{(postingyear-1)% 100}{postingyear % 100}"
        else:
            fiscal_year = f"{postingyear % 100}{(postingyear + 1) % 100}"
        prefix = f"{company_abbr}-MAT-RECO-{fiscal_year}-"
        self.name = prefix + getseries(prefix, 5)