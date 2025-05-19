#bench --site erp.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.PE_n_JV_gaps.export_pe_je_discrepancies

import frappe
import pandas as pd
import os

import frappe
import pandas as pd
import os
from datetime import datetime, timedelta

def find_matching_journal_entry(pe):
    """
    Try to find a Journal Entry matching the Payment Entry based on party, amount, and date.
    """
    return frappe.db.sql("""
        SELECT
            je.name, je.posting_date, je.company, jea.account,
            jea.debit, jea.credit, jea.cost_center, jea.budget_head, jea.location
        FROM `tabJournal Entry` je
        JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
        WHERE
            je.docstatus = 1
            AND je.posting_date BETWEEN DATE_SUB(%s, INTERVAL 5 DAY) AND DATE_ADD(%s, INTERVAL 5 DAY)
            AND jea.party = %s
            AND ABS(jea.debit - %s) < 0.01 OR ABS(jea.credit - %s) < 0.01
        LIMIT 1
    """, (pe.posting_date, pe.posting_date, pe.party, pe.paid_amount, pe.paid_amount), as_dict=True)

def export_pe_je_discrepancies():
    rows = []
    payment_entries = frappe.get_all("Payment Entry", filters={"docstatus": 1}, fields=["name", "posting_date", "party", "paid_amount", "paid_from", "paid_to", "company"])

    for pe_data in payment_entries:
        pe = frappe.get_doc("Payment Entry", pe_data.name)
        je_matches = find_matching_journal_entry(pe)

        if not je_matches:
            continue  # No match found

        je = je_matches[0]

        pe_deduction = pe.deductions[0] if pe.deductions else {}

        discrepancy = {
            "Payment Entry": pe.name,
            "Journal Entry": je.name,
            "Company (PE)": pe.company,
            "Company (JE)": je.company,
            "Party": pe.party,
            "Account (PE Paid From)": pe.paid_from,
            "Account (PE Paid To)": pe.paid_to,
            "JE Account": je.account,
            "PE Amount": pe.paid_amount,
            "JE Amount": je.debit or je.credit,
            "Cost Center (PE)": pe.get("cost_center", ""),
            "Cost Center (JE)": je.cost_center,
            "Budget Head (PE)": pe.get("budget_head", ""),
            "Budget Head (JE)": je.budget_head,
            "Location (PE)": pe.get("location", ""),
            "Location (JE)": je.location,
        }

        # Check for differences
        if any([
            discrepancy["Company (PE)"] != discrepancy["Company (JE)"],
            discrepancy["JE Account"] not in [discrepancy["Account (PE Paid From)"], discrepancy["Account (PE Paid To)"]],
            abs(discrepancy["PE Amount"] - discrepancy["JE Amount"]) > 0.01,
            discrepancy["Cost Center (PE)"] != discrepancy["Cost Center (JE)"],
            discrepancy["Budget Head (PE)"] != discrepancy["Budget Head (JE)"],
            discrepancy["Location (PE)"] != discrepancy["Location (JE)"],
        ]):
            rows.append(discrepancy)

    if not rows:
        print("✅ No discrepancies found.")
        return

    df = pd.DataFrame(rows)
    export_path = os.path.join(frappe.utils.get_site_path(), "private", "files", "pe_je_discrepancies.xlsx")
    df.to_excel(export_path, index=False)
    print(f"✅ Exported to {export_path}")
