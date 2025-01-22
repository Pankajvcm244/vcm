import frappe,requests,json

import logging
logging.basicConfig(level=logging.DEBUG)

@frappe.whitelist()
def filter_sellable_items(items,price_list,company):
        #logging.debug(f"in Filter sellable items .")
        #logging.debug(f"in Filter sellable items . {price_list}. {company}") 
        try:
            items = json.loads(items)
        except json.JSONDecodeError:
            frappe.throw(_("Invalid items parameter format. Please provide a valid JSON array."))
        
        # Ensure items is a list
        if not isinstance(items, list):
            frappe.throw(_("Items must be a list."))
        
        #logging.debug(f"in Filter sellable items1 {items}") 
        
        # Convert the list to a SQL-safe string
        items_tuple = tuple(items)
        #logging.debug(f"in Filter sellable items3 {items_tuple}")

        # Prepare the query
        query = """
            SELECT
                item.`item_code` AS code,
                item.`item_name` AS name,
                IF(STRCMP(item_template.name, "") = 1,
                    ROUND(item_price.`price_list_rate` + (item_price.`price_list_rate` * item_template.cumulative_tax / 100), 0),
                    ROUND(item_price.`price_list_rate`, 0)
                ) AS rate
            FROM
                `tabItem` item
            LEFT JOIN `tabItem Price` item_price
                ON item_price.item_code = item.item_code
            LEFT JOIN `tabItem Tax` tax
                ON tax.parent = item.name
            LEFT JOIN `tabItem Tax Template` item_template
                ON tax.item_tax_template = item_template.name
            WHERE item.has_variants = 0
                AND item.name IN %(items)s
                AND item_price.price_list = %(price_list)s
                AND (item_template.name IS NULL OR item_template.company = %(company)s)
            GROUP BY item.name
            """

        # Execute the query
        data = frappe.db.sql(query, {
            'items': items_tuple,
            'price_list': price_list,
            'company': company
        }, as_dict=True)
        #logging.debug(f"in Filter sellable items6 {data}")
        return data
