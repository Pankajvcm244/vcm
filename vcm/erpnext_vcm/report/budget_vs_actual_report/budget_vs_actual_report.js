// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.query_reports["Budget vs Actual Report"] = {
	"filters": [
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
        },
        {
            "fieldname": "cost_center",
            "label": "Cost Center",
            "fieldtype": "Link",
            "options": "Cost Center"
        },
        {
            "fieldname": "location",
            "label": "Location",
            "fieldtype": "Link",
            "options": "Budget Location"
        },
		{
            "fieldname": "fiscal_year",
            "label": "Fiscal year",
            "fieldtype": "Link",
            "options": "Fiscal Year"
        },
	]
};
