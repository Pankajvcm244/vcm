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
    }
});


frappe.ui.form.on("Material Request", {
    validate: function(frm) {
        
    }
});
