// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM Stock Audit Merge", {
    refresh: function(frm) {
        frm.add_custom_button("Merge Audits", function() {
            frappe.call({
                method: "vcm.erpnext_vcm.doctype.vcm_stock_audit_merge.vcm_stock_audit_merge.merge_audits",
                args: {
                    docname: frm.doc.name
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.msgprint("✅ Audits merged successfully.");
                        frm.reload_doc();
                    }
                }
            });
        });
        frm.add_custom_button("Export as Excel", function () {
            frappe.call({
                method: "vcm.erpnext_vcm.doctype.vcm_stock_audit_merge.vcm_stock_audit_merge.export_merged_report",
                args: {
                    docname: frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        window.open(r.message);
                    }
                }
            });
        });
    }
});

