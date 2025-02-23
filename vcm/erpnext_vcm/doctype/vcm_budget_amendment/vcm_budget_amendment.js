// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM Budget Amendment", {

    cost_center: function(frm) {
        console.log("Cost center calling fetch_budget_data.js entry:", frm.doc.name);
        fetch_budget_data(frm);
    }
    
});






function fetch_budget_data(frm) {
    console.log("in fetch_budget_data entry:", frm.doc.name);
    if (!frm.doc.company || !frm.doc.fiscal_year || !frm.doc.cost_center) {
        frappe.msgprint(__('Please fill Company, Fiscal Year, and Cost Center.'));
        return;
    }

    frappe.call({
        method: 'vcm.erpnext_vcm.doctype.vcm_budget.vcm_budget.get_budget_items',
        args: {
            company: frm.doc.company,
            fiscal_year: frm.doc.fiscal_year,
            cost_center: frm.doc.cost_center
        },
        callback: function(response) {

            if (response.message.length === 0) {
                frappe.msgprint(__('No budget records found for this Company, Fiscal Year, and Cost Center.'));
                return;
            }            
            console.log("in fetch_budget_data entry -2 :", response.message);
             // Clear the existing table
            frm.clear_table('budget_amendment_items');

            response.message.forEach(item => {
                let row = frm.add_child('budget_amendment_items');
                console.log("in fetch_budget_data entry 2-1-1 :", item.budget_head, item.original_amount,  );

                row.budget_head = item.budget_head;
                row.original_amount = item.original_amount || 0;  
                row.current_budget = item.original_amount || 0; //initialize current budget as original amount
                row.amended_till_now = item.amended_till_now || 0;
                row.used_budget = item.used_budget || 0;
                row.balance_budget = item.original_amount || 0; //initialize balance budget as original amount
                row.proposed_amendment = 0;
            });

            // Refresh the child table to update UI
            frm.refresh_field('budget_amendment_items');
            
            
        }
    });
}