// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM StoreRequisition", {
    refresh(frm) {
        //console.log("VCM Store Requisition.js entry:", frm.doc.name);
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(
            __("Create Material Request"),
            function () {
                frappe.call({
                method:
                    "vcm.erpnext_vcm.utilities.fetch_items_from_store_requisition.get_MR_items",
                args: {
                    item_req_doc_id: frm.doc.name,
                },
                callback: (r) => {
                    var doc = frappe.model.sync(r.message);
                    frappe.set_route("Form", doc[0].doctype, doc[0].name);
                },
                });
            },
            "Utilities"
            );
        }
        },
        company: function(frm) {
            if (frm.doc.company) {
                frm.set_query('cost_center', function() {
                    return {
                        filters: {
                            company: frm.doc.company  // Filtering Cost Centers by selected Company
                        }
                    };
                });
                frm.set_query('department', function() {
                    return {
                        filters: {
                            company: frm.doc.company  // Filtering Cost Centers by selected Company
                        }
                    };
                });
                frm.set_query('target_warehouse', function() {
                    return {
                        filters: {
                            company: frm.doc.company  // Filtering Cost Centers by selected Company
                        }
                    };
                });

            }
        },


});

//make_custom_buttons: function (frm) {
//  if (frm.doc.docstatus == 0 && frm.doc.status == "Draft") {
    //frm.add_custom_button(
    //  __("Submit for Approval"),
    //  () => frm.events.get_items_from_bom(frm),
    //  __("Utilities")
    //);
    //}

    //if (frm.doc.docstatus == 1 && frm.doc.status != "Stopped") {
    
        //frm.add_custom_button(__("Stop"), () => frm.events.update_status(frm, "Stopped"));
    //}
    //}


    frappe.ui.form.on("VCM Item Request Table", {  // Ensure this matches the Child Table Doctype
    item_code: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);  // Get the current row in the child table
        if (row.item_code) {
            frappe.call({
                method: "vcm.erpnext_vcm.utilities.fetch_items_from_store_requisition.get_item_details",  // Update with your app path
                args: { item_code: row.item_code },
                callback: function(response) {
                    if (response.message) {
                        frappe.model.set_value(cdt, cdn, "item_name", response.message.item_name);
                        frappe.model.set_value(cdt, cdn, "uom", response.message.uom);
                        frappe.model.set_value(cdt, cdn, "stock_uom", response.message.stock_uom);
                    }
                }
            });
        }
    }
});


    
