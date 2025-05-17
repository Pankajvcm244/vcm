// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

// frappe.ui.form.on("VCM Warehouse ALM", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('VCM Warehouse ALM', {
    company: function(frm) {
        if (frm.doc.company) {
            frm.fields_dict.vcm_warehouse_alm_level.grid.get_field('target_warehouse').get_query = function(doc, cdt, cdn) {
                return {
                    filters: {
                        'company': frm.doc.company
                    }
                };
            };
        }
    }
});