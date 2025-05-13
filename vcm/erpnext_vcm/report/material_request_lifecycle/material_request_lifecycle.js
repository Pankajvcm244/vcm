// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

// frappe.query_reports["Material Request Lifecycle"] = {
// 	"filters": [

// 	]
// };





//#####################################################   Default set i mont rnage and set TSF And Depart ment #################


frappe.query_reports["Material Request Lifecycle"] = {
    "filters": [
      {
        "fieldname": "company",
        "label": "Company",
        "fieldtype": "Link",
        "options": "Company",
        "default": "TOUCHSTONE FOUNDATION VRINDAVAN - NCR"
      },
      {
        "fieldname": "department",
        "label": "Department",
        "fieldtype": "Link",
        "options": "Department",
        "default": "Merchandise - TSF"
      },
      {
        "fieldname": "set_warehouse",
        "label": "Set Warehouse",
        "fieldtype": "Link",
        "options": "Warehouse"
      },
      {
        "fieldname": "from_date",
        "label": "From Date",
        "fieldtype": "Date",
        "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
      },
      {
        "fieldname": "to_date",
        "label": "To Date",
        "fieldtype": "Date",
        "default": frappe.datetime.get_today()
      }
    ]
  }
  