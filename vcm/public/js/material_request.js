//this is added by Pankaj to make Cost Center Mandatory in Material Request
//Pankaj 10-02-2025
frappe.ui.form.on("Material Request", {
    validate: function(frm) {
        if (!frm.doc.cost_center) {
            frappe.msgprint(__("Cost Center is mandatory."));
            frappe.validated = false;
        }
        // Check if Material Request Type is "Purchase" or "Material Transfer"
        if (frm.doc.material_request_type == "Purchase" || frm.doc.material_request_type == "Material Transfer") {
            if (!frm.doc.set_warehouse) {  // Replace with your Target Warehouse fieldname if different
                frappe.msgprint({
                    title: __("Validation Error"),
                    message: __("Target Warehouse is mandatory for Purchase and Material Transfer requests."),
                    indicator: "red"
                });
                frappe.validated = false;
            }
        }
    },    
    company:function(frm){
        frm.events.filter_company_items(frm);
    },
    filter_company_items:function(frm){
            frm.set_query("item_code", "items", function(doc, cdt, cdn) {
                if (doc.material_request_type == "Customer Provided") {
                    return {
                        //query: "erpnext.controllers.queries.item_query",
                        filters: {
                            customer: doc.customer,
                            is_stock_item: 1
                        },
                    };
                } else if (doc.material_request_type == "Purchase") {
                    return {
                        //query: "erpnext.controllers.queries.item_query",
                        filters: { 
                            is_purchase_item: 1,
                            company: doc.company
                         },
                    };
                } else {
                    return {
                        //query: "erpnext.controllers.queries.item_query",
                        filters: { 
                            is_stock_item: 1,
                            company: doc.company
                        },
                    };
                }
            });    
    }    
});


frappe.ui.form.on("Material Request", {
    validate: function(frm) {
        
    }
});
