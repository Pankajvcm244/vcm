from __future__ import unicode_literals
from frappe import _

def get_data():
    return {
        'fieldname': 'vcm_item_creation_request',  
        'transactions': [
            {
                'label': _('Item Code'),
                'items': ['Item']
            }
        ]
    }




