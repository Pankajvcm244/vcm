import frappe

def get_child_cost_centers(parent_cost_center):
    """Fetch all child cost centers recursively under a given parent"""
    cost_centers = frappe.get_all(
        "Cost Center",
        filters={"parent_cost_center": parent_cost_center},
        pluck="name"
    )

    all_cost_centers = cost_centers[:]
    for cost_center in cost_centers:
        all_cost_centers.extend(get_child_cost_centers(cost_center))  # Recursive call to fetch sub-levels

    return all_cost_centers

def execute(filters=None):
    if not filters:
        filters = {}

    conditions = "vcm.docstatus = 1"  # Ensure only submitted documents (docstatus=1) are fetched
    values = []

    # If a parent cost center is selected, get all child cost centers
    if "cost_center" in filters:
        child_cost_centers = get_child_cost_centers(filters["cost_center"])
        child_cost_centers.append(filters["cost_center"])  # Include parent itself
        conditions += " AND vcm.cost_center IN ({})".format(", ".join(["%s"] * len(child_cost_centers)))
        values.extend(child_cost_centers)

    if "location" in filters:
        conditions += " AND vcm.location = %s"
        values.append(filters["location"])
    if "fiscal_year" in filters:
        conditions += " AND vcm.fiscal_year = %s"
        values.append(filters["fiscal_year"])
    if "company" in filters:
        conditions += " AND vcm.company = %s"
        values.append(filters["company"])

    # SQL Query to fetch budget data with docstatus condition
    query = """
        SELECT 
            cb.budget_head, cb.original_amount, cb.current_budget, cb.amended_till_now, cb.unpaid_purchase_order, cb.unpaid_purchase_invoice, cb.paid_payment_entry,
            cb.used_budget, cb.balance_budget, vcm.location, vcm.fiscal_year, 
            vcm.cost_center, vcm.company  
        FROM `tabVCM Budget Child Table` cb
        JOIN `tabVCM Budget` vcm ON cb.parent = vcm.name
        WHERE {conditions}
    """.format(conditions=conditions)

    data = frappe.db.sql(query, values, as_dict=True)

    # Define columns for report
    columns = [
        {"label": "Budget Head", "fieldname": "budget_head", "fieldtype": "Data", "width": 200},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Data", "width": 150},
        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 150},
        {"label": "Original Amount", "fieldname": "original_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Current Budget", "fieldname": "current_budget", "fieldtype": "Currency", "width": 150},
        {"label": "Used Budget", "fieldname": "used_budget", "fieldtype": "Currency", "width": 150},
        {"label": "Amended till now", "fieldname": "amended_till_now", "fieldtype": "Currency", "width": 150},
        {"label": "Balance Budget", "fieldname": "balance_budget", "fieldtype": "Currency", "width": 150},
        {"label": "Fiscal Year", "fieldname": "fiscal_year", "fieldtype": "Data", "width": 120},
        {"label": "UnPaid Purchase Order", "fieldname": "unpaid_purchase_order", "fieldtype": "Currency", "width": 200},
        {"label": "UnPaid Purchase Invoice", "fieldname": "unpaid_purchase_invoice", "fieldtype": "Currency", "width": 200},
        {"label": "Paid Payment Entry", "fieldname": "paid_payment_entry", "fieldtype": "Currency", "width": 200},
        {"label": "Company", "fieldname": "company", "fieldtype": "Data", "width": 200},
    ]

    return columns, data




