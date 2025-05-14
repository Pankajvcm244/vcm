// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt


frappe.ui.form.on("Supplier Payment Request", {
    refresh(frm) {
        //if (frm.doc.docstatus === 1 && !frm.doc.payment_entry && frm.doc.purchase_order) {
            frm.add_custom_button("Create PO Payment Entry", function () {
                frappe.call({
                    method: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.create_payment_entry_from_request",
                    args: {
                        docname: frm.doc.name
                    },
                    callback(r) {
                        if (r.message) {
                            frappe.msgprint(`Payment Entry <b>${r.message}</b> created.`);
                            frappe.set_route("Form", "Payment Entry", r.message);
                        }
                    }
                });
            });
            frm.add_custom_button("Create PI Payment Entry", () => {
                frappe.call({
                    method: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.create_payment_entry_for_selected_invoices",
                    args: { docname: frm.doc.name },
                    callback(r) {
                        if (r.message) {
                            frappe.msgprint(`Payment Entry <a href="/app/payment-entry/${r.message}" target="_blank">${r.message}</a> created`);
                        }
                    }
                });
            });
        //}
    },

    onload: function(frm) {
        if (frm.doc.supplier) {
            frm.trigger("supplier");
        }
        if (frm.doc.supplier) {
            frm.trigger("request_type");
        }
        
    },
    supplier: function(frm) {
        const rt = frm.doc.request_type;
        if (rt === "Advance Payments (against PO)") {
            frm.clear_table("pending_invoice_detail");
            frm.refresh_fields("pending_invoice_detail"); 
            frm.set_query("purchase_order", function() {
                return {
                    filters: {
                        supplier: frm.doc.supplier,
                        company: frm.doc.company,
                        status: ["not in", ["Closed", "Completed"]],
                        docstatus: 1
                    }
                };
            });
            //} 
        }
        if (rt === "Credit Payments (against Invoice)") { 
            frm.clear_table("po_payment_details");
            frm.refresh_fields("po_payment_details");           
            // Get PI entries for supplier
            frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Purchase Invoice",
                fields: ["name", "posting_date", "due_date", "grand_total", "outstanding_amount"],
                filters: {
                    supplier: frm.doc.supplier,
                    docstatus: 1,
                    company: frm.doc.company,
                    outstanding_amount: [">", 0]
                },
                limit_page_length: 100
            },
            callback: function (r) {
                if (r.message) {
                    frm.clear_table("pending_invoice_detail");
                    r.message.forEach(row => {
                        const child = frm.add_child("pending_invoice_detail", {
                            invoice: row.name,
                            posting_date: row.posting_date,
                            due_date: row.due_date,
                            grand_total: row.grand_total,
                            outstanding_amount: row.outstanding_amount
                        });
                    });
                    frm.refresh_field("pending_invoice_detail");
                }
            }
            });
            //PI entries for supplier
        }
    },
    request_type: function(frm) {
        const rt = frm.doc.request_type;
        // Handle Purchase Order visibility and requirement
        if (rt === "Advance Payments (against PO)") {
            frm.set_df_property("purchase_order", "hidden", false);
            frm.set_df_property("purchase_order", "reqd", true);
        } else {
            frm.set_df_property("purchase_order", "hidden", true);
            frm.set_df_property("purchase_order", "reqd", false);
            frm.set_value("purchase_order", null);
        }        
    },
    purchase_order: function(frm) {
        if (!frm.doc.purchase_order) {
            frm.set_value("po_amount", null);
            frm.set_value("advance__paid", null);
            frm.set_value("remaining_advance", null);
            frm.clear_table("po_payment_details");
            frm.refresh_field("po_payment_details");
            return;
        }
        // Get PO info
        frappe.db.get_value("Purchase Order", frm.doc.purchase_order, ["grand_total", "advance_paid", "custom_advance_amount"])
            .then(r => {
                if (r && r.message) {
                    const grand_total = r.message.grand_total || 0;
                    const advance_paid = r.message.advance_paid || 0;
                    const advance_requested_in_po = r.message.custom_advance_amount || 0;
                    const remaining = advance_requested_in_po - advance_paid;

                    frm.set_value("po_amount", grand_total);
                    frm.set_value("advance__paid", advance_paid);
                    frm.set_value("advance_requested_in_po", advance_requested_in_po);
                    frm.set_value("remaining_advance", remaining);
                }
            });

         // 2. Fetch Payment Entries from backend
        frappe.call({
            method: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.get_payment_entries_for_po",
            args: {
                purchase_order: frm.doc.purchase_order
            },
            callback: function(r) {
                const entries = r.message || [];
                let total = 0;

                frm.clear_table("po_payment_details");

                entries.forEach(pe => {
                    const row = frm.add_child("po_payment_details");
                    row.payment_entry = pe.name;
                    row.payment_date = pe.posting_date;
                    row.paid_amount = pe.paid_amount;
                    total += pe.paid_amount;
                });                
                frm.refresh_fields();
            }
        });
    }
    
    
        
});