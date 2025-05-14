# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
import datetime
from frappe.model.document import Document
from frappe.model.naming import getseries
from frappe.utils import nowdate


class SupplierPaymentRequest(Document):
    def autoname(self):
        today = datetime.datetime.today()
        day = today.strftime("%d")
        month = today.strftime("%m")
        year = today.strftime("%y")
        company_name = frappe.get_doc("Company", self.company)
        company_abbr = company_name.abbr
        # Create the prefix with warehouse, current date (day, month, year)
        prefix = f"{company_abbr}-PaymentReq-{day}{month}{year}-"
        # Set the name using the series (getseries)
        self.name = prefix + getseries(prefix, 2)
    
    def validate(self):
        # Check if the request type is "Advance Payments (against PO)"
        if self.request_type == "Advance Payments (against PO)":
            validate_supplier_po_payment_request(self)

    def on_submit(self):
        # Check if the request type is "Advance Payments (against PO)"
        if self.request_type == "Advance Payments (against PO)":
            create_payment_entry_from_request(self.name)

        # Check if the request type is "Credit Payments (against Invoice)"
        elif self.request_type == "Credit Payments (against Invoice)":
            create_payment_entry_for_selected_invoices(self.name)

        # else:
        #     frappe.throw(_("Invalid request type."))            

@frappe.whitelist()
def create_payment_entry_from_request(docname):
    doc = frappe.get_doc("Supplier Payment Request", docname)

    # Preconditions
    # if doc.docstatus != 1:
    #     frappe.throw(_("Document must be submitted."))

    # if doc.status != "Approved":
    #     frappe.throw(_("Only approved requests are processed."))

    if doc.request_type != "Advance Payments (against PO)":
        frappe.throw(("Request type must be 'Advance Payment (against PO)'."))

    if not doc.purchase_order:
        frappe.throw(("Purchase Order is required."))

    # Check Purchase Order status
    po = frappe.get_doc("Purchase Order", doc.purchase_order)
    if po.docstatus != 1:
        frappe.throw(("Linked Purchase Order must be submitted."))

    if po.status == "Closed" or po.status == "Completed":
        frappe.throw(("Cannot process payment for a closed or completed Purchase Order."))

    # Check if Payment Entry already exists
    existing_pe = frappe.get_all("Payment Entry",
        filters={
            "reference_no": doc.name,
            "reference_date": doc.modified,
            "party": doc.supplier,
            "party_type": "Supplier",
            "docstatus": 1
        },
        pluck="name"
    )

    if existing_pe:
        return f"Payment Entry {existing_pe[0]} already exists."

    # Get accounts
    # paid_from_account = frappe.get_value("Company", doc.company, "default_bank_account")
    paid_from_account = "2320 - Canara Bank- Annakoot & Brajras - TSF"
    if not paid_from_account:
        frappe.throw(("Default bank account not set in Company"))

    # paid_to_account = frappe.get_value("Account", {
    #     "account_type": "Payable",
    #     "company": doc.company
    # })
    #remove this hard coding later on Pankaj
    paid_to_account = "Sundry Creditors - Suppliers - TSF"
    if not paid_to_account:
        frappe.throw(("No payable account found for company."))

    # Create Payment Entry
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Pay"
    pe.party_type = "Supplier"
    pe.cost_center = doc.cost_center
    pe.fiscal_year = doc.fiscal_year
    pe.party = doc.supplier
    pe.company = doc.company
    pe.paid_from = paid_from_account
    pe.paid_to = paid_to_account
    pe.paid_amount = doc.payment_requested
    pe.received_amount = doc.payment_requested
    pe.reference_no = doc.name
    pe.reference_date = doc.modified
    pe.posting_date = frappe.utils.nowdate()

    pe.append("references", {
        "reference_doctype": "Purchase Order",
        "reference_name": doc.purchase_order,
        "allocated_amount": doc.payment_requested
    })
    pe.insert(ignore_permissions=True)
    #pe.submit()
    return f"Payment Entry {pe.name} created successfully."

@frappe.whitelist()
def validate_supplier_po_payment_request(doc):
    advance_balance = doc.remaining_advance or 0
    if doc.request_type == "Advance Payments (against PO)" and doc.payment_requested:
        if doc.payment_requested > advance_balance :
            frappe.throw((
                f"Requested advance amount ({doc.payment_requested }) exceeds the remaining advance balance ({doc.remaining_advance}) "
                f"for Purchase Order {doc.purchase_order}."
            ))
            
@frappe.whitelist()
def get_payment_entries_for_po(purchase_order):
    if not purchase_order:
        return []

    # Get related Payment Entry References
    references = frappe.get_all(
        "Payment Entry Reference",
        filters={
            "reference_doctype": "Purchase Order",
            "reference_name": purchase_order
        },
        fields=["parent"]
    )

    parent_names = list(set(ref["parent"] for ref in references))

    if not parent_names:
        return []

    # Fetch payment entries
    payment_entries = frappe.get_all(
        "Payment Entry",
        filters={
            "name": ["in", parent_names],
            "docstatus": 1,
            "party_type": "Supplier"
        },
        fields=["name", "posting_date", "paid_amount"]
    )
    return payment_entries

@frappe.whitelist()
def create_payment_entry_for_selected_invoices(docname):
    doc = frappe.get_doc("Supplier Payment Request", docname)

    if doc.request_type != "Credit Payments (against Invoice)":
        frappe.throw(("Request Type must be 'Credit Payments (against Invoice)'."))

    references = []
    total_amount = 0

    for row in doc.pending_invoice_detail:
        if row.include_in_payment:
            references.append({
                "reference_doctype": "Purchase Invoice",
                "reference_name": row.invoice,
                "allocated_amount": row.outstanding_amount
            })      
    if not references:
        frappe.throw(("Please select at least one invoice to create Payment Entry."))

    supplier = frappe.db.get_value("Purchase Invoice", references[0]["reference_name"], "supplier")
    company = doc.company

    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Pay"
    pe.party_type = "Supplier"
    pe.party = supplier
    pe.posting_date = nowdate()
    pe.company = company
    pe.cost_center = doc.cost_center
    pe.fiscal_year = doc.fiscal_year
    # pe.paid_from = frappe.get_cached_value("Company", company, "default_bank_account")
    # pe.paid_to = frappe.get_cached_value("Company", company, "default_payable_account")
    pe.paid_from = "2320 - Canara Bank- Annakoot & Brajras - TSF"
    pe.paid_to = "Sundry Creditors - Suppliers - TSF"
    #remove this hard coding later on Pankaj
    
    pe.mode_of_payment = "Bank Transfer"

    for row in doc.pending_invoice_detail:
        if row.include_in_payment:
            if not supplier:
                supplier = frappe.db.get_value("Purchase Invoice", row.invoice, "supplier")
                pe.party = supplier

            pe.append("references", {
                "reference_doctype": "Purchase Invoice",
                "reference_name": row.invoice,
                "allocated_amount": row.outstanding_amount
            })

            total_amount += row.outstanding_amount
    pe.paid_amount = total_amount
    pe.received_amount = total_amount
    pe.reference_no = doc.name
    pe.reference_date = nowdate()

    pe.insert(ignore_permissions=True)
    #pe.submit()

    return pe.name