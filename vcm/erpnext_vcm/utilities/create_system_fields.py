import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
import logging
logging.basicConfig(level=logging.DEBUG)

def get_system_fields():
    custom_fields = {

        #  "Stock Entry": [
        #     dict(
        #         fieldname="vcm_remarks",
        #         label="VCM Remarks",
        #         fieldtype="Data",
        #         insert_after="material_recipient",
        #     )
        # ]
        # "Stock Entry": [
        #     dict(
        #         fieldname="material_recipient",
        #         label="Material Recipient",
        #         fieldtype="Link",
        #         options="User",
        #         insert_after="stock_entry_type",
        #     )
        # ]
        # "Item": [
        #     dict(
        #         fieldname="vcm_item_creation_request",
        #         label="VCM Item Creation Request",
        #         fieldtype="Link",
        #         options="VCM Item Creation Request",
        #         insert_after="item_name",
        #     )
        # ]
    }
    return custom_fields
#bench --site erp.vcmerp.in execute vcm.erpnext_vcm.utilities.create_system_fields.create_system_fields
def create_system_fields():
    custom_fields = get_system_fields()
    #logging.debug(f"in create_system_fields {custom_fields}")
    create_custom_fields(custom_fields, update=True)