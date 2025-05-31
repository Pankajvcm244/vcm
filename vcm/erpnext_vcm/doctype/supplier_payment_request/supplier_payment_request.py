# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
import datetime
from frappe.model.document import Document
from frappe.model.naming import getseries
from frappe.utils import nowdate

from erpnext.accounts.party import get_party_account

from vcm.erpnext_vcm.doctype.supplier_payment_request.preq_alm.preqalm import (
    assign_and_notify_next_preq_authority,
    get_preq_alm_level,
)

from frappe.workflow.doctype.workflow_action.workflow_action import (
    get_doc_workflow_state,
)

import logging
logging.basicConfig(level=logging.DEBUG)

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
    
    def before_save(self):
        #logging.debug(f"in PREQ before_save")
        self.refresh_preq_alm()
    
    def on_update(self):
        #logging.debug(f"in PREQ on_update")        
        assign_and_notify_next_preq_authority(self)

    def validate(self):
        #logging.debug(f"in PREQ validate")
        # Check if the request type is "Advance Payments (against PO)"
        if self.request_type == "Advance Payments (against PO)":
            # validate if amount is more than mentioned in PO
            validate_supplier_po_payment_request(self)

    def on_submit(self):
        #logging.debug(f"in PREQ on_submit")
        # Check if the request type is "Advance Payments (against PO)"
        if self.request_type == "Advance Payments (against PO)":
            create_payment_entry_from_request(self.name)
        # Check if the request type is "Credit Payments (against Invoice)"
        elif self.request_type == "Credit Payments (against Invoice)":
            create_payment_entry_for_selected_invoices(self.name)        
        elif self.request_type == "Adhoc Payment":
            create_payment_entry_from_adhoc_request(self.name)
    
    def refresh_preq_alm(self):
        #logging.debug(f"in PREQ refresh_preq_alm")
        if hasattr(self, "department") and self.department == "":
            frappe.throw("Department is not set.")
        alm_level = get_preq_alm_level(self)
        if alm_level is not None:
            self.l1_approving_authority = alm_level.l1_approver
            self.l2_approving_authority = alm_level.l2_approver
            self.l3_approving_authority = alm_level.l3_approver
            self.final_approving_authority = alm_level.final_approver
            #logging.debug(f"in PREQ refresh_preq_alm {self.name}, {self.l1_approving_authority}, {self.l2_approving_authority}, {self.l3_approving_authority}, {self.final_approving_authority}")
        else:
            frappe.throw("ALM Levels are not set for Payment Req in this document")

@frappe.whitelist()
def create_payment_entry_from_request(docname):
    #logging.debug(f"**********in PREQ create_payment_entry_from_request {docname}  ******************")
    doc = frappe.get_doc("Supplier Payment Request", docname)

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

    # Create Payment Entry
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Pay"
    pe.party_type = "Supplier"
    pe.cost_center = po.cost_center
    pe.fiscal_year = po.fiscal_year
    pe.budget_head = po.budget_head
    pe.location = po.location
    pe.party = doc.supplier
    pe.company = doc.company
    # Get accounts
    pe.paid_to = get_party_account("Supplier", doc.supplier, doc.company)
    pe.paid_from = frappe.get_value("Company", doc.company, "default_cash_account")
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
def create_payment_entry_from_adhoc_request(docname):
    doc = frappe.get_doc("Supplier Payment Request", docname)    

    if doc.request_type != "Adhoc Payment":
        frappe.throw(("Request type must be 'Adhoc Payment'."))    
    
    pe = frappe.new_doc("Payment Entry")
    # Create Payment Entry
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Pay"
    pe.party_type = "Supplier"
    pe.cost_center = doc.cost_center
    pe.fiscal_year = doc.fiscal_year
    pe.budget_head = doc.budget_head
    pe.location = doc.location
    pe.party = doc.supplier
    pe.company = doc.company
    # Get accounts 
    pe.paid_to = get_party_account("Supplier", doc.supplier, doc.company)
    pe.paid_from = frappe.get_value("Company", doc.company, "default_cash_account")    
    pe.source_exchange_rate = 1.0
    pe.paid_amount = doc.adhoc_amount
    pe.received_amount = doc.adhoc_amount
    pe.reference_no = doc.name
    pe.reference_date = doc.modified
    pe.posting_date = frappe.utils.nowdate()    
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
        frappe.throw("Request Type must be 'Credit Payments (against Invoice)'.")

    invoice_groups = {}

    # Step 1: Group invoices by dimension combinations (including blanks)
    for row in doc.pending_invoice_detail:
        if not row.include_in_payment:
            continue

        invoice_doc = frappe.get_doc("Purchase Invoice", row.invoice)

        # Use row-level or fallback to Supplier Payment Request-level
        cost_center = getattr(row, "cost_center", None) or doc.get("cost_center")
        location = getattr(row, "location", None) or doc.get("location")
        fiscal_year = getattr(row, "fiscal_year", None) or doc.fiscal_year  # always taken from doc
        supplier = invoice_doc.supplier
        budget_head = getattr(row, "budget_head", None) or doc.get("budget_head")


        # Keep blank values in the key
        group_key = (supplier, cost_center, location, fiscal_year, budget_head)

        invoice_groups.setdefault(group_key, []).append({
            "invoice": row.invoice,
            "outstanding_amount": row.amount_to_be_paid
        })

    if not invoice_groups:
        frappe.throw("Please select at least one invoice to create Payment Entry.")

    created_entries = []

    # Step 2: Create a Payment Entry per unique group
    for key, invoice_list in invoice_groups.items():
        supplier, cost_center, location, fiscal_year, budget_head = key
        total_amount = sum(float(inv["outstanding_amount"]) for inv in invoice_list)

        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.party_type = "Supplier"
        pe.party = supplier
        pe.posting_date = nowdate()
        pe.company = doc.company

        # Dimensions — set only if not None
        if cost_center:
            pe.cost_center = cost_center
        if location:
            pe.location = location
        if fiscal_year:
            pe.fiscal_year = fiscal_year
        if budget_head:
            pe.budget_head = budget_head

        # Customize accounts or make dynamic
        pe.paid_to = get_party_account("Supplier", doc.supplier, doc.company)
        pe.paid_from = frappe.get_value("Company", doc.company, "default_cash_account")
        pe.mode_of_payment = "Bank Transfer"

        for inv in invoice_list:
            pe.append("references", {
                "reference_doctype": "Purchase Invoice",
                "reference_name": inv["invoice"],
                "allocated_amount": float(inv["outstanding_amount"])
            })

        pe.paid_amount = total_amount
        pe.received_amount = total_amount
        pe.reference_no = doc.name
        pe.reference_date = nowdate()

        pe.insert(ignore_permissions=True)
        # pe.submit()

        created_entries.append(pe.name)

    return created_entries

@frappe.whitelist()
def get_purchase_orders_without_invoice_or_payment(doctype, txt, searchfield, start, page_len, filters):
    #  We want to show Purchase Orders that:
        # Have no Purchase Invoice
        # Have no Payment Entry except if only cancelled PEs (docstatus = 2) exist, SO PE evein in draft will remove from PO list
    company = filters.get("company")
    department = filters.get("department")

    return frappe.db.sql("""
        SELECT po.name, po.supplier_name
        FROM `tabPurchase Order` po
        LEFT JOIN `tabPurchase Invoice Item` pii 
            ON pii.purchase_order = po.name
        WHERE pii.name IS NULL
            AND NOT EXISTS (
                SELECT 1
                FROM `tabPayment Entry Reference` per
                JOIN `tabPayment Entry` pe ON pe.name = per.parent
                WHERE per.reference_name = po.name
                  AND per.reference_doctype = 'Purchase Order'
                  AND pe.docstatus != 2  -- Exclude only cancelled Payment Entries
            )
            AND po.docstatus = 1
            AND po.status NOT IN ('Closed', 'Completed')
            AND po.custom_advance_amount > 0
            AND po.company = %(company)s
            AND po.department = %(department)s
            AND (po.name LIKE %(txt)s OR po.supplier_name LIKE %(txt)s)
        GROUP BY po.name
        ORDER BY po.name ASC
        LIMIT %(start)s, %(page_len)s
    """, {
        "company": company,
        "department": department,
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len
    })


@frappe.whitelist()
def get_unlinked_payment_sum(supplier, company):
    #logging.debug(f"in get_unlinked_payment_sum with supplier: {supplier}, company: {company}")
    result = frappe.db.sql("""
        SELECT SUM(pe.unallocated_amount) AS total_unsettled
        FROM `tabPayment Entry` pe
        WHERE pe.party_type = 'Supplier'
          AND pe.party = %(supplier)s
          AND pe.company = %(company)s
          AND pe.docstatus = 1
          AND pe.payment_type = 'Pay'
          AND pe.unallocated_amount > 0
          AND NOT EXISTS (
              SELECT 1 FROM `tabPayment Entry Reference` per
              WHERE per.parent = pe.name
                AND per.reference_doctype = 'Purchase Invoice'
          )
    """, {
        "supplier": supplier,
        "company": company
    }, as_dict=True)
    return result[0].total_unsettled or 0


@frappe.whitelist()
def resend_approver_request(docname, method):
    frappe.only_for(["System Manager", "Adhoc Payment Requester", "Purchase Manager", "Purchase User"])
    doc = frappe.get_doc("Supplier Payment Request", docname)
    assign_and_notify_next_preq_authority(doc, method)