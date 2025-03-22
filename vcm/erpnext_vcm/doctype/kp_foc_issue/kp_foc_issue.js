frappe.ui.form.on('FOC Items', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Reset Rate before fetching new value
        frappe.model.set_value(cdt, cdn, "rate", "");

        if (row.item_code) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Item Price",
                    filters: {
                        item_code: row.item_code,
                        selling: 1
                    },
                    fieldname: ["price_list_rate"]
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "rate", r.message.price_list_rate);
                    } else {
                        frappe.msgprint("No Selling Price found for this Item.");
                    }
                    calculate_total(frm);
                }
            });
        }
    },
    rate: function(frm, cdt, cdn) {
        calculate_total(frm);
    },
    quantity: function(frm, cdt, cdn) {
        calculate_total(frm);
    }
});

function calculate_total(frm) {
    let total = 0;
    $.each(frm.doc.items || [], function(i, row) {
        total += parseFloat(row.rate || 0) * parseFloat(row.quantity || 1);
    });

    // Set grand total with 2 decimal places
    frm.set_value("grand_total", parseFloat(total).toFixed(2));
}
