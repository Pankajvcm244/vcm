import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def get_system_fields():
    custom_fields = {
        "Item": [
            dict(
                fieldname="vcm_item_creation_request",
                label="VCM Item Creation Request",
                fieldtype="Link",
                options="VCM Item Creation Request",
                insert_after="item_name",
            )
        ]
    }
    return custom_fields

def create_system_fields():
    custom_fields = get_system_fields()
    create_custom_fields(custom_fields, update=True)