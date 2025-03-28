

import frappe

def execute(filters=None):
    if not filters:
        filters = {}
    
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    document_type = filters.get("document_type", "Purchase Invoice")

    return [
        {"label": "ID", "fieldname": "name", "fieldtype": "Link", "options": document_type, "width": 150},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 200},
        {"label": "Transaction Date", "fieldname": "date", "fieldtype": "Date", "width": 120},  # Fixed alias
        {"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 150},
        {"label": "Budget Head", "fieldname": "budget_head", "fieldtype": "Data", "width": 150},
    ]

def get_data(filters):
    document_type = filters.get("document_type", "Purchase Invoice")
    selected_table = "tab" + document_type
    
    # Correcting date field mapping dynamically
    amount_field = "grand_total" if document_type in ["Purchase Order", "Purchase Invoice"] else "paid_amount"
    supplier_field = "supplier" if document_type != "Payment Entry" else "party"
    date_field = "transaction_date" if document_type == "Purchase Order" else "posting_date"

    conditions = ["docstatus = 1"]  # Ensures only submitted documents are fetched
    
    if filters.get("supplier"):
        conditions.append(f"{supplier_field} = %(supplier)s")
    if filters.get("cost_center"):
        conditions.append("cost_center = %(cost_center)s")
    if filters.get("location"):
        conditions.append("location = %(location)s")
    if filters.get("budget_head"):
        conditions.append("budget_head = %(budget_head)s")
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append(f"{date_field} BETWEEN %(from_date)s AND %(to_date)s")
    
    condition_string = " AND ".join(conditions)
    
    query = f"""
        SELECT
            name,
            {supplier_field} AS supplier,
            {date_field} AS date,  -- Fixed alias
            {amount_field} AS total_amount,
            status,
            cost_center,
            location,
            budget_head
        FROM `{selected_table}`
        WHERE {condition_string}
    """
    
    return frappe.db.sql(query, filters, as_dict=True)

