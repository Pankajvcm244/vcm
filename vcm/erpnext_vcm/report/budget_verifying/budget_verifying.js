// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Verifying"] = {
    "filters": [
        {
            "fieldname": "document_type",
            "label": "Document Type",
            "fieldtype": "Select",
            "options": ["Purchase Order", "Purchase Invoice", "Payment Entry", "Journal Entry"],
            "default": "Purchase Order",
            "reqd": 1,
        },
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company"
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 1,
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "cost_center",
            "label": "Cost Center",
            "fieldtype": "Link",
            "options": "Cost Center"
        },
        {
            "fieldname": "location",
            "label": "Budget Location",
            "fieldtype": "Link",
            "options": "Budget Location"
        },
        {
            "fieldname": "budget_head",
            "label": "Budget Head",
            "fieldtype": "Link",
            "options": "Budget Head"
        }
    ]
};
