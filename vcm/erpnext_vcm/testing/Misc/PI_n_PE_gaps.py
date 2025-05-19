
# bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.PI_n_PE_gaps.export_invoice_payment_discrepancies_to_excel

import frappe
import pandas as pd
import os

def export_invoice_payment_discrepancies_to_excel():
    rows = []

    # Fetch all Payment Entry References linked to Purchase Invoices
    payment_refs = frappe.db.sql("""
        SELECT 
            per.parent AS payment_entry,
            per.reference_name AS purchase_invoice,
            per.allocated_amount,
            pe.paid_to,
            pe.paid_from,
            pe.party,
            pe.party_type,
            pe.company AS pe_company
        FROM
            `tabPayment Entry Reference` per
        JOIN
            `tabPayment Entry` pe ON pe.name = per.parent
        WHERE
            per.reference_doctype = 'Purchase Invoice'
            AND pe.docstatus = 1
    """, as_dict=True)

    for ref in payment_refs:
        try:
            pi = frappe.get_doc("Purchase Invoice", ref.purchase_invoice)
            pe = frappe.get_doc("Payment Entry", ref.payment_entry)

            pi_item = pi.items[0] if pi.items else None
            pe_deduction = pe.deductions[0] if pe.deductions else None

            discrepancy = {
                "Purchase Invoice": pi.name,
                "Payment Entry": pe.name,
                "Company (PI)": pi.company,
                "Company (PE)": ref.pe_company,
                "Supplier (PI)": pi.supplier,
                "Supplier (PE)": ref.party,
                "Bill No (PI)": pi.bill_no,
                "Paid To (PE)": ref.paid_to,
                "Credit To (PI)": pi.credit_to,
                "PI Amount": pi.grand_total,
                "PE Allocated": ref.allocated_amount,
                "Cost Center (PI)": pi.cost_center,
                "Cost Center (PE)": pe.get("cost_center", ""),
                "Location (PI)": pi.location,
                "Location (PE)": pe.get("location", ""),
                "Budget Head (PI)": pi.budget_head,
                "Budget Head (PE)": pe.get("budget_head", ""),
            }

            # Only include rows with mismatches
            if any([
                discrepancy["Company (PI)"] != discrepancy["Company (PE)"],
                discrepancy["Supplier (PI)"] != discrepancy["Supplier (PE)"],
                discrepancy["Paid To (PE)"] != discrepancy["Credit To (PI)"],
                abs(discrepancy["PI Amount"] - discrepancy["PE Allocated"]) > 0.01,
                discrepancy["Cost Center (PI)"] != discrepancy["Cost Center (PE)"],
                discrepancy["Location (PI)"] != discrepancy["Location (PE)"],
                discrepancy["Budget Head (PI)"] != discrepancy["Budget Head (PE)"],
            ]):
                rows.append(discrepancy)

        except Exception:
            frappe.log_error(frappe.get_traceback(), "Discrepancy Report Error")

    if not rows:
        print("✅ No discrepancies found.")
        return

    # Export to Excel
    df = pd.DataFrame(rows)
    export_path = os.path.join(frappe.utils.get_site_path(), "private", "files", "invoice_payment_discrepancies.xlsx")
    df.to_excel(export_path, index=False)

    print(f"✅ Discrepancy report exported to: {export_path}")



