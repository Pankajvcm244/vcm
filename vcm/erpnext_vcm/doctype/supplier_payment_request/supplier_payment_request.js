// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt
frappe.ui.form.on("Supplier Payment Request", {
    refresh(frm) {
        //if (frm.doc.docstatus === 1 && !frm.doc.payment_entry && frm.doc.purchase_order) {
            // frm.add_custom_button("Create PO Payment Entry", function () {
            //     frappe.call({
            //         method: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.create_payment_entry_from_request",
            //         args: {
            //             docname: frm.doc.name
            //         },
            //         callback(r) {
            //             if (r.message) {
            //                 frappe.msgprint(`Payment Entry <b>${r.message}</b> created.`);
            //                 frappe.set_route("Form", "Payment Entry", r.message);
            //             }
            //         }
            //     });
            // });
            // frm.add_custom_button("Create Adhoc Payment Entry", function () {
            //     frappe.call({
            //         method: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.create_payment_entry_from_adhoc_request",
            //         args: {
            //             docname: frm.doc.name
            //         },
            //         callback(r) {
            //             if (r.message) {
            //                 frappe.msgprint(`Payment Entry <b>${r.message}</b> created.`);
            //                 frappe.set_route("Form", "Payment Entry", r.message);
            //             }
            //         }
            //     });
            // });
            // frm.add_custom_button("Create PI Payment Entry", () => {
            //     frappe.call({
            //         method: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.create_payment_entry_for_selected_invoices",
            //         args: { docname: frm.doc.name },
            //         callback(r) {
            //             if (r.message) {
            //                 frappe.msgprint(`Payment Entry <a href="/app/payment-entry/${r.message}" target="_blank">${r.message}</a> created`);
            //             }
            //         }
            //     });
            // });
        //}
        // Always set department query based on selected company
        frm.set_query("department", function() {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
         
    },

    onload: function(frm) {
        if (frm.doc.request_type  === "Adhoc Payment" ) {
            frm.clear_table("pending_invoice_detail");
            frm.refresh_fields("pending_invoice_detail");
            frm.clear_table("po_payment_details");
            frm.refresh_fields("po_payment_details");
        }
        if (frm.doc.request_type  === "Advance Payments (against PO)" ) {
            frm.clear_table("pending_invoice_detail");
            frm.refresh_fields("pending_invoice_detail");
            frm.trigger("department");
        }
        if (frm.doc.request_type  === "Credit Payments (against Invoice)" ) {
            frm.clear_table("po_payment_details");
            frm.refresh_fields("po_payment_details");
        } 
    },
    department: function(frm) {
        const rt = frm.doc.request_type;
        // Handle Advance Payments (against PO)
        if (rt === "Advance Payments (against PO)") {
            frm.clear_table("pending_invoice_detail");
            frm.refresh_fields("pending_invoice_detail");
            frm.set_query("purchase_order", function() {
                return {
                    query: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.get_purchase_orders_without_invoice_or_payment",
                    filters: {
                        company: frm.doc.company,
                        department: frm.doc.department
                    }
                };
            });
        }
        // Handle Credit Payments (against Invoice)
        if (rt === "Credit Payments (against Invoice)") {
            frm.clear_table("po_payment_details");
            frm.refresh_fields("po_payment_details");
            // Step 1: Get Purchase Invoices for the selected department
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Purchase Invoice",
                    fields: [
                        "name", "posting_date", "supplier", "budget_head",
                        "custom_purchase_person", "fiscal_year", "location",
                        "cost_center", "due_date", "grand_total", "outstanding_amount"
                    ],
                    filters: {
                        department: frm.doc.department,
                        docstatus: 1,
                        company: frm.doc.company,
                        outstanding_amount: [">", 0]
                    },
                    limit_page_length: 100
                },
                callback: function(r) {
                    if (r.message && r.message.length) {
                        frm.clear_table("pending_invoice_detail");
                        r.message.forEach(row => {
                            // Add child row first with default unsettled_payments = 0
                            const child = frm.add_child("pending_invoice_detail", {
                                invoice: row.name,
                                posting_date: row.posting_date,
                                due_date: row.due_date,
                                grand_total: row.grand_total,
                                outstanding_amount: row.outstanding_amount,
                                purchase_person: row.custom_purchase_person,
                                fiscal_year: row.fiscal_year,
                                location: row.location,
                                cost_center: row.cost_center,
                                budget_head: row.budget_head,
                                supplier: row.supplier,
                                amount_to_be_paid: row.outstanding_amount,
                                unsettled_payments: 0
                            });

                            // Step 2: Fetch unlinked unallocated payment sum for this supplier
                            frappe.call({
                                method: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.get_unlinked_payment_sum",
                                args: {
                                    supplier: row.supplier,
                                    company: frm.doc.company
                                },
                                callback: function(res) {
                                    if (res.message !== null) {
                                        child.unsettled_payments = res.message;
                                        frm.refresh_field("pending_invoice_detail");
                                    }
                                }
                            });
                        });
                    }
                }
            });
        }
    },
    supplier: function(frm) {
        const rt = frm.doc.request_type;
        // Handle Advance Payments (against PO)
        if (rt === "Advance Payments (against PO)") {
            frm.clear_table("pending_invoice_detail");
            frm.refresh_fields("pending_invoice_detail");
            frm.set_query("purchase_order", function() {
                return {
                    query: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.get_purchase_orders_without_invoice_or_payment",
                    filters: {
                        company: frm.doc.company,
                        supplier: frm.doc.supplier,
                        department: frm.doc.department
                    }
                };
            });
        }

        // Handle Credit Payments (against Invoice)
        if (rt === "Credit Payments (against Invoice)") {
            frm.clear_table("po_payment_details");
            frm.refresh_fields("po_payment_details");

            // Step 1: Get Purchase Invoices for the selected department
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Purchase Invoice",
                    fields: [
                        "name", "posting_date", "supplier", "budget_head",
                        "custom_purchase_person", "fiscal_year", "location",
                        "cost_center", "due_date", "grand_total", "outstanding_amount"
                    ],
                    filters: {
                        department: frm.doc.department,
                        docstatus: 1,
                        company: frm.doc.company,
                        supplier: frm.doc.supplier,
                        outstanding_amount: [">", 0]
                    },
                    limit_page_length: 100
                },
                callback: function(r) {
                    if (r.message && r.message.length) {
                        frm.clear_table("pending_invoice_detail");

                        r.message.forEach(row => {
                            // Add child row first with default unsettled_payments = 0
                            const child = frm.add_child("pending_invoice_detail", {
                                invoice: row.name,
                                posting_date: row.posting_date,
                                due_date: row.due_date,
                                grand_total: row.grand_total,
                                outstanding_amount: row.outstanding_amount,
                                purchase_person: row.custom_purchase_person,
                                fiscal_year: row.fiscal_year,
                                location: row.location,
                                cost_center: row.cost_center,
                                budget_head: row.budget_head,
                                supplier: row.supplier,
                                amount_to_be_paid: row.outstanding_amount,
                                unsettled_payments: 0
                            });

                            // Step 2: Fetch unlinked unallocated payment sum for this supplier
                            frappe.call({
                                method: "vcm.erpnext_vcm.doctype.supplier_payment_request.supplier_payment_request.get_unlinked_payment_sum",
                                args: {
                                    supplier: row.supplier,
                                    company: frm.doc.company
                                },
                                callback: function(res) {
                                    if (res.message !== null) {
                                        child.unsettled_payments = res.message;
                                        frm.refresh_field("pending_invoice_detail");
                                    }
                                }
                            });
                        });
                    }
                }
            });
        }
    },
    
    request_type: function(frm) {
        const rt = frm.doc.request_type;
        // Handle visibility and requirement for fields based on the request type
        if (rt === "Advance Payments (against PO)") {
            // Show and require the 'purchase_order' field
            frm.set_df_property("purchase_order", "hidden", false);
            frm.set_df_property("purchase_order", "reqd", true);
            frm.set_df_property("remarks__justification", "reqd", false);
            frm.clear_table("pending_invoice_detail");
            frm.refresh_fields("pending_invoice_detail");
            frm.set_value("preq_amount", frm.doc.payment_requested || 0);
        } else if (rt === "Adhoc Payment") {
            frm.set_df_property("cost_center", "reqd", true);    
            frm.set_df_property("location", "reqd", true);
            frm.set_df_property("budget_head", "reqd", true); 
            frm.set_df_property("fiscal_year", "reqd", true);  // Unrequire purchase_order
            frm.set_df_property("remarks__justification", "reqd", true);
            frm.set_df_property("adhoc_amount", "reqd", true);
            frm.set_df_property("supplier", "reqd", true);                        
            frm.clear_table("po_payment_details");
            frm.refresh_fields("po_payment_details");
            frm.clear_table("pending_invoice_detail");
            frm.refresh_fields("pending_invoice_detail");
            frm.set_value("preq_amount", frm.doc.adhoc_amount || 0);
        } else if (rt === "Credit Payments (against Invoice)") {
            let total = 0;
            // Hide and unrequire all relevant fields for other request types
            frm.set_df_property("purchase_order", "hidden", true);
            frm.set_df_property("purchase_order", "reqd", false);
            frm.set_value("purchase_order", null);  // Optionally clear value
            frm.set_df_property("remarks__justification", "reqd", false);
            frm.set_value("po_amount", null);
            frm.set_value("advance__paid", null);
            frm.set_value("remaining_advance", null);
            (frm.doc.pending_invoice_detail || []).forEach(row => {
                if (row.include_in_payment) {
                    total += flt(row.amount_to_be_paid);
                }
            });
            frm.set_value("preq_amount", total);
        }        
    },
    purchase_order: function(frm) {
        const rt = frm.doc.request_type;
        // Handle visibility and requirement for fields based on the request type
        if (rt !== "Advance Payments (against PO)") 
            return

        if (!frm.doc.purchase_order) {
            frm.set_value("po_amount", null);
            frm.set_value("advance__paid", null);
            frm.set_value("remaining_advance", null);
            frm.clear_table("po_payment_details");
            frm.refresh_field("po_payment_details");
            return;
        }
        // Get PO info
        frappe.db.get_value("Purchase Order", frm.doc.purchase_order, ["grand_total", "advance_paid", "supplier", "custom_advance_amount"])
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
                    frm.set_value("supplier", r.message.supplier);
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
    },
    // Optional: update preq_amount when adhoc_amount changes
    adhoc_amount: function (frm) {
        if (frm.doc.request_type === "Adhoc Payment") {
            frm.set_value("preq_amount", frm.doc.adhoc_amount || 0);
        }
    },
    // Optional: update preq_amount when payment_requested changes
    payment_requested: function (frm) {
        if (frm.doc.request_type === "Advance Payments (against PO)") {
            frm.set_value("preq_amount", frm.doc.payment_requested || 0);
        }
    }
    
    
        
});

// Optional: also trigger update when a child row is modified
frappe.ui.form.on("PI Payment Details", {  // replace with your child table DocType
    include_in_payment: function (frm) {
        if (frm.doc.request_type === "Credit Payments (against Invoice)") {
            update_credit_payment_total(frm);
        }
    },
    amount_to_be_paid: function (frm) {
        if (frm.doc.request_type === "Credit Payments (against Invoice)") {
            update_credit_payment_total(frm);
        }
    }
});

function update_credit_payment_total(frm) {
    let total = 0;
    (frm.doc.pending_invoice_detail || []).forEach(row => {
        if (row.include_in_payment) {
            total += flt(row.amount_to_be_paid);
        }
    });
    frm.set_value("preq_amount", total);
}