#bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.dhananjaya.test.numberseries

import frappe
#import os

import logging
logging.basicConfig(level=logging.DEBUG)

def numberseries():
    #meta = frappe.get_all("DocType", filters={"name": "Donation Receipt"})
    # meta = frappe.get_meta("Donation Receipt")
    # fields = [df.fieldname for df in meta.fields]
    # print(fields)
    # naming_series_field = frappe.get_meta("Donation Receipt").get_field("receipt_series")
    # if naming_series_field:
    #     print(naming_series_field.options)
    # else:
    #     print("Naming Series field not found in Donation Receipt.")

    current_value = frappe.db.get_value("Series", "HKMV-DR2504", "current")
    print(f"Current Counter: {current_value}")

    #naming_series = frappe.get_meta("Donation Receipt").get_field("naming_series").options
    #frappe.msgprint(f"Donation Receipt Series: {naming_series}")
    #print(f"Seva Type already exists. {meta}")
