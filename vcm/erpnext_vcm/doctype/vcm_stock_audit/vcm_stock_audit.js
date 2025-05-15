// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM Stock Audit", {
	onload: function(frm) {
		frm.trigger('toggle_item_columns');
        if (frm.is_new() && !frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.now_date());
        }
    }, 
	warehouse: function(frm) {
        frm.trigger('toggle_item_columns');
    },
    toggle_item_columns: function(frm) {
        let show_columns = frm.doc.warehouse && frm.doc.warehouse.includes("Operations Store - HKMV");

        ['expected_quantity', 'qty_difference'].forEach(fieldname => {
            frm.fields_dict['items'].grid.get_field(fieldname).df.hidden = !show_columns;
        });

        frm.fields_dict['items'].grid.refresh();
    },
	refresh: function(frm) {
        frm.add_custom_button("Pull Items with Stock > 0", function() {
            if (!frm.doc.warehouse) {
                frappe.msgprint("Please select a Warehouse first.");
                return;
            }
			// Check if warehouse contains "Operations Store"
            // if (!frm.doc.warehouse.includes("Operations Store - HKMV")) {
            //     frappe.msgprint("This action is only allowed for 'Operations Store - HKMV' warehouses.");
            //     return;
            // }
			const allowed_warehouses = [
				"Operations Store - HKMV",
				"Operations Store - VCMT",
				"Krishna Prasadam POS - HKMV",
				"Annadan Store - HKMV",
				"Sadhu Seva - HKMV",
				"Pushpanjali Stores - VCMT",
				"Krishnamrita Store - HKMV"
			];

			if (!allowed_warehouses.includes(frm.doc.warehouse)) {
				frappe.msgprint("This action is only allowed for the following warehouses: " + allowed_warehouses.join(", "));
				return;
			}

            frappe.call({
                method: "vcm.erpnext_vcm.doctype.vcm_stock_audit.vcm_stock_audit.get_items_with_stock",
                args: {
                    warehouse: frm.doc.warehouse
                },
                callback: function(r) {
                    if (r.message) {
                        frm.clear_table("items");

                        r.message.forEach(item => {
                            let row = frm.add_child("items", {
                                item_code: item.item_code,
                                item_name: item.item_name,
                                uom: item.stock_uom,
                                expected_quantity: item.actual_qty
                            });
                        });

                        frm.refresh_field("items");
                    }
                }
            });
        });
    }
	// warehouse:function(frm){
    //     frm.events.filter_warehouse_items(frm);
    // },
	// filter_warehouse_items:function(frm){
	// 	frm.set_query("item_code", "items", function(doc, cdt, cdn) {
	// 		return {
	// 			filters: { 
	// 				default_warehouse: frm.doc.warehouse
	// 			},
	// 		};                
	// 	});    
	// }  
});


frappe.ui.form.on('VCM Stock Audit Child Table', {	

	actual_quantity: function(frm, cdt, cdn) {
		//console.log("item code actual_qty:");
		const row = locals[cdt][cdn];		
		// Set timestamp whenevr we type actual quantity
		frappe.model.set_value(cdt, cdn, 'counted_at', frappe.datetime.now_datetime());

		// Recalculate difference (optional)
		if (row.expected_quantity !== null && row.expected_quantity !== undefined) {
			let diff = row.actual_quantity - row.expected_quantity;
			frappe.model.set_value(cdt, cdn, 'qty_difference', diff);
			//console.log("Difference Qty C:", diff);
		}
		
	},    
    items_add: function(frm, cdt, cdn) {
		//console.log("item code items_add:");
		let row = locals[cdt][cdn];
		if (row.actual_quantity) {
			frappe.meta.get_docfield('VCM Stock Audit Child Table', 'actual_quantity', frm.doc.name).read_only = 1;
		}
	},
    item_code: function(frm, cdt, cdn) {
		console.log("item item_code:");
		let row = locals[cdt][cdn];
		if (!frm.doc.warehouse) {
			frappe.msgprint("Please select a Warehouse first.");
		}
		if (row.item_code) {
			// Check for duplicates
			let duplicate = frm.doc.items.find((r) => r.item_code === row.item_code && r.name !== row.name);
			if (duplicate) {
				frappe.msgprint(`Item ${row.item_code} is already added.`);
				frappe.model.set_value(cdt, cdn, "item_code", null);
				frappe.model.set_value(cdt, cdn, "item_name", null);
				frappe.model.set_value(cdt, cdn, "uom", null);
				return;
			}
			// Fetch item name and UOM
			frappe.model.with_doc("Item", row.item_code, () => {
				let item_doc = frappe.model.get_doc("Item", row.item_code);
				frappe.model.set_value(cdt, cdn, "item_name", item_doc.item_name);
				frappe.model.set_value(cdt, cdn, "stock_uom", item_doc.stock_uom);
			});
			//console.log("Fetched Item Details:", row.item_code);

			// Fetch expected quantity
			frappe.call({				
				method: "vcm.erpnext_vcm.doctype.vcm_stock_audit.vcm_stock_audit.get_vcm_current_qty",
				args: {
					item_code: row.item_code,
					warehouse: frm.doc.warehouse
				},
				callback: function (r) {
					if (r.message !== undefined) {
						console.log("return from callback:", r.message, row.item_code);
						frappe.model.set_value(cdt, cdn, "expected_quantity", r.message);
					}
				}
			});
		} 
	}
});
