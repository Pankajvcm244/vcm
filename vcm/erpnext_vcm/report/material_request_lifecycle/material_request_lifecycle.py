# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


##############################################    I want this for by default set compny depart and date range 1 Month  ############

import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company","width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department","width": 150},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center","width": 150},
        {"label": "Set Target Warehouse", "fieldname": "set_warehouse", "fieldtype": "Link", "options": "Warehouse","width": 150},
        {"label": "Material Request ID", "fieldname": "material_request_id", "fieldtype": "Link", "options": "Material Request", "width": 150},
        {"label": "Material Request Workflow State", "fieldname": "material_request_workflow_state", "fieldtype": "Data", "width": 180},
        {"label": "Material Request Status", "fieldname": "material_request_status", "fieldtype": "Data", "width": 150},
        {"label": "Material Request Creation Date", "fieldname": "material_request_creation_date", "fieldtype": "Date", "width": 150},
        {"label": "Percent Ordered", "fieldname": "percent_ordered", "fieldtype": "Percent", "width": 100},
        {"label": "Percent Received", "fieldname": "percent_received", "fieldtype": "Percent", "width": 100},
        {"label": "Purpose", "fieldname": "purpose", "fieldtype": "Data", "width": 150},
        {"label": "Item Code", "fieldname": "material_request_item_code", "fieldtype": "Data", "width": 120},
        {"label": "Item Name", "fieldname": "material_request_item_name", "fieldtype": "Data", "width": 200},
        {"label": "Qty", "fieldname": "material_request_quantity", "fieldtype": "Float", "width": 80},
        {"label": "UOM", "fieldname": "material_request_uom", "fieldtype": "Data", "width": 100},

        {"label": "Purchase Order ID", "fieldname": "purchase_order_id", "fieldtype": "Link", "options": "Purchase Order", "width": 150},
        {"label": "Purchase Order Creation Date", "fieldname": "purchase_order_creation_date", "fieldtype": "Date", "width": 150},
        {"label": "Purchase Person", "fieldname": "custom_purchase_person", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "Purchase Order Status", "fieldname": "purchase_order_status", "fieldtype": "Data", "width": 150},
        {"label": "Purchase Order Workflow State", "fieldname": "purchase_order_workflow_state", "fieldtype": "Data", "width": 180},

        {"label": "Gate In ID", "fieldname": "gate_in_id", "fieldtype": "Data", "width": 150},
        {"label": "Gate In Creation Date", "fieldname": "gate_in_creation_date", "fieldtype": "Date", "width": 150},
       
        {"label": "Purchase Receipt ID", "fieldname": "purchase_receipt_id", "fieldtype": "Link", "options": "Purchase Receipt", "width": 150},
        {"label": "Purchase Receipt Status", "fieldname": "purchase_receipt_status", "fieldtype": "Data", "width": 150},
        {"label": "Purchase Receipt Creation Date", "fieldname": "purchase_receipt_creation_date", "fieldtype": "Date", "width": 150},

        {"label": "Purchase Invoice ID", "fieldname": "purchase_invoice_id", "fieldtype": "Link", "options": "Purchase Invoice", "width": 150},
        {"label": "Purchase Invoice Status", "fieldname": "purchase_invoice_status", "fieldtype": "Data", "width": 150},
        {"label": "Purchase Invoice Creation Date", "fieldname": "purchase_invoice_creation_date", "fieldtype": "Date", "width": 150},

        {"label": "Payment Entry ID", "fieldname": "payment_entry_id", "fieldtype": "Link", "options": "Payment Entry", "width": 150},
        {"label": "Payment Entry Status", "fieldname": "payment_entry_status", "fieldtype": "Data", "width": 150},
        {"label": "Payment Entry Date", "fieldname": "payment_entry_date", "fieldtype": "Date", "width": 150},
        {"label": "Mode of Payment", "fieldname": "mode_of_payment", "fieldtype": "Data", "width": 150},
        {"label": "Paid Amount", "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
    ]

    conditions = "mr.docstatus = 1 AND mr.material_request_type = 'Purchase'"
    values = {}

    if filters.get("company"):
        conditions += " AND mr.company = %(company)s"
        values["company"] = filters["company"]

    if filters.get("department"):
        conditions += " AND mr.department = %(department)s"
        values["department"] = filters["department"]

    if filters.get("set_warehouse"):
        conditions += " AND mr.set_warehouse = %(set_warehouse)s"
        values["set_warehouse"] = filters["set_warehouse"]

    if filters.get("from_date"):
        conditions += " AND mr.creation >= %(from_date)s"
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions += " AND mr.creation <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    data = frappe.db.sql(f"""
        SELECT
            mr.name AS material_request_id,
            UPPER(mr.status) AS material_request_status,
            mr.workflow_state AS material_request_workflow_state,
            DATE(mr.creation) AS material_request_creation_date,
            mr.per_ordered AS percent_ordered,
            mr.per_received AS percent_received,
            mr.purpose,
            mr.company,
            mr.department,
            mr.cost_center,
            mr.set_warehouse,
            mri.item_code AS material_request_item_code,
            mri.item_name AS material_request_item_name,
            mri.qty AS material_request_quantity,
            mri.uom AS material_request_uom,

            po.name AS purchase_order_id,
            UPPER(po.status) AS purchase_order_status,
            DATE(po.creation) AS purchase_order_creation_date,
            po.workflow_state AS purchase_order_workflow_state,
            po.custom_purchase_person AS custom_purchase_person,
                         
            gi.name AS gate_in_id,
            DATE(gi.creation) AS gate_in_creation_date,            
            
            pr.name AS purchase_receipt_id,
            UPPER(pr.status) AS purchase_receipt_status,
            DATE(pr.creation) AS purchase_receipt_creation_date,

            pi.name AS purchase_invoice_id,
            UPPER(pi.status) AS purchase_invoice_status,
            DATE(pi.creation) AS purchase_invoice_creation_date,

            pe.name AS payment_entry_id,
            UPPER(pe.status) AS payment_entry_status,
            pe.posting_date AS payment_entry_date,
            pe.mode_of_payment,
            pe.paid_amount

        FROM
            `tabMaterial Request` mr
        LEFT JOIN `tabMaterial Request Item` mri ON mri.parent = mr.name
        LEFT JOIN `tabPurchase Order Item` poi ON poi.material_request = mr.name AND poi.item_code = mri.item_code
        LEFT JOIN `tabPurchase Order` po ON po.name = poi.parent
        LEFT JOIN `tabVCM Gate-In` gi ON gi.purchase_order = po.name
        LEFT JOIN `tabPurchase Receipt Item` pri ON pri.purchase_order = po.name AND pri.item_code = mri.item_code
        LEFT JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
        LEFT JOIN `tabPurchase Invoice Item` pii ON pii.purchase_order = po.name AND pii.item_code = mri.item_code
        LEFT JOIN `tabPurchase Invoice` pi ON pi.name = pii.parent
        LEFT JOIN `tabPayment Entry Reference` per ON per.reference_name = pi.name AND per.reference_doctype = 'Purchase Invoice'
        LEFT JOIN `tabPayment Entry` pe ON pe.name = per.parent
        WHERE {conditions}
    """, values=values, as_dict=1)

    return columns, data
