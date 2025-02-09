// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM Item Request", {
    refresh(frm) {
        //console.log("VCM Item Request.js entry:", frm.doc.name);
        frm.add_custom_button(
          __("Create Material Request"),
          function () {
            frappe.call({
              method:
                "vcm.erpnext_vcm.utilities.fetch_items_from_item_request.get_MR_items",
              args: {
                item_req_doc_id: frm.doc.name,
              },
              callback: (r) => {
                var doc = frappe.model.sync(r.message);
                frappe.set_route("Form", doc[0].doctype, doc[0].name);
              },
            });
          },
          "Create"
        );
      },
     

 });

 frappe.ui.form.on("VCM Item Request Table", {  // Ensure this matches the Child Table Doctype
    item_code: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);  // Get the current row in the child table
        if (row.item_code) {
            frappe.call({
                method: "vcm.erpnext_vcm.utilities.fetch_items_from_item_request.get_item_details",  // Update with your app path
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


    