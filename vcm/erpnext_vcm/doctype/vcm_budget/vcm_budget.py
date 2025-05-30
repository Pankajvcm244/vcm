# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe.utils import getdate
import pandas as pd
import os
from frappe.utils.file_manager import get_file
import logging
logging.basicConfig(level=logging.DEBUG)

class VCMBudget(Document):

    def autoname(self):
        if self.cost_center and self.company and self.fiscal_year:
            company_name = frappe.get_doc("Company", self.company)
            company_abbr = company_name.abbr
            self.name = f"{company_abbr}-{self.fiscal_year}-{self.location}-{self.cost_center}"

    def on_update(self):
            # Skip addiition or deletion validation for new documents
            # Fetch existing document from the database before modifications
            old_doc = frappe.get_doc("VCM Budget", self.name)

            # Extract budget item names before and after modification
            old_budget_items = {item.name for item in old_doc.get("budget_items") or []}
            new_budget_items = {item.name for item in self.get("budget_items") or []}

            # Identify deleted items (if present in old but not in new)
            deleted_items = old_budget_items - new_budget_items

            # Check if document is submitted and if any row is deleted
            if self.docstatus == 1 and deleted_items:
                frappe.throw("You cannot delete Budget Items after submission, but you can add new ones.")

    def validate(self):
        #logging.debug(f"in budget validate-1   ")
        # Check if budget already exists for new entry
        if self.is_new():
            #logging.debug(f"in budget validate-ID {self.name} , {self.total_amount}  ")
            if self.total_amount == 0:
                # This is new Budget creation as after this Origional amount will be non-zero              
                budget_exists = frappe.db.exists("VCM Budget", {
                    "company": self.company, 
                    "location": self.location,
                    "fiscal_year": self.fiscal_year,
                    "cost_center": self.cost_center
                    })
                if budget_exists:
                    frappe.throw(f"Budget exists for {self.company}-{self.fiscal_year}-{self.location}-{self.cost_center}")               
        is_group = frappe.get_value("Cost Center", self.cost_center, "is_group")
        if is_group:
                frappe.throw(f"Cost Center {self.cost_center} is a folder. Please select a child Cost Center.")
        
        # we will check Budget Head in Child table row below        
        budget_heads = set()
        for row in self.budget_items:
            # Check for duplicate budget heads
            if row.budget_head in budget_heads:
                frappe.throw(f"Duplicate Budget Head: {row.budget_head}. Each Budget Head must be unique.")
            is_head_group = frappe.get_value("Budget Head", row.budget_head, "is_group")
            if is_head_group:
                frappe.throw(f"Budget Head '{row.budget_head}' is a folder. Please select a child Budget Head.")
            budget_heads.add(row.budget_head)           

@frappe.whitelist()
def get_budget_items(company, fiscal_year, location, cost_center): 
    #logging.debug(f"in get_budget_items-1   {company}, {fiscal_year}, {cost_center} ")    
    # Fetch VCM Budget document name for a given company, location, fiscal year, and cost center where Docstatus = 1
    budget_name = frappe.db.get_value(
        "VCM Budget", 
        {"company": company, "location": location, "fiscal_year": fiscal_year, "cost_center": cost_center, "docstatus": 1},
        "name")
    budget_doc = frappe.get_doc("VCM Budget", budget_name)    
    if not budget_doc:
        return []  # Return an empty list if no budget found

    # Fetch all budget items for the given company and fiscal year
    budget_items = frappe.db.sql("""
        SELECT bci.budget_head, bci.original_amount, bci.amended_till_now, bci.paid_payment_entry, bci.unpaid_purchase_invoice, bci.unpaid_purchase_order, bci.additional_je,  bci.current_budget, bci.used_budget, bci.balance_budget
        FROM `tabVCM Budget` b
        JOIN `tabVCM Budget Child Table` bci ON b.name = bci.parent
        WHERE b.company = %s AND b.location = %s AND b.fiscal_year = %s AND b.cost_center = %s AND b.docstatus = 1
        """, (company, location, fiscal_year, cost_center), as_dict=True)
    #logging.debug(f"in get_budget_items-2   {budget_items}  ")
    return budget_items


@frappe.whitelist()
def get_vcm_budget_head(cost_center, location, company):
    today = getdate(nowdate())
    fiscal_year = frappe.db.get_value("Fiscal Year", {
        "year_start_date": ["<=", today],
        "year_end_date": [">=", today],
    }, "name")

    #logging.debug(f"in get_vcm_budget_head-0   {cost_center}, {location}, {company}, {fiscal_year}")
    budget_name = frappe.db.get_value(
			"VCM Budget", 
			{"company": company, "location": location, "fiscal_year": fiscal_year, "cost_center": cost_center, "docstatus": 1},
			"name")    
    #logging.debug(f"in get_vcm_budget_head-1   {budget_name} ,{cost_center}, {location}, {company}, {fiscal_year}")
    # Fetch the Budget document only if it's in Submit state and not Cancelled
    budget_doc = frappe.get_doc("VCM Budget", budget_name)    
    if not budget_doc:
        return {"vcm_budget": None, "budget_heads": []}
    #logging.debug(f"in get_vcm_budget_head-2   {budget_doc} ")
    # Create a dictionary for quick lookup of budget heads
    budget_items_map = {item.budget_head: item for item in budget_doc.get("budget_items") or []}
    #logging.debug(f"in get_vcm_budget_head-3   {budget_items_map.keys()} ") 
    return {"vcm_budget": budget_name, "budget_heads": budget_items_map.keys()}

@frappe.whitelist()
def is_pool_budget_head(budget_head_name):
    """  Returns:  bool: True if 'Pool Budget Head' is checked (1), False otherwise.
    """
    if not budget_head_name:
        return False
    if not frappe.db.exists("Budget Head", budget_head_name):
        return False
    budget_head = frappe.get_doc("Budget Head", budget_head_name)
    return budget_head.pool_budget_head == 1


@frappe.whitelist()
def excel_to_child_table(file_url, docname):
    # Allowed users
    allowed_users = ['Administrator','pankaj.sharma@vcm.org.in', 'prashant.yadav@vcm.org.in', 'sund@vcm.org.in', 'gaurav.vyas@vcm.org.in', ]; 
    if frappe.session.user not in allowed_users:
        frappe.throw("You are not authorized to upload Excel files.")

   # Get the file document using the file_url
    try:
        file_doc = frappe.get_doc("File", {"file_url": file_url})
    except frappe.DoesNotExistError:
        frappe.throw(f"File not found in the system: {file_url}")

    # Get the file content directly from the file document
    file_content = file_doc.get_content()

    # Use pandas to read the Excel file content directly from the binary data
    try:
        # pd.read_excel can read from binary data using a BytesIO buffer
        from io import BytesIO
        df = pd.read_excel(BytesIO(file_content))
    except Exception as e:
        frappe.throw(f"Failed to read Excel file: {e}")

    # Verify if the required columns exist in the DataFrame
    required_columns = ['BUDGET HEAD', 'TOTAL']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        frappe.throw(f"Missing required columns in the Excel file: {', '.join(missing_columns)}")
    
    # Load the parent document
    doc = frappe.get_doc('VCM Budget', docname)
    # Clear existing child rows if needed
    doc.set('budget_items', [])

    # Iterate and append rows
    for _, row in df.iterrows():
        doc.append('budget_items', {
            'budget_head': row.get('BUDGET HEAD'),
            'original_amount': row.get('TOTAL'),
            'proposed_by': frappe.session.user 
        })

    doc.save()
    frappe.db.commit()
