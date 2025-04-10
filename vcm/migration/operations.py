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


def update_donor_receipts():
    for d in frappe.get_all(
        "Donation Receipt",
        filters={
            "donor": ["LIKE", "%%LDNR%%"],
            "company": ["!=", "HARE KRISHNA MOVEMENT LUCKNOW"],
        },
        fields=["name", "donor"],
    ):
        print(d["donor"])
        frappe.db.set_value(
            "Donation Receipt", d["name"], "donor", d["donor"], update_modified=False
        )


@frappe.whitelist()
def update_series():
    exisiting = {}
    for s in frappe.db.sql("SELECT * FROM `tabSeries` WHERE 1", as_dict=1):
        exisiting[s["name"]] = s["current"]

    data = json.loads(frappe.request.data)
    for k, v in data.items():
        if k in exisiting:
            if exisiting[k] == 1:
                frappe.db.sql(
                    f"UPDATE `tabSeries` SET current = '{v}' WHERE name = '{k}' "
                )
        else:
            frappe.db.sql(
                f"INSERT INTO `tabSeries` (name, current) VALUES ('{k}','{v}'); "
            )


def remove_tx_info():
    frappe.db.sql(
        """
        UPDATE `tabDonation Receipt`
        SET bank_account = NULL,
            bank_transaction = NULL,
            bounce_transaction = NULL,
            donation_account = NULL,
            cash_account = NULL,
            tds_account = NULL,
            gateway_expense_account = NULL,
            cost_center = NULL,
            budget_head = NULL
        WHERE owner = "migration@vcmerp.in"
        """
    )

    frappe.db.comit()
def correct_donors():
    for r in frappe.get_all(
        "Donation Receipt",
        filters={"company":"HARE KRISHNA MOVEMENT LUCKNOW"},
        fields=["name", "donor"],
    ):
        frappe.db.set_value("Donation Receipt", r["name"], "donor", f"L{r['donor']}")

def correct_donors_2():
    for r in frappe.get_all(
        "Donor",
        filters={
            "creation": [">=", "2025-04-09"],
            "owner": "migration@vcmerp.in",
        },
        pluck="name",
    ):
        if r.startswith("L"):
            try:
                frappe.rename_doc("Donor", r, f"O{r[1:]}")
            except Exception as e:
                print(e)
                # current_name = frappe.db.get_value("Donor", r, "full_name")
                # existing_name = frappe.db.get_value("Donor", r[1:], "full_name")
                # print(
                #     f"Current Name : {current_name} || Exisiting Name : {existing_name}"
                # )
                # if current_name == existing_name:
                #     print("Matched")
                #     frappe.delete_doc("Donor", r)
                #     frappe.db.commit()
