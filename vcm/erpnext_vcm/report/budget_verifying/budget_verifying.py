import frappe
import logging
logging.basicConfig(level=logging.DEBUG)

def execute(filters=None):
    if not filters:
        filters = {}
    
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    document_type = filters.get("document_type", "Purchase Invoice")

    columns = [
        {"label": "ID", "fieldname": "name", "fieldtype": "Link", "options": document_type, "width": 150},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": "Budget Applicable", "fieldname": "vcm_budget_applicable", "fieldtype": "Link", "options": "Cost Center", "width": 100},
        {"label": "Location", "fieldname": "location", "fieldtype": "Data", "width": 75},
        {"label": "Budget Head", "fieldname": "budget_head", "fieldtype": "Data", "width": 150},
         {"label": "Fiscal Year", "fieldname": "fiscal_year", "fieldtype": "Data", "width": 150},

    ]
    if document_type == "Purchase Invoice":
        columns.append({"label": "Has PO", "fieldname": "has_po", "fieldtype": "Data", "width": 100})
        columns.append({"label": "PO Number", "fieldname": "po_number", "fieldtype": "Data", "width": 150})    
    elif document_type == "Payment Entry":
        columns.append({"label": "Has Reference", "fieldname": "has_reference", "fieldtype": "Data", "width": 100})
        columns.append({"label": "Linked References", "fieldname": "linked_references", "fieldtype": "Data", "width": 200})
    elif document_type == "Journal Entry":
        columns.append({"label": "Root Type", "fieldname": "root_type", "fieldtype": "Data", "width": 100})
        columns.append({"label": "Root Type", "fieldname": "entry_type", "fieldtype": "Data", "width": 100}) 
        columns.append({"label": "JV A/C", "fieldname": "jv_account", "fieldtype": "Data", "width": 100})     
    columns.append({"label": "Transaction Date", "fieldname": "date", "fieldtype": "Date", "width": 120} )
    columns.append({"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150})
    columns.append({"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 150})
    columns.append({"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100})

    return columns

def get_data(filters):
    document_type = filters.get("document_type", "Purchase Invoice")
    selected_table = f"tab{document_type}"
    alias = "doc"

    supplier_field = {
        "Purchase Invoice": "supplier",
        "Purchase Order": "supplier",
        "Payment Entry": "party",
        "Journal Entry": "party"  # comes from child table in JE
    }.get(document_type, "supplier")

    date_field = {
        "Purchase Invoice": "posting_date",
        "Purchase Order": "transaction_date",
        "Payment Entry": "posting_date",
        "Journal Entry": "posting_date"
    }.get(document_type, "posting_date")

    amount_field = {
        "Purchase Invoice": "grand_total",
        "Purchase Order": "grand_total",
        "Payment Entry": "paid_amount",
        "Journal Entry": "total_debit"
    }.get(document_type, "grand_total")

    # Determine whether fields are from child or parent table
    use_child_fields = document_type == "Journal Entry"

    # Begin condition building
    conditions = [f"{alias}.docstatus = 1"]

    # Adjust filters based on doctype structure
    if use_child_fields:
        child_alias = "jea"
        # if filters.get("supplier"):
        #     conditions.append(f"{child_alias}.party = %(supplier)s")
        if filters.get("cost_center"):
            conditions.append(f"{child_alias}.cost_center = %(cost_center)s")
        if filters.get("location"):
            conditions.append(f"{child_alias}.location = %(location)s")
        if filters.get("budget_head"):
            conditions.append(f"{child_alias}.budget_head = %(budget_head)s")
        if filters.get("company"):
            conditions.append(f"{alias}.company = %(company)s")        
        if filters.get("from_date") and filters.get("to_date"):
            conditions.append(f"{alias}.{date_field} BETWEEN %(from_date)s AND %(to_date)s")
        conditions.append("acc.root_type = 'Expense'")
    else:
        if filters.get("supplier"):
            conditions.append(f"{alias}.{supplier_field} = %(supplier)s")
        if filters.get("cost_center"):
            conditions.append(f"{alias}.cost_center = %(cost_center)s")
        if filters.get("location"):
            conditions.append(f"{alias}.location = %(location)s")
        if filters.get("budget_head"):
            conditions.append(f"{alias}.budget_head = %(budget_head)s")
        if filters.get("company"):
            conditions.append(f"{alias}.company = %(company)s")
        if filters.get("from_date") and filters.get("to_date"):
            conditions.append(f"{alias}.{date_field} BETWEEN %(from_date)s AND %(to_date)s")

    condition_string = " AND ".join(conditions)

    # Check if the "status" field exists
    has_status = any(f.fieldname == "status" for f in frappe.get_meta(document_type).fields)

    # Handle each doctype specifically
    if document_type == "Purchase Invoice":
        query = f"""
            SELECT
                {alias}.name,
                {alias}.{supplier_field} AS supplier,
                {alias}.{date_field} AS date,
                {alias}.{amount_field} AS total_amount,
                {alias}.status,
                {alias}.cost_center,
                {alias}.location,
                {alias}.company,
                {alias}.budget_head,
                {alias}.fiscal_year,
                cc.custom_vcm_budget_applicable AS vcm_budget_applicable,
                CASE
                    WHEN pii.purchase_order IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END AS has_po,
                GROUP_CONCAT(DISTINCT pii.purchase_order SEPARATOR ', ') AS po_number
            FROM `{selected_table}` {alias}
            LEFT JOIN `tabPurchase Invoice Item` pii ON pii.parent = {alias}.name
            LEFT JOIN `tabCost Center` cc ON cc.name = {alias}.cost_center
            WHERE {condition_string}
            GROUP BY {alias}.name
        """

    elif document_type == "Journal Entry":
        query = f"""
                SELECT
                    {alias}.name,
                    jea.party AS supplier, 
                    {alias}.{date_field} AS date,                   
                    SUM(CASE 
                        WHEN jea.debit > 0 THEN jea.debit
                        WHEN jea.credit > 0 THEN -jea.credit
                        ELSE 0
                    END) AS total_amount,
                    CASE 
                        WHEN SUM(jea.debit) > SUM(jea.credit) THEN 'Debit'
                        WHEN SUM(jea.credit) > SUM(jea.debit) THEN 'Credit'
                        ELSE 'Neutral'
                    END AS entry_type, 
                    jea.account AS jv_account,
                    jea.cost_center,
                    cc.custom_vcm_budget_applicable AS vcm_budget_applicable,
                    jea.location,
                    jea.fiscal_year,
                    {alias}.company,
                    jea.budget_head,           
                    acc.root_type AS root_type
                FROM `tabJournal Entry` {alias}
                LEFT JOIN `tabJournal Entry Account` jea ON jea.parent = {alias}.name
                LEFT JOIN `tabAccount` acc ON acc.name = jea.account
                LEFT JOIN `tabCost Center` cc ON cc.name = jea.cost_center
                WHERE {condition_string}
                GROUP BY 
                    {alias}.name,
                    jea.party,
                    jea.account,
                    jea.cost_center,
                    cc.custom_vcm_budget_applicable,
                    jea.location,
                    jea.fiscal_year,
                    {alias}.company,
                    jea.budget_head,
                    acc.root_type,
                    {alias}.{date_field}                
                """
    elif document_type == "Payment Entry":
        query = f"""
            SELECT
                {alias}.name,
                {alias}.{supplier_field} AS supplier,
                {alias}.{date_field} AS date,
                {alias}.{amount_field} AS total_amount,
                {alias}.cost_center,
                cc.custom_vcm_budget_applicable AS vcm_budget_applicable,
                {alias}.location,
                {alias}.company,
                {alias}.budget_head,
                {alias}.fiscal_year,
                CASE
                    WHEN COUNT(DISTINCT per.reference_name) > 0 THEN 'Yes'
                    ELSE 'No'
                END AS has_reference,
                GROUP_CONCAT(DISTINCT per.reference_name SEPARATOR ', ') AS linked_references
            FROM `tabPayment Entry` {alias}
            LEFT JOIN `tabPayment Entry Reference` per ON per.parent = {alias}.name
            LEFT JOIN `tabCost Center` cc ON cc.name = {alias}.cost_center
            WHERE {condition_string}
            GROUP BY {alias}.name
        """
    else:
        # Generic handler for Purchase Order and Payment Entry
        select_fields = f"""
            {alias}.name,
            {alias}.{supplier_field} AS supplier,
            {alias}.{date_field} AS date,
            {alias}.{amount_field} AS total_amount,
        """

        if has_status:
            select_fields += f"{alias}.status,"

        select_fields += f"""
            {alias}.cost_center,
            cc.custom_vcm_budget_applicable AS vcm_budget_applicable,
            {alias}.location,
            {alias}.company,
            {alias}.budget_head,
            {alias}.fiscal_year            
        """

        query = f"""
            SELECT
                {select_fields}
            FROM `{selected_table}` {alias}            
            LEFT JOIN `tabCost Center` cc ON cc.name = {alias}.cost_center
            WHERE {condition_string}
        """

    return frappe.db.sql(query, filters, as_dict=True)