// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM ALM", {
    onload: function (frm) {
		frm.set_query("department", "vcm_alm_levels", function (doc, cdt, cdn) {
			return {
				filters: {
					company: doc.company
				}
			};
		});
	}

});


