# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance
from frappe.model.naming import getseries
from pypika.functions import IfNull, Sum  
from frappe.utils import flt
import datetime

import logging
logging.basicConfig(level=logging.DEBUG)

class VCMStockAudit(Document):
	def autoname(self):
		import datetime
		# Ensure posting_date is a datetime.date or datetime.datetime object
		if isinstance(self.posting_date, str):
			posting_date = datetime.datetime.strptime(self.posting_date, "%Y-%m-%d")
		else:
			posting_date = self.posting_date
		day = posting_date.strftime("%d")
		month = posting_date.strftime("%m")
		year = posting_date.strftime("%y")
		prefix = f"StockPV-{self.warehouse}-{day}{month}{year}-"
		self.name = prefix + getseries(prefix, 2)


@frappe.whitelist()
def get_item_qty(item_code, warehouse):
	logging.debug(f"in stock audit get_item_qty 1 {item_code} {warehouse}")
	if not item_code or not warehouse:
		logging.debug(f"in stock audit get_item_qty returning 0")
		return 0.0

	# Optional: use now() or a specific posting time if needed
	stock_qty = get_stock_balance(item_code, warehouse)
	logging.debug(f"in stock audit get_item_qty 2 {stock_qty}")
	return stock_qty or 0.0


#get_pos_reserved_qty(item_code, warehouse)

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

@frappe.whitelist()
def get_vcm_current_qty(item_code, warehouse):
	# Get the current stock balance for the item in the specified warehouse
	stock_qty = get_item_qty(item_code, warehouse)
	# Get the reserved quantity for the item in the specified warehouse
	reserved_qty = get_pos_reserved_qty(item_code, warehouse)
	# Calculate the available quantity
	available_qty = flt(stock_qty) - flt(reserved_qty)
	return available_qty



@frappe.whitelist()
def get_items_with_stock(warehouse):
    return frappe.db.sql("""
        SELECT
            bin.item_code,
            item.item_name,
            item.stock_uom,
            bin.actual_qty
        FROM
            `tabBin` bin
        JOIN
            `tabItem` item ON bin.item_code = item.name
        WHERE
            bin.warehouse = %s AND bin.actual_qty > 0
        ORDER BY bin.item_code
    """, warehouse, as_dict=True)