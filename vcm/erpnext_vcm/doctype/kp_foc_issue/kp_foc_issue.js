
frappe.ui.form.on('KP FOC Issue', {
    onload: function(frm) {
        if (!frm.doc.company) {
            frm.set_value('company', 'HARE KRISHNA MOVEMENT VRINDAVAN');
        }
        if (!frm.doc.cost_center) {
            frm.set_value('cost_center', 'KRISHNA PRASADAM COUNTER - HKMV');
        }
        if (!frm.doc.material_recipient) {
            frm.set_value('material_recipient', 'kp_pos@gmail.com');
        }

        // Apply item group filter
        apply_item_filter(frm);  

        // Fetch projected stock qty
        fetch_projected_qty(frm);  
    },

    company: function(frm) {
        apply_item_filter(frm);
    },

    validate: function(frm) {
        fetch_projected_qty(frm);
    }
});

frappe.ui.form.on('FOC Items', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Reset rate
        frappe.model.set_value(cdt, cdn, "rate", "");

        if (row.item_code) {
            // Fetch Selling Price
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

            // Fetch Projected Qty
            fetch_projected_qty(frm, row);
        }
    },

    rate: function(frm, cdt, cdn) {
        calculate_total(frm);
    },

    quantity: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let available_stock = row.stock_quantity || 0;

        if (row.quantity > available_stock) {
            frappe.msgprint({
                title: __("Insufficient Stock"),
                indicator: "red",
                message: `Entered quantity (${row.quantity}) exceeds available stock (${available_stock}).`
            });

            console.warn(`Quantity exceeded for ${row.item_code}. Available: ${available_stock}, Entered: ${row.quantity}`);
            frappe.model.set_value(cdt, cdn, "quantity", available_stock);
        } else {
            calculate_total(frm);
        }
    },

    items_add: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "source_warehouse", "Krishna Prasadam POS - HKMV");
    }
});

function fetch_projected_qty(frm, row = null) {
    let items = row ? [row] : frm.doc.items;

    items.forEach(row => {
        if (row.item_code) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Bin",
                    filters: {
                        item_code: row.item_code,
                        warehouse: row.source_warehouse || "Krishna Prasadam POS - HKMV"
                    },
                    fields: ["projected_qty"]
                },
                callback: function(bin_res) {
                    let projected_qty = bin_res.message.length > 0 ? parseFloat(bin_res.message[0].projected_qty) : 0;
                    console.log(`Projected Qty for ${row.item_code}:`, projected_qty);

                    frappe.call({
                        method: "vcm.api.get_pos_reserved_qty",
                        args: {
                            item_code: row.item_code,
                            warehouse: row.source_warehouse || "Krishna Prasadam POS - HKMV"
                        },
                        callback: function(pos_res) {
                            let pos_reserved_qty = parseFloat(pos_res.message || 0);
                            let final_qty = projected_qty - pos_reserved_qty;
                            console.log(`Final Stock Qty for ${row.item_code}:`, final_qty);

                            frappe.model.set_value(row.doctype, row.name, "stock_quantity", final_qty);
                            frm.refresh_field("items");
                        }
                    });
                }
            });
        }
    });
}

function calculate_total(frm) {
    let total = 0;
    $.each(frm.doc.items || [], function(i, row) {
        total += parseFloat(row.rate || 0) * parseFloat(row.quantity || 1);
    });

    frm.set_value("grand_total", parseFloat(total).toFixed(2));
}


// function apply_item_filter(frm) {
//     frappe.call({
//         method: "vcm.api.get_krishna_prasadam_items",
//         callback: function(r) {
//             if (r.message) {
//                 let item_codes = r.message.map(item => item.name);
//                 frm.fields_dict.items.grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
//                     return {
//                         filters: {
//                             name: ["in", item_codes]
//                         }
//                     };
//                 };
//             }
//         }
//     });
// }


function apply_item_filter(frm) {
    frm.fields_dict.items.grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
        return {
            query: "erpnext.controllers.queries.item_query",
            filters: {
                name: ["like", "KP%"]
            }
        };
    };
}
