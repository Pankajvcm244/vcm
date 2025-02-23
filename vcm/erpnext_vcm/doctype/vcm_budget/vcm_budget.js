// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt


frappe.ui.form.on('VCM Budget', {
    before_save: function(frm) {
        console.log("Before Save: Child Table Data", frm.doc.budget_items);
        frm.doc.budget_items.forEach(row => {
            row.budget_head = row.budget_head || "Unknown";  // Default value
            row.current_budget = row.original_amount || 0.00;
            row.balance_budget = row.original_amount || 0.00;
            row.amended_till_now = row.amended_till_now || 0.00;
            row.used_budget = row.used_budget || 0.00;            
            row.proposed_amendment = row.proposed_amendment || 0.00;
            row.proposed_by = row.proposed_by || "Unknown";

        });
    },
    after_save: function(frm) {
        console.log("After Save: Child Table Data", frm.doc.budget_items);
    }
    

});