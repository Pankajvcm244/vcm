frappe.query_reports["VCM Mode of Payment & Top Performing Items"] = {
    filters: [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -1) // Two days ago
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -1) // Two days ago
        },
        {
            "fieldname": "pos_profile",
            "label": "POS Profile",
            "fieldtype": "Link",
            "options": "POS Profile",
            "default": "Gita Counter POS"
        }
    ]
};

