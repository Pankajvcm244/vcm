import frappe

def execute(filters=None):
    if filters is None:
        filters = {}

    columns = [
        {"label": "Material Request", "fieldname": "material_request", "fieldtype": "Link", "options": "Material Request", "width": 220},
        {"label": "MR Date", "fieldname": "mr_date", "fieldtype": "Date", "width": 120},

        {"label": "Purchase Order", "fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "width": 200},
        {"label": "PO Date", "fieldname": "po_date", "fieldtype": "Date", "width": 120},

        {"label": "Gate-In", "fieldname": "gate_in_id", "fieldtype": "Link", "options": "VCM Gate-In", "width": 180},
        {"label": "Gate-In Date", "fieldname": "gate_in_date", "fieldtype": "Date", "width": 120},

        {"label": "Purchase Receipt", "fieldname": "purchase_receipt_id", "fieldtype": "Link", "options": "Purchase Receipt", "width": 180},
        {"label": "PR Receipt Date", "fieldname": "purchase_receipt_date", "fieldtype": "Date", "width": 140},

        {"label": "Purchase Invoice", "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 180},
        {"label": "PI Date", "fieldname": "pi_date", "fieldtype": "Date", "width": 120},

        {"label": "Supplier Inv No", "fieldname": "supplier_invoice_no", "fieldtype": "Data", "width": 150},
        {"label": "Supplier Inv Date", "fieldname": "supplier_invoice_date", "fieldtype": "Date", "width": 150},

        {"label": "Invoice Amount", "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 140},

        {"label": "Payment Entry", "fieldname": "payment_entry", "fieldtype": "Link", "options": "Payment Entry", "width": 200},
        {"label": "PE Date", "fieldname": "pe_date", "fieldtype": "Date", "width": 120},
    ]

    conditions = """
        WHERE mr.docstatus = 1
        AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s
        AND mr.company = %(company)s
    """

    if filters.get("cost_center"):
        conditions += " AND poi.cost_center = %(cost_center)s"

    if filters.get("supplier"):
        conditions += " AND po.supplier = %(supplier)s"

    query = f"""
        SELECT
            mr.name AS material_request,
            mr.transaction_date AS mr_date,

            po.name AS purchase_order,
            po.transaction_date AS po_date,
        

            pi.name AS purchase_invoice,
            pi.posting_date AS pi_date,

            IFNULL(pi.bill_no, 'N/A') AS supplier_invoice_no,
            IFNULL(pi.bill_date, NULL) AS supplier_invoice_date,

            pe.name AS payment_entry,
            pe.posting_date AS pe_date,

            pr.name AS purchase_receipt_id,
            DATE(pr.creation) AS purchase_receipt_date,

            gi.name AS gate_in_id,
            DATE(gi.creation) AS gate_in_date,

            pi.grand_total AS invoice_amount

        FROM `tabMaterial Request` mr
        LEFT JOIN `tabPurchase Order Item` poi ON poi.material_request = mr.name
        LEFT JOIN `tabPurchase Order` po ON po.name = poi.parent

        LEFT JOIN `tabPurchase Invoice Item` pii ON pii.purchase_order = po.name
        LEFT JOIN `tabPurchase Invoice` pi ON pi.name = pii.parent

        LEFT JOIN `tabPayment Entry Reference` per ON per.reference_name = pi.name
        LEFT JOIN `tabPayment Entry` pe ON pe.name = per.parent

        LEFT JOIN `tabPurchase Receipt Item` pri ON pri.purchase_order = po.name
        LEFT JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent

        LEFT JOIN `tabVCM Gate-In` gi ON gi.name = pr.custom_gate_in_reference

        {conditions}

        GROUP BY mr.name, po.name, pi.name, pe.name, pr.name, gi.name
        ORDER BY mr.transaction_date
    """

    data = frappe.db.sql(query, filters, as_dict=True)
    return columns, data
