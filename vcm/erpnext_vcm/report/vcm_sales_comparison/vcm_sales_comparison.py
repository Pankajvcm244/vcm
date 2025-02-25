
import frappe
from frappe.utils import formatdate

def execute(filters=None):
    if not filters:
        filters = {}

    # Define columns
    columns = [
        {"fieldname": "posting_date", "label": "Date", "fieldtype": "Date", "width": 110},
        {"fieldname": "pos_profile", "label": "POS Profile", "fieldtype": "Link", "options": "POS Profile", "width": 150},
        {"fieldname": "total_sales", "label": "Total Sales", "fieldtype": "Currency", "width": 120}
    ]

    # Set conditions
    conditions = ["si.docstatus = 1", "si.is_pos = 1"]
    values = {}

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    if filters.get("pos_profile"):
        conditions.append("si.pos_profile = %(pos_profile)s")
        values["pos_profile"] = filters["pos_profile"]

    conditions_sql = " AND ".join(conditions)

    # Fetch Sales Data
    raw_data = frappe.db.sql(
        f"""
        SELECT
            si.posting_date,
            si.pos_profile,
            SUM(si.grand_total) AS total_sales
        FROM `tabSales Invoice` si
        WHERE {conditions_sql}
        GROUP BY si.posting_date, si.pos_profile
        ORDER BY si.posting_date
        """,
        values=values,
        as_dict=True
    )

    # Prepare Data for Table
    data = [{"posting_date": row.posting_date, "pos_profile": row.pos_profile, "total_sales": row.total_sales} for row in raw_data]

    # Extract unique dates & profiles
    all_dates = sorted(list({d.posting_date for d in raw_data}))
    all_profiles = sorted(list({d.pos_profile for d in raw_data}))

    # Create a sales map
    sales_map = {}
    for d in raw_data:
        sales_map.setdefault(d.posting_date, {})[d.pos_profile] = d.total_sales

    # Prepare Chart Data
    chart_data = {
        "labels": [formatdate(dt, "dd-MMM") for dt in all_dates],
        "datasets": []
    }

    if filters.get("pos_profile"):  
        # Show data for only the selected POS profile
        dataset = {
            "name": filters["pos_profile"],
            "values": [sales_map.get(dt, {}).get(filters["pos_profile"], 0) for dt in all_dates]
        }
        chart_data["datasets"].append(dataset)
    else:
        # Show data for all POS profiles if no filter is selected
        for profile in all_profiles:
            dataset = {
                "name": profile,
                "values": [sales_map.get(dt, {}).get(profile, 0) for dt in all_dates]
            }
            chart_data["datasets"].append(dataset)

    # Chart Configuration
    chart = {
        "data": chart_data,
        "type": "line",
        "title": f"Sales Comparison {filters.get('pos_profile', 'Across POS Counters')}"
    }

    return columns, data, None, chart
