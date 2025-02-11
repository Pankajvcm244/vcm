//this is added by Pankaj to make Cost Center Mandatory in Material Request
//Pankaj 10-02-2025
frappe.ui.form.on("Material Request", {
    validate: function(frm) {
        if (!frm.doc.cost_center) {
            frappe.msgprint(__("Cost Center is mandatory."));
            frappe.validated = false;
        }
    }
});
