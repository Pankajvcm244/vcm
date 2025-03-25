

frappe.query_reports["VCM Budget Usage"] = {
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
        // {
        //     "fieldname": "fiscal_year",
        //     "label": "Fiscal Year",
        //     "fieldtype": "Data"
        // }
    ]
};

