# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.data import flt
from frappe.utils import today

import logging
logging.basicConfig(level=logging.DEBUG)

def execute(filters=None):
    if not filters:
        filters = {}
    company_filter = filters.get("company") if filters else None
    columns = [
        {"label": "Bank Account", "fieldname": "bank_account", "fieldtype": "Link", "options": "Account", "width": 150},
        {"label": "Account Name", "fieldname": "account_name", "fieldtype": "Data", "width": 150},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": "Bank Balance(GL)", "fieldname": "balance_as_per_system", "fieldtype": "Currency", "width": 150},
        #{"label": "Reco Pend Debit", "fieldname": "total_debit", "fieldtype": "Currency", "width": 150},
        # {"label": "Reco Pend Credit", "fieldname": "total_credit", "fieldtype": "Currency", "width": 150},
        {"label": "Unalloc Debit", "fieldname": "vcm_tx_debit", "fieldtype": "Currency", "width": 150},
        {"label": "Unalloc Credit", "fieldname": "vcm_tx_credit", "fieldtype": "Currency", "width": 150},
        {"label": "Final Balance", "fieldname": "bank_balance", "fieldtype": "Currency", "width": 150},
    ]
    bank_account_filters = {"account_type": "Bank", "is_group": 0}
    if company_filter:
        bank_account_filters["company"] = company_filter

    data = []
	
    bank_accounts = frappe.db.get_all('Account', filters={"account_type": "Bank", "is_group": 0}, fields=["name", "account_name", "company", "account_currency"])

    for bank in bank_accounts:
        # Get GL balance (debit - credit)
        balance_as_per_system = frappe.db.sql("""
            SELECT SUM(debit) - SUM(credit)
            FROM `tabGL Entry`
            WHERE account = %s AND company = %s AND posting_date <= %s AND docstatus = 1
        """, (bank.name, bank.company, today()))[0][0] or 0.0

        # Get unallocated amount (bank transactions not linked yet)
        tx_debit, tx_credit = vcm_get_amounts_from_bank_transactions(bank.name, bank.company)
        #logging.debug(f"Unallocated 2 : Debit={tx_debit}, Credit={tx_credit}")

        # filters = {"account": bank.name, "report_date": today(), "company": bank.company}
        # reco_entries = get_entries(filters)
        # total_debit, total_credit = 0, 0
        # for d in reco_entries:
        #     total_debit += flt(d.debit)
        #     total_credit += flt(d.credit)

        # Get amounts not reflected in system
        # amounts_not_reflected_in_system = get_amounts_not_reflected_in_system(
        #     bank.name, bank.company, filters
        # )
        bank_balance = (
            balance_as_per_system
            #  - flt(total_debit)
            #  + flt(total_credit)
            #+ amounts_not_reflected_in_system
            + flt(tx_debit)
            - flt(tx_credit)
        )
        data.append({
            "bank_account": bank.name,
            "account_name": bank.account_name,
            "company": bank.company,
            "currency": bank.account_currency,
            "balance_as_per_system": balance_as_per_system,
            "vcm_tx_debit": flt(tx_debit),
            "vcm_tx_credit": flt(tx_credit),
            # "total_debit": flt(total_debit),
            # "total_credit": flt(total_credit),
            "bank_balance": bank_balance, 
        })
        

    return columns, data

def vcm_get_amounts_from_bank_transactions(bank_name, company_name):
    #logging.debug(f"in vcm_get_amounts_ {bank_name} {company_name}")
    # Get unallocated amounts from bank transactions
    # This is the sum of unallocated amounts for both debit and credit transactions   
    bank_account = frappe.get_value(
        "Bank Account", {"account": bank_name}, "name"
    ) 
    s = frappe.db.sql(
        """
                SELECT 
                    SUM(IF(deposit > 0, unallocated_amount, 0)) AS debit,
                    SUM(IF(withdrawal > 0, unallocated_amount, 0)) AS credit
                FROM `tabBank Transaction`
                WHERE  
                    status = 'Unreconciled' 
                    AND docstatus = 1 
                    AND bank_account=%s 
                    AND company=%s
                    AND `date` <= %s
                """ , (bank_account, company_name, today()))    
    if s and s[0]:        
        debit = flt(s[0][0] or 0.0)
        credit = flt(s[0][1] or 0.0)
        #logging.debug(f"Unallocated 1: Debit={debit}, Credit={credit}")
        return debit, credit
    else:
        #logging.debug(f"in S2 {s} ")
        return [0, 0]