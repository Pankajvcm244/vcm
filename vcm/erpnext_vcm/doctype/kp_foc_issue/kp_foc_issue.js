



frappe.ui.form.on('KP FOC Issue', {
    onload: function(frm) {
        // Set default values on form load
        if (!frm.doc.company) {
            frm.set_value('company', 'HARE KRISHNA MOVEMENT VRINDAVAN');
        }
        if (!frm.doc.cost_center) {
            frm.set_value('cost_center', 'KRISHNA PRASADAM COUNTER - HKMV');
        }

        // Set default source_warehouse for all child table rows
        if (frm.doc.items && frm.doc.items.length > 0) {
            frm.doc.items.forEach(row => {
                if (!row.source_warehouse) {
                    frappe.model.set_value(row.doctype, row.name, "source_warehouse", "Krishna Prasadam POS - HKMV");
                }
            });
        }

        // Apply filter when the form is loaded
        apply_item_filter(frm);
    },

    company: function(frm) {
        // Apply filter when the company is changed
        apply_item_filter(frm);
    }
});

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
    },

    // Set default source_warehouse when adding a new row
    items_add: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "source_warehouse", "Krishna Prasadam POS - HKMV");
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

// Function to filter items based on the selected company
function apply_item_filter(frm) {
    if (frm.doc.company) {
        frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };
    }
}
