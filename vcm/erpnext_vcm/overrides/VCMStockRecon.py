import frappe
from frappe.model.naming import getseries
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import StockReconciliation


class VCMStockRecon(StockReconciliation):
    
    def autoname(self):
        # based upon creation date
        company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
        #year = dateF.strftime("%y")
        #month = dateF.strftime("%m")
        prefix = f"{company_abbr}-MAT-RECO-2526-"
        self.name = prefix + getseries(prefix, 5)