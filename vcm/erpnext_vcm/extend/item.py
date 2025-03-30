import frappe
from frappe.utils.background_jobs import enqueue
from frappe.utils import time_diff_in_hours, time_diff_in_seconds, date_diff, flt
from frappe.model.workflow import apply_workflow


@frappe.whitelist()
def fetch_item_code(item_group):
    if frappe.db.exists("Item Group", item_group):
        item_grp_doc = frappe.get_doc("Item Group", item_group)
        series = item_grp_doc.get("item_code_series")
        if series is not None and series.strip() != "":
            codes = frappe.db.sql(
                """
						select CAST(TRIM(LEADING '{}-' FROM item_code ) AS int) AS new_code 
						from `tabItem`
						where item_code LIKE '{}-%'
						order by new_code DESC
							""".format(
                    series, series
                ),
                as_dict=1,
            )

            last_code = codes[0]["new_code"] if len(codes) > 0 else 1
            last_code = str(last_code + 1).zfill(4)
            return series + "-" + last_code
    return 0