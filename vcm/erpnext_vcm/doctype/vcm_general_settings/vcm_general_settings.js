// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM General Settings", {
    refresh: function(frm) {
            frm.add_custom_button('Run MR Reorder', function() {
                frappe.call({
                    method: 'vcm.erpnext_vcm.utilities.custom_reorder.reorder_item',  // Update path to match your custom app and function
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint(__('MR Reorder complete'));
                        }
                    }
                });
            });
    },
});
