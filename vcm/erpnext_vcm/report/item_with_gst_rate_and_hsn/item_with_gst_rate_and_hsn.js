// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.query_reports["ITEM With GST Rate and HSN"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"width": 80,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List",
			"reqd": 1,
			"width": 80,
			"default": frappe.defaults.get_user_default("Price List")
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 80
		},
	],
};
