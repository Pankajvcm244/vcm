// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM PREQ DEPT ALM", {
	onload: function (frm) {
        // Assuming the fieldname of the child table in the parent form is also "alm_levels"
        frm.fields_dict["alm_levels"].grid.get_field("department").get_query = function (doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company || ""
                }
            };
        };
    }
});
