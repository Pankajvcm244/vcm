# bench --site erp.vcmerp.in execute vcm.migration.operations.delete_donors_requests

import json
from mimetypes import guess_type
import frappe


@frappe.whitelist()
def create_doc():
    data = json.loads(frappe.request.data)
    s = frappe.get_doc(data)
    s.insert(ignore_permissions=True, set_name=data["name"], ignore_links=True)


@frappe.whitelist()
def create_doc_with_file():
    data = frappe.request.data
    doc = frappe.get_doc(data)
    doc.insert(ignore_permissions=True, set_name=data["name"], ignore_links=True)
    return
    files = frappe.request.files
    if "image" in files:
        file = files["image"]
        content = file.stream.read()
        fileref = file.filename
        content_type = guess_type(fileref)[0]
        image_doc = frappe.get_doc(
            {
                "doctype": "File",
                "attached_to_doctype": doc.doctype,
                "attached_to_name": doc.name,
                "attached_to_field": "payment_screenshot",
                "folder": "Home",
                "file_name": fileref,
                "is_private": 0,
                "content": content,
            }
        ).save(ignore_permissions=1)
        frappe.db.commit()
        doc.reload()


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


def delete_donation_receipts():
    for i, d in enumerate(frappe.get_all("Donation Receipt", pluck="name")):
        if i > 5000:
            break
        print(f"Processing : {i+1}")
        doc = frappe.get_doc("Donation Receipt", d)
        if doc.docstatus == 1:

            doc.cancel()
        # doc.delete(delete_permanently=True)
        frappe.delete_doc(
            "Donation Receipt",
            d,
            delete_permanently=True,
            ignore_missing=True,
            ignore_on_trash=True,
        )


@frappe.whitelist()
def update_receipts():
    data = json.loads(frappe.request.data)
    for key, value in data.items():
        frappe.db.set_value("Donation Receipt", key, "receipt_date", value)
