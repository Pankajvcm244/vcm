import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    # Define columns for the report
    columns = [
        {"fieldname": "payment_mode", "label": "Payment Mode", "fieldtype": "Data", "width": 150},
        {"fieldname": "total_paid", "label": "Total Paid Amount", "fieldtype": "Currency", "width": 150},
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data", "width": 150},  
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "total_qty", "label": "Total Quantity Sold", "fieldtype": "Float", "width": 150},
        {"fieldname": "total_sales", "label": "Total Sales Amount", "fieldtype": "Currency", "width": 150}
    ]

    # Initialize conditions and values for SQL query
    conditions = []
    values = {}

    # Apply Date Filters
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("si.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = filters["from_date"]
        values["to_date"] = filters["to_date"]

    # Apply POS Profile Filter
    if filters.get("pos_profile"):
        conditions.append("si.pos_profile = %(pos_profile)s")
        values["pos_profile"] = filters["pos_profile"]

    # Combine conditions
    conditions_sql = " AND ".join(conditions) if conditions else "1=1"

    # Fetch Payment Mode Summary
    payment_data = frappe.db.sql(
        """
        SELECT 
            sip.mode_of_payment AS payment_mode, 
            SUM(sip.amount) AS total_paid
        FROM `tabSales Invoice Payment` sip
        JOIN `tabSales Invoice` si ON sip.parent = si.name
        WHERE {conditions_sql}
        GROUP BY sip.mode_of_payment
        """.format(conditions_sql=conditions_sql), 
        values, as_dict=True
    )

    # Calculate the total sum of all payment methods
    total_amount = sum(row["total_paid"] for row in payment_data) if payment_data else 0

    # Append a total row for payment summary
    payment_data.append({
        "payment_mode": "Total",
        "total_paid": total_amount
    })

    # Fetch Top 10 Selling Items based on Quantity (Including Item Code)
    top_items_data = frappe.db.sql(
        """
        SELECT 
            si_item.item_code AS item_code,
            si_item.item_name AS item_name, 
            SUM(si_item.qty) AS total_qty, 
            SUM(si_item.amount) AS total_sales
        FROM `tabSales Invoice Item` si_item
        JOIN `tabSales Invoice` si ON si_item.parent = si.name
        WHERE {conditions_sql}
        GROUP BY si_item.item_code, si_item.item_name
        ORDER BY total_qty DESC
        """.format(conditions_sql=conditions_sql), 
        values, as_dict=True
    )

    # Prepare combined data
    data = payment_data + top_items_data

    # Prepare **ONLY** the Payment Mode Chart
    chart = {
        "data": {
            "labels": [row["payment_mode"] for row in payment_data if row["payment_mode"] != "Total"],
            "datasets": [{"values": [row["total_paid"] for row in payment_data if row["payment_mode"] != "Total"]}]
        },
        "type": "donut"
    }
    # Prepare **Payment Mode Chart with Total**
#     chart = {
#     "data": {
#         "labels": [row["payment_mode"] for row in payment_data],  # Include 'Total' label
#         "datasets": [{"values": [row["total_paid"] for row in payment_data]}]  # Include 'Total' value
#     },
#     "type": "donut"
# }

    

    return columns, data, None, chart  # Returning only the Payment Mode Chart



