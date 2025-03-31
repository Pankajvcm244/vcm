import json
import frappe


@frappe.whitelist()
def create_doc():
    # data = json.loads(kwargs)
    data = json.loads(frappe.request.data)
    s = frappe.get_doc(data)
    s.insert(ignore_permissions=True, set_name=data["name"], ignore_links=True)


def delete_donors():
    for i, d in enumerate(frappe.get_all("Donor", pluck="name")):
        if i > 15:
            break
        print(f"Processing : {i+1}")
        frappe.delete_doc("Donor", d, delete_permanently=True)


def delete_donors_requests():
    for i, d in enumerate(frappe.get_all("Donor Creation Request", pluck="name")):
        if i > 5000:
            break
        print(f"Processing : {i+1}")
        doc = frappe.get_doc("Donor Creation Request", d)
        if doc.docstatus == 1:
            doc.cancel()
        # doc.delete(delete_permanently=True)
        frappe.delete_doc("Donor Creation Request", d, delete_permanently=True)
