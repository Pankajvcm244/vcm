import re
from erpnext.accounts.party import get_default_contact
import frappe
from frappe.contacts.doctype.address.address import get_default_address
#import logging
#logging.basicConfig(level=logging.DEBUG)




@frappe.whitelist()
def get_MR_items(item_req_doc_id):
    #logging.debug(f"get_PR_items.py  {pr_doc_id} ")
    item_req_doc = frappe.get_doc("VCM Item Request", item_req_doc_id)
    #logging.debug(f"purchase_receipt_doc {purchase_receipt_doc} ")
    
    items = []
    for item in item_req_doc.items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "schedule_date": item.required_by,
            "uom": item.uom,
            "stock_uom": item.stock_uom,
        })
    #logging.debug(f"Items:  {items} ")
    mr_receipt_entry_dict = frappe._dict(
        items=items,
    )

    material_request_doc = frappe.new_doc("Material Request")   
    material_request_doc.update(mr_receipt_entry_dict)
    material_request_doc.purpose_subject = item_req_doc.purpose_subject
    material_request_doc.company = item_req_doc.company
    material_request_doc.cost_center = item_req_doc.cost_center
    material_request_doc.project = item_req_doc.project
    material_request_doc.department = item_req_doc.department
    material_request_doc.purpose = item_req_doc.purpose_subject
    material_request_doc.description = item_req_doc.purpose_description
    return material_request_doc

@frappe.whitelist()
def get_item_details(item_code):
    """Fetch Item Name, UOM, and Stock UOM based on Item Code"""
    if not item_code:
        return {"error": "Item Code is required"}

    item = frappe.get_doc("Item", item_code)
    #logging.debug(f"Item:  {item} ")
    #logging.debug(f"***Item UOM etc:  {item.item_name}, {item.stock_uom} , {item.stock_uom}")
    return {
        "item_name": item.item_name,
        "uom": item.stock_uom,  # Fetch Stock UOM as default UOM
        "stock_uom": item.stock_uom
        
    }

