
frappe.ui.form.on('Stock Entry', {
    company: function(frm) {
        frm.events.filter_company_items(frm);
    },

    filter_company_items: function(frm) {
        frm.set_query("item_code", "items", function(doc, cdt, cdn) {
            return {
                //query: "erpnext.controllers.queries.item_query",
                filters: { 
                    is_stock_item: 1,
                    company: doc.company
                }
            };
        });
    }
});

// Stock Entry Detail Child Table Script
frappe.ui.form.on('Stock Entry Detail', {
    qty: function(frm, cdt, cdn) {
        // Validate if Stock Entry Type is 'Material Transfer' or 'Material Issue'
        if (["Material Transfer", "Material Issue"].includes(frm.doc.stock_entry_type)) {
            let row = frappe.get_doc(cdt, cdn);
            let available_stock = row.actual_qty || 0;

            if (row.qty > available_stock) {
                frappe.msgprint({
                    title: __("Insufficient Stock"),
                    indicator: "red",
                    message: `Entered quantity (${row.qty}) exceeds available stock (${available_stock}).`
                });

                frappe.model.set_value(cdt, cdn, "qty", available_stock);
            }
        }
    }
});

