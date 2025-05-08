# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries
import datetime
from frappe.utils.xlsxutils import make_xlsx
from frappe.utils.file_manager import save_file


class VCMStockAuditMerge(Document):
	def autoname(self):    
		# Get today's date
		today = datetime.datetime.today()
		day = today.strftime("%d")
		month = today.strftime("%m")
		year = today.strftime("%y")
		# Create the prefix with warehouse, current date (day, month, year)
		prefix = f"StockPVMerged-{self.warehouse}-{day}{month}{year}-"
		# Set the name using the series (getseries)
		self.name = prefix + getseries(prefix, 2)


@frappe.whitelist()
def merge_audits(docname):
    doc = frappe.get_doc("VCM Stock Audit Merge", docname)
    merged_data = {}
    for ref in doc.audit_references:
        audit = frappe.get_doc("VCM Stock Audit", ref.audit)
        for row in audit.items:
            key = row.item_code
            if key in merged_data:
                # If item exists, add actual quantity only
                merged_data[key]["actual_quantity"] += row.actual_quantity or 0
                merged_data[key]["qty_difference"] =(
                    merged_data[key]["actual_quantity"] - merged_data[key]["expected_quantity"]
                )
            else:
                # If item is new, take all fields
                merged_data[key] = {
                    "item_code": row.item_code,
                    "item_name": row.item_name,
                    "stock_uom": row.uom,
                    "expected_quantity": row.expected_quantity or 0,
                    "actual_quantity": row.actual_quantity or 0,
                    "qty_difference": (row.actual_quantity or 0) - (row.expected_quantity or 0),
                    "counted_at": row.counted_at
                }

    # Clear old data
    doc.set("merged_items", [])

    # Add merged data to child table
    for item in merged_data.values():
        doc.append("merged_items", item)

    doc.save()
    return "Merged successfully!"

@frappe.whitelist()
def export_merged_report(docname):
    doc = frappe.get_doc("VCM Stock Audit Merge", docname)

    # Add metadata rows before the table
    data = []

    # Add warehouse info
    data.append(["Warehouse:", doc.warehouse])
    
    # Add audit references
    audit_names = ", ".join([ref.audit for ref in doc.audit_references])
    data.append(["Audit References:", audit_names])

    # Empty row for spacing
    data.append([])

    # Add table headers
    data.append(["Item Code", "Item Name", "UOM", "Expected Quantity", "Actual Quantity", "Qty Difference"])

    # Add table rows
    for row in doc.merged_items:
        data.append([
            row.item_code,
            row.item_name,
            row.uom,
            row.expected_quantity,
            row.actual_quantity,
            row.qty_difference
        ])

    # Generate XLSX content
    xlsx_file = make_xlsx(data, "Merged Stock Report")

    # Save the file
    saved_file = save_file(
        fname=f"Merged_Stock_Report_{docname}.xlsx",
        content=xlsx_file.getvalue(),
        dt="VCM Stock Audit Merge",
        dn=docname,
        is_private=True
    )

    return saved_file.file_url