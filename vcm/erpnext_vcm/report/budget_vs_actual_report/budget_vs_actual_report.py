# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": "Fiscal Year", "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 100},        
        {"label": "Budget Head", "fieldname": "budget_head", "fieldtype": "Link", "options": "Budget Head", "width": 150},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 120},
        {"label": "Original Budget", "fieldname": "original_budget", "fieldtype": "Currency", "width": 130},
        {"label": "Current Budget", "fieldname": "current_budget", "fieldtype": "Currency", "width": 130},
        {"label": "Used Budget", "fieldname": "used_budget", "fieldtype": "Currency", "width": 130},
        {"label": "Used PI", "fieldname": "used_budget_pi", "fieldtype": "Currency", "width": 130},
        {"label": "Used PE", "fieldname": "used_budget_pe", "fieldtype": "Currency", "width": 130},
        {"label": "Used JV", "fieldname": "used_budget_jv", "fieldtype": "Currency", "width": 130},
        {"label": "Balance Budget", "fieldname": "balance_budget", "fieldtype": "Currency", "width": 130},
        {"label": "April", "fieldname": "Apr", "fieldtype": "Currency", "width": 100},
        {"label": "May", "fieldname": "May", "fieldtype": "Currency", "width": 100},
        {"label": "June", "fieldname": "Jun", "fieldtype": "Currency", "width": 100},
        {"label": "July", "fieldname": "Jul", "fieldtype": "Currency", "width": 100},
        {"label": "August", "fieldname": "Aug", "fieldtype": "Currency", "width": 100},
        {"label": "September", "fieldname": "Sep", "fieldtype": "Currency", "width": 100},
        {"label": "October", "fieldname": "Oct", "fieldtype": "Currency", "width": 100},
        {"label": "November", "fieldname": "Nov", "fieldtype": "Currency", "width": 100},
        {"label": "December", "fieldname": "Dec", "fieldtype": "Currency", "width": 100},
        {"label": "January", "fieldname": "Jan", "fieldtype": "Currency", "width": 100},
        {"label": "February", "fieldname": "Feb", "fieldtype": "Currency", "width": 100},
        {"label": "March", "fieldname": "Mar", "fieldtype": "Currency", "width": 100},
    ]



def get_data(filters):
    pi_conditions = ""
    pe_conditions = ""
    jv_conditions = ""
    outer_conditions = ""

    # Inner query filters for PI, PE, JV
    if filters.get("company"):
        company = filters["company"]
        pi_conditions += f" AND pi.company = '{company}'"
        pe_conditions += f" AND pe.company = '{company}'"
        jv_conditions += f" AND je.company = '{company}'"
        outer_conditions += f" AND v.company = '{company}'"
    if filters.get("cost_center"):
        cost_center = filters["cost_center"]
        pi_conditions += f" AND pi.cost_center = '{cost_center}'"
        pe_conditions += f" AND pe.cost_center = '{cost_center}'"
        jv_conditions += f" AND jea.cost_center = '{cost_center}'"
        outer_conditions += f" AND v.cost_center = '{cost_center}'"
    if filters.get("location"):
        location = filters["location"]
        pi_conditions += f" AND pi.location = '{location}'"
        pe_conditions += f" AND pe.location = '{location}'"
        jv_conditions += f" AND jea.location = '{location}'"
        outer_conditions += f" AND v.location = '{location}'"
    if filters.get("fiscal_year"):
        fiscal_year = filters["fiscal_year"]
        pi_conditions += f" AND pi.fiscal_year = '{fiscal_year}'"
        pe_conditions += f" AND pe.fiscal_year = '{fiscal_year}'"
        jv_conditions += f" AND jea.fiscal_year = '{fiscal_year}'"
        outer_conditions += f" AND v.fiscal_year = '{fiscal_year}'"

    query = f"""
        WITH expense_data AS (
            SELECT
                pi.budget_head,
                pi.cost_center,
                pi.location,
                pi.company,
                pi.fiscal_year,
                MONTH(pi.posting_date) AS month,
                pi.grand_total AS amount,
                'PI' AS source
            FROM `tabPurchase Invoice` pi
            WHERE pi.docstatus = 1 AND pi.budget_head IS NOT NULL {pi_conditions}

            UNION ALL

            SELECT
                pe.budget_head,
                pe.cost_center,
                pe.location,
                pe.company,
                pe.fiscal_year,
                MONTH(pe.posting_date) AS month,
                pe.paid_amount AS amount,
                'PE' AS source
            FROM `tabPayment Entry` pe
            LEFT JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
            WHERE pe.docstatus = 1
                AND pe.budget_head IS NOT NULL
                AND (
                    per.reference_doctype IS NULL
                    OR (per.reference_doctype NOT IN ('Purchase Invoice', 'Purchase Order'))
                )
                {pe_conditions}


            UNION ALL

            SELECT
                jea.budget_head,
                jea.cost_center,
                jea.location,
                je.company,
                jea.fiscal_year,
                MONTH(je.posting_date) AS month,
                CASE 
                    WHEN jea.debit > 0 THEN jea.debit
                    WHEN jea.credit > 0 THEN -jea.credit
                    ELSE 0
                END AS amount,
                'JV' AS source
            FROM `tabJournal Entry` je
            LEFT JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
            WHERE je.docstatus = 1
                AND jea.budget_head IS NOT NULL 
                AND jea.account IN (SELECT name FROM `tabAccount` WHERE root_type = 'Expense')
                {jv_conditions}
        )

        SELECT 
            b.budget_head,
            v.cost_center,
            v.location,
            v.company,
            v.fiscal_year,
            COALESCE(b.original_amount, 0) AS original_budget,
            COALESCE(b.current_budget, 0) AS current_budget,

            SUM(CASE WHEN e.month = 4 THEN e.amount ELSE 0 END) AS Apr,
            SUM(CASE WHEN e.month = 5 THEN e.amount ELSE 0 END) AS May,
            SUM(CASE WHEN e.month = 6 THEN e.amount ELSE 0 END) AS Jun,
            SUM(CASE WHEN e.month = 7 THEN e.amount ELSE 0 END) AS Jul,
            SUM(CASE WHEN e.month = 8 THEN e.amount ELSE 0 END) AS Aug,
            SUM(CASE WHEN e.month = 9 THEN e.amount ELSE 0 END) AS Sep,
            SUM(CASE WHEN e.month = 10 THEN e.amount ELSE 0 END) AS Oct,
            SUM(CASE WHEN e.month = 11 THEN e.amount ELSE 0 END) AS Nov,
            SUM(CASE WHEN e.month = 12 THEN e.amount ELSE 0 END) AS `Dec`,
            SUM(CASE WHEN e.month = 1 THEN e.amount ELSE 0 END) AS Jan,
            SUM(CASE WHEN e.month = 2 THEN e.amount ELSE 0 END) AS Feb,
            SUM(CASE WHEN e.month = 3 THEN e.amount ELSE 0 END) AS Mar,

            COALESCE(SUM(e.amount), 0) AS used_budget,
            COALESCE(SUM(CASE WHEN e.source = 'PI' THEN e.amount ELSE 0 END), 0) AS used_budget_pi,
            COALESCE(SUM(CASE WHEN e.source = 'PE' THEN e.amount ELSE 0 END), 0) AS used_budget_pe,
            COALESCE(SUM(CASE WHEN e.source = 'JV' THEN e.amount ELSE 0 END), 0) AS used_budget_jv,
            
            COALESCE(b.current_budget, 0) - COALESCE(SUM(e.amount), 0) AS balance_budget

        FROM `tabVCM Budget` v
        LEFT JOIN `tabVCM Budget Child Table` b ON b.parent = v.name
        LEFT JOIN expense_data e ON 
            e.budget_head = b.budget_head AND
            e.cost_center = v.cost_center AND
            e.location = v.location AND
            e.company = v.company AND
            e.fiscal_year = v.fiscal_year

        WHERE 1=1 {outer_conditions}

        GROUP BY 
            b.budget_head,
            v.cost_center,
            v.location,
            v.company,
            v.fiscal_year,
            b.original_amount,
            b.current_budget

        HAVING used_budget > 0 OR COALESCE(b.current_budget, 0) > 0

        ORDER BY b.budget_head, v.fiscal_year, v.cost_center
    """

    return frappe.db.sql(query, as_dict=True)
