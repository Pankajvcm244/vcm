#bench --site pankaj.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.PE_n_JV_gaps.export_payment_journal_discrepancies_to_excel

import frappe
import pandas as pd
import os

def export_payment_journal_discrepancies_to_excel():
    rows = []

    # Step 1: Find Payment Entries linked to Journal Entries
    journal_links = frappe.db.sql("""
        SELECT 
            jea.reference_name AS payment_entry,
            je.name AS journal_entry,
            jea.account,
            jea.debit,
            jea.credit,
            je.company AS je_company,
            jea.cost_center,
            jea.budget_head
        FROM `tabJournal Entry` je
        JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
        WHERE jea.reference_type = 'Payment Entry'
        AND je.docstatus = 1
    """, as_dict=True)

    # Step 2: Process and compare with Payment Entry
    for link in journal_links:
        try:
            pe = frappe.get_doc("Payment Entry", link.payment_entry)

            pe_deduction = pe.deductions[0] if pe.deductions else None

            discrepancy = {
                "Payment Entry": pe.name,
                "Journal Entry": link.journal_entry,
                "Company (PE)": pe.company,
                "Company (JE)": link.je_company,
                "Party (PE)": pe.party,
                "Account (PE Paid From)": pe.paid_from,
                "Account (PE Paid To)": pe.paid_to,
                "Account (JE)": link.account,
                "PE Amount": pe.paid_amount,
                "JE Debit": link.debit,
                "JE Credit": link.credit,
                "Cost Center (PE)": pe_deduction.cost_center if pe_deduction else "",
                "Cost Center (JE)": link.cost_center,
                "Budget Head (PE)": pe_deduction.budget_head if pe_deduction else "",
                "Budget Head (JE)": link.budget_head,
                "Location (PE)": getattr(pe, "location", ""),
                "Location (JE)": getattr(frappe.get_doc("Journal Entry", link.journal_entry), "location", "")
            }

            # Check for differences
            if any([
                discrepancy["Company (PE)"] != discrepancy["Company (JE)"],
                discrepancy["Account (PE Paid To)"] != link.account and discrepancy["Account (PE Paid From)"] != link.account,
                abs(discrepancy["PE Amount"] - (link.debit or 0) - (link.credit or 0)) > 0.01,
                discrepancy["Cost Center (PE)"] != discrepancy["Cost Center (JE)"],
                discrepancy["Budget Head (PE)"] != discrepancy["Budget Head (JE)"],
                discrepancy["Location (PE)"] != discrepancy["Location (JE)"],
            ]):
                rows.append(discrepancy)

        except Exception:
            frappe.log_error(frappe.get_traceback(), "Payment-Journal Discrepancy Error")

    if not rows:
        print("✅ No discrepancies found.")
        return

    # Step 3: Export to Excel
    df = pd.DataFrame(rows)
    export_path = os.path.join(frappe.utils.get_site_path(), "private", "files", "payment_journal_discrepancies.xlsx")
    df.to_excel(export_path, index=False)

    print(f"✅ Discrepancy report exported to: {export_path}")
