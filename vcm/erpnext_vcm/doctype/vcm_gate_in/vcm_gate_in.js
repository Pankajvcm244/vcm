// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM Gate-In", {
    //this refresh was added due to double pop-up when supplier is selected
    refresh: function(frm) {
        frm.meta.supplier_dialog_opened = false; // Reset flag when form refreshes
        //In case User tagged Gate-In by mistake and wants to Free Gate-In
        if (frm.doc.status === "Received" && frappe.user.has_role("Administrator")) {
            frm.add_custom_button(__('Change Status to Pending'), function() {
                frappe.call({
                    method: "vcm.erpnext_vcm.doctype.vcm_gate_in.vcm_gate_in.update_gate_in_status",
                    args: {
                        gate_in_name: frm.doc.name,
                        new_status: "Pending"
                    },
                    callback: function(response) {
                        if (response.message) {
                            frm.reload_doc();
                        }
                    }
                });
            }).addClass("btn-danger");
        }
        if (frm.doc.status === "Pending" && frappe.user.has_role("Administrator")) {
            frm.add_custom_button(__('Change Status to Received'), function() {
                frappe.call({
                    method: "vcm.erpnext_vcm.doctype.vcm_gate_in.vcm_gate_in.update_gate_in_status",
                    args: {
                        gate_in_name: frm.doc.name,
                        new_status: "Received"
                    },
                    callback: function(response) {
                        if (response.message) {
                            frm.reload_doc();
                        }
                    }
                });
            }).addClass("btn-danger");
        }          
    },
    supplier: function(frm) {
        if (!frm.doc.supplier || frm.supplier_dialog_opened) return;
        frm.supplier_dialog_opened = true; // Prevent duplicate popups
        //console.log("VCM Gate-In.js Supplier:", frm.supplier_dialog_opened, frm.doc.supplier);
        //console.trace();

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Purchase Order",
                filters: { "supplier": frm.doc.supplier, "company": frm.doc.company, "status": "To Receive and Bill" },
                fields: ["name", "transaction_date", "grand_total"]
            },
            callback: function(r) { 
                if (r.message.length > 0) {
                    let po_options = r.message.map(po => ({ label: `${po.name} - ${po.grand_total}`, value: po.name }));

                    let d = new frappe.ui.Dialog({
                        title: 'Select Purchase Order',
                        fields: [
                            { fieldname: 'po', fieldtype: 'Select', label: 'Purchase Order', options: po_options },
                        ],
                        primary_action_label: 'Select',
                        primary_action(values) {
                            frm.set_value("purchase_order", values.po);
                            d.hide();
                        }
                    });

                    d.show();
                    //frm.supplier_dialog_opened = false; // Reset flag after response
                    //console.log("VCM Gate-In.js Supplier 2:", frm.supplier_dialog_opened, frm.doc.supplier);
                } else {
                    frappe.msgprint("No Purchase Orders found for this supplier.");
                }
            }
        });
    },
    purchase_order: function(frm) {
        if (!frm.doc.purchase_order) return;
        //make Purchase person read only based upon PO field
        toggle_purchase_person(frm);

        // Fetch all items from the selected Purchase Order
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Purchase Order",
                name: frm.doc.purchase_order
            },
            callback: function(r) {
                if (r.message) {
                    let po_data = r.message;
                    // Fetch and set the Purchase Person
                    if (po_data.custom_purchase_person) {
                        //gate-in form still has purchase_person
                        frm.set_value("purchase_person", po_data.custom_purchase_person);
                    } else {
                        frm.set_value("purchase_person", "Not Available");
                    }
                    frm.set_value("company", po_data.company);
                    frm.set_value("cost_center", po_data.cost_center);
                    frm.set_value("budget_head", po_data.budget_head);
                    frm.clear_table("items"); // Clear existing items before adding new ones

                    po_data.items.forEach(item => {
                        let row = frm.add_child("items");
                        row.item_code = item.item_code;
                        row.item_name = item.item_name;
                        row.qty = item.qty;
                        row.uom = item.uom;
                        row.rate = item.rate;
                        row.amount = item.amount;
                        row.required_by = item.schedule_date;
                    });

                    frm.refresh_field("items"); // Refresh the table to show new items
                }
            }
        });
    },
    onload: function(frm) {
        frm.set_query("custom_purchase_person", function() {
            return {
                query: "vcm.erpnext_vcm.utilities.fetch_user_data.vcm_get_users_with_role",
                filters: {
                    role: "Purchase User"
                }
            };
        });               
    },
    validate: function(frm) {
        if (!frm.doc.purchase_order && !frm.doc.bill_number) {
            frappe.throw(__('Please enter at least one of PO Number, Bill Number, or Challan Number.'));
        }
    },
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (!frm.doc.purchase_order && row.item_code) {
            frappe.db.get_value('Item', row.item_code, ['item_name', 'uom'], function(value) {
                if (value) {
                    frappe.model.set_value(cdt, cdn, 'item_name', value.item_name);
                    frappe.model.set_value(cdt, cdn, 'uom', value.uom);
                    
                }
            });
        }
    },
    company: function(frm) {
        if (frm.doc.company) {
            frm.set_query('cost_center', function() {
                return {
                    filters: {
                        company: frm.doc.company,  // Filtering Cost Centers by selected Company
                        is_group: 0  // Only leaf cost centers
                    }
                };
            });       
        }
    }
    // , 
    // cost_center: function(frm) {
    //     fetch_budget_data(frm);
    // },
    // location: function(frm) {
    //     fetch_budget_data(frm);
    // }   
});

function toggle_purchase_person(frm) {
    if (!frm.doc.purchase_order) {
        frm.set_df_property('custom_purchase_person', 'read_only', 0);  // Make editable
    } else {
        frm.set_df_property('custom_purchase_person', 'read_only', 1);  // Make read-only
    }
}


function fetch_budget_data(frm) {
    if (frm.doc.cost_center && frm.doc.location && frm.doc.company) {
        frappe.call({
            method: "vcm.erpnext_vcm.doctype.vcm_budget.vcm_budget.get_vcm_budget_head",
            args: {
                cost_center: frm.doc.cost_center,
                location: frm.doc.location,
                company: frm.doc.company
            },
            callback: function(response) {
                if (response.message) {
                    let budget_heads = response.message.budget_heads;

                    // Set query for Budget Head field
                    frm.set_query("budget_head", function() {
                        return {
                            filters: [["name", "in", budget_heads]]
                        };
                    });
                }
            }
        });
    }
}