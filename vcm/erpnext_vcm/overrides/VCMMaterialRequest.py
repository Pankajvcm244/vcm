import frappe
from frappe.model.naming import getseries
from erpnext.stock.doctype.material_request.material_request import MaterialRequest

class VCMMaterialRequest(MaterialRequest):
    def autoname(self):
        # based upon creation date
        company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
        #year = dateF.strftime("%y")
        #month = dateF.strftime("%m")
        prefix = f"{company_abbr}-MAT-MR-2526-"
        self.name = prefix + getseries(prefix, 5)