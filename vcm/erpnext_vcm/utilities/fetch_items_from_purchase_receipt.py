import re
from erpnext.accounts.party import get_default_contact
import frappe
from frappe.contacts.doctype.address.address import get_default_address
#import logging
#logging.basicConfig(level=logging.DEBUG)


@frappe.whitelist()
def get_PR_items(pr_doc_id):
    #logging.debug(f"get_PR_items.py  {pr_doc_id} ")
    purchase_receipt_doc = frappe.get_doc("Purchase Receipt", pr_doc_id)
    #logging.debug(f"purchase_receipt_doc {purchase_receipt_doc} ")

    items = []
    for item in purchase_receipt_doc.items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty
        })
    #logging.debug(f"Items:  {items} ")
    pr_receipt_entry_dict = frappe._dict(
        payment_recipt_number=pr_doc_id,
        company=purchase_receipt_doc.company,
        items=items,

    )

    purchase_receipt_entry = frappe.new_doc("VCM PR Label Print")
    purchase_receipt_entry.update(pr_receipt_entry_dict)
    return purchase_receipt_entry


