# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data

def get_columns():
    months = [
        {"label": "Apr", "fieldname": "Apr"},
        {"label": "May", "fieldname": "May"},
        {"label": "Jun", "fieldname": "Jun"},
        {"label": "Jul", "fieldname": "Jul"},
        {"label": "Aug", "fieldname": "Aug"},
        {"label": "Sep", "fieldname": "Sep"},
        {"label": "Oct", "fieldname": "Oct"},
        {"label": "Nov", "fieldname": "Nov"},
        {"label": "Dec", "fieldname": "Dec"},
        {"label": "Jan", "fieldname": "Jan"},
        {"label": "Feb", "fieldname": "Feb"},
        {"label": "Mar", "fieldname": "Mar"},
    ]
    
    columns = [
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 180},
        {"label": "Fiscal Year", "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 120},
        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 100},
        {"label": "Budget Head", "fieldname": "budget_head", "fieldtype": "Link", "options": "Budget Account", "width": 200},
        {"label": "Original Budget", "fieldname": "original_budget", "fieldtype": "Currency", "width": 140},
        {"label": "Current Budget", "fieldname": "current_budget", "fieldtype": "Currency", "width": 140},
    ]

    # Add month-wise columns
    for month in months:
        columns.append({"label": month["label"], "fieldname": month["fieldname"], "fieldtype": "Currency", "width": 100})

    # Used budget and balance
    columns += [
        {"label": "Used Budget", "fieldname": "used_budget", "fieldtype": "Currency", "width": 140},
        {"label": "Balance Budget", "fieldname": "balance_budget", "fieldtype": "Currency", "width": 140},
    ]

    return columns

def get_data(filters):
	pi_conditions = ""
	pe_conditions = ""
	jv_conditions = ""

	# Dynamic filter conditions
	if filters.get("company"):
		company = filters["company"]
		pi_conditions += f" AND pi.company = '{company}'"
		pe_conditions += f" AND pe.company = '{company}'"
		jv_conditions += f" AND je.company = '{company}'"
	if filters.get("cost_center"):
		cost_center = filters["cost_center"]
		pi_conditions += f" AND pi.cost_center = '{cost_center}'"
		pe_conditions += f" AND pe.cost_center = '{cost_center}'"
		jv_conditions += f" AND jea.cost_center = '{cost_center}'"
	if filters.get("location"):
		location = filters["location"]
		pi_conditions += f" AND pi.location = '{location}'"
		pe_conditions += f" AND pe.location = '{location}'"
		jv_conditions += f" AND jea.location = '{location}'"
	if filters.get("fiscal_year"):
		fiscal_year = filters["fiscal_year"]
		pi_conditions += f" AND pi.fiscal_year = '{fiscal_year}'"
		pe_conditions += f" AND pe.fiscal_year = '{fiscal_year}'"
		jv_conditions += f" AND jea.fiscal_year = '{fiscal_year}'"

	query = f"""
		WITH expense_data AS (
			SELECT
				pii.budget_head,
				pi.cost_center,
				pi.location,
				pi.company,
				pi.fiscal_year,
				MONTH(pi.posting_date) AS month,
				pi.grand_total AS amount
			FROM `tabPurchase Invoice` pi
			LEFT JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
			WHERE pi.docstatus = 1 AND pii.budget_head IS NOT NULL {pi_conditions}

			UNION ALL

			SELECT
				pe.budget_head,
				pe.cost_center,
				pe.location,
				pe.company,
				pe.fiscal_year,
				MONTH(pe.posting_date) AS month,
				pe.paid_amount AS amount
			FROM `tabPayment Entry` pe
			WHERE pe.docstatus = 1 AND pe.budget_head IS NOT NULL {pe_conditions}

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
				END AS amount
			FROM `tabJournal Entry` je
			LEFT JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
			WHERE je.docstatus = 1
				AND jea.budget_head IS NOT NULL 
				AND jea.account IN (SELECT name FROM `tabAccount` WHERE root_type = 'Expense')
				{jv_conditions}
		)

		SELECT 
			e.budget_head,
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
			SUM(e.amount) AS used_budget,
			COALESCE(b.current_budget, 0) - SUM(e.amount) AS balance_budget
		FROM expense_data e
		LEFT JOIN `tabVCM Budget` v ON 
			e.cost_center = v.cost_center AND
			e.location = v.location AND
			e.company = v.company AND
			e.fiscal_year = v.fiscal_year
		LEFT JOIN `tabVCM Budget Child Table` b ON 
			b.parent = v.name AND
			e.budget_head = b.budget_head
		GROUP BY 
			e.budget_head,
			v.cost_center,
			v.location,
			v.company,
			v.fiscal_year,
			b.original_amount,
			b.current_budget
		HAVING used_budget > 0 OR COALESCE(b.current_budget, 0) > 0
		ORDER BY e.budget_head, v.fiscal_year, v.cost_center
	"""

	return frappe.db.sql(query, filters, as_dict=True)
