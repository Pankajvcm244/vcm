import frappe
from frappe.utils import flt
from pypika.functions import IfNull, Sum  



@frappe.whitelist(allow_guest=True)
def get_erp_domains():
    # Fetch records from the custom Doctype 'ERP Domain'
    records = frappe.get_all(
        'VCM ERP Domain',  # Doctype name
        fields=['erp_title', 'erp_address']  # Fields to fetch
    )
    return records



# erpnext.accounts.doctype.pos_invoice.pos_invoice.get_pos_reserved_qty"


@frappe.whitelist()
def get_pos_reserved_qty(item_code, warehouse):
    p_inv = frappe.qb.DocType("POS Invoice")
    p_item = frappe.qb.DocType("POS Invoice Item")

    reserved_qty = (
        frappe.qb.from_(p_inv)
        .from_(p_item)
        .select(Sum(p_item.stock_qty).as_("stock_qty"))  
        .where(
            (p_inv.name == p_item.parent)
            & (IfNull(p_inv.consolidated_invoice, "") == "")
            & (p_item.docstatus == 1)
            & (p_item.item_code == item_code)
            & (p_item.warehouse == warehouse)
        )
    ).run(as_dict=True)

    return flt(reserved_qty[0].stock_qty) if reserved_qty and reserved_qty[0].stock_qty else 0




