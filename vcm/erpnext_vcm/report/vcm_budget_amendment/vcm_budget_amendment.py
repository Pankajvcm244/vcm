# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data

def get_columns():
    return [
       
        {"fieldname": "company", "label": _("Company"), "fieldtype": "Link", "options": "Company", "width": 150},    
        {"fieldname": "fiscal_year", "label": _("Fiscal Year"), "fieldtype": "Data", "width": 120},
        {"fieldname": "cost_center", "label": _("Cost Center"), "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"fieldname": "budget_head", "label": _("Budget Head"), "fieldtype": "Select", "options": "Salary\nCAPEX\nRepair and Maintenance\nElectricity", "width": 150},
		{"fieldname": "original_amount", "label": _("Original Budget"), "fieldtype": "Float", "width": 150},
        {"fieldname": "amended_till_now", "label": _("Amended Till Now"), "fieldtype": "Float", "width": 150},
        {"fieldname": "proposed_amendment", "label": _("Amended Amount"), "fieldtype": "Float", "width": 150},
        {"fieldname": "current_budget", "label": _("Current Budget"), "fieldtype": "Float", "width": 150},
        {"fieldname": "used_budget", "label": _("Used Budget"), "fieldtype": "Float", "width": 150},
        {"fieldname": "balance_budget", "label": _("Balance Budget"), "fieldtype": "Float", "width": 150},
        {"fieldname": "proposed_by", "label": _("Amended By"), "fieldtype": "Link", "options": "Employee", "width": 150},
        {"fieldname": "amendment_date", "label": "Amendment Date", "fieldtype": "Date"}  # 🔹 Include Date
	]

def get_data(filters):
    query = """
        SELECT
            ba.name,
            ba.company,
            ba.fiscal_year,
            ba.cost_center,
            DATE(ba.modified) AS amendment_date,           
            bai.original_amount,
            bai.current_budget,
            bai.used_budget,
            bai.balance_budget, 
            bai.amended_till_now, 
            bai.budget_head,
            bai.proposed_amendment, 
            bai.proposed_by,         
            (
              SELECT GROUP_CONCAT(CONCAT(bai.budget_head, ': ', bai.proposed_by) SEPARATOR ', ')
              FROM `tabVCM Budget Amendment Child Table` bai
              WHERE bai.parent = ba.name
            ) AS amendment_details
        FROM `tabVCM Budget Amendment` ba
        JOIN `tabVCM Budget Amendment Child Table` bai ON bai.parent = ba.name
        WHERE ba.docstatus IN (0, 1)
        {conditions}
        ORDER BY ba.cost_center DESC
    """
    
    conditions, values = [], {}
    if filters.get("company"):
        conditions.append("ba.company = %(company)s")
        values["company"] = filters.get("company")
    if filters.get("fiscal_year"):
        conditions.append("ba.fiscal_year = %(fiscal_year)s")
        values["fiscal_year"] = filters.get("fiscal_year")
    if filters.get("cost_center"):
        conditions.append("ba.cost_center = %(cost_center)s")
        values["cost_center"] = filters.get("cost_center")
    
    condition_str = ""
    if conditions:
        condition_str = " AND " + " AND ".join(conditions)
    
    query = query.format(conditions=condition_str)
    return frappe.db.sql(query, values, as_dict=1)
