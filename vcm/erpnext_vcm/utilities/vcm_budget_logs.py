import frappe
import logging
from frappe.utils import flt

logging.basicConfig(level=logging.DEBUG)

@frappe.whitelist()
def create_vcm_transaction_log(self, remarks):
    #logging.debug(f"create_vcm_transaction {self}")
    doc = frappe.get_doc({
        "doctype": "VCMBudget Log",
        "transaction_date": frappe.utils.nowdate(),
        "company": self.company,
        "cost_center": self.cost_center,
        "budget_head": self.budget_head,
        "reference_document": self.name,
        "amount": self.rounded_total,
        "remarks": remarks,
        "status": "Pending"
    })
    #logging.debug(f"create_vcm_transaction {self}, {remarks}")
    doc.insert()
    frappe.db.commit()
    return doc.name


@frappe.whitelist()
def create_vcm_pe_transaction_log(self, remarks):
    #logging.debug(f"create_vcm_pe_transaction {self}")
    doc = frappe.get_doc({
        "doctype": "VCMBudget Log",
        "transaction_date": frappe.utils.nowdate(),
        "company": self.company,
        "cost_center": self.cost_center,
        "budget_head": self.budget_head,
        "reference_document": self.name,
        "amount": flt(self.paid_amount),
        "remarks": remarks,
        "status": "Pending"
    })
    #logging.debug(f"create_vcm_transaction {self}, {remarks}")
    doc.insert()
    frappe.db.commit()
    return doc.name


@frappe.whitelist()
def create_vcm_jv_transaction_log(self, remarks):
    #logging.debug(f"create_vcm_transaction {self}")
    #doc = frappe.get_doc({
    #    "doctype": "VCMBudget Log",
    #    "transaction_date": frappe.utils.nowdate(),
    #    "company": "TSF", #self.company,
    #    "cost_center": "Annakoot", #self.cost_center,
    #    "budget_head": "Test", #self.budget_head,
    #    "reference_document": "JV", #self.name,
    #    "amount": 100, #self.rounded_total,
    #    "remarks": remarks,
    #    "status": "Pending"
    #})
    #logging.debug(f"create_vcm_transaction {self}, {remarks}")
    #doc.insert()
    #frappe.db.commit()
    #return doc.name
    return

@frappe.whitelist()
def delete_vcm_transaction_log(self, remarks=""):
    #logging.debug(f"delete_vcm_transaction {self}")
    frappe.db.sql("""DELETE FROM `tabVCMBudget Log` WHERE reference_document = %s""", self.name)
    frappe.db.commit()