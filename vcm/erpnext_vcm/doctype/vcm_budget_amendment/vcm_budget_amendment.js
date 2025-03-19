// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("VCM Budget Amendment", {
    refresh: function(frm) {
        calculate_proposed_amended_amount(frm);
    },
    budget_items_add: function(frm, cdt, cdn) {
        calculate_proposed_amended_amount(frm);
    },
    budget_items_remove: function(frm, cdt, cdn) { 
        calculate_proposed_amended_amount(frm);
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
        }
    },
    cost_center: function(frm) {
        //console.log("Cost center calling fetch_budget_data.js entry:", frm.doc.name);
        fetch_budget_data(frm);
    },
    validate: function(frm) {
        let budget_heads = [];
        let duplicate_found = false;
        //console.log("Budget amendment:", frm.doc.name);
        $.each(frm.doc.budget_amendment_items || [], function(i, row) {
            //console.log("Budget amendment:", frm.doc.budget_amendment_items);
            if (budget_heads.includes(row.budget_head)) {
                frappe.msgprint(__('Duplicate Budget Head: {0}', [row.budget_head]));
                frappe.validated = false;
                duplicate_found = true;
                return false;  // Exit loop early
            }
            budget_heads.push(row.budget_head);
        });
        if (duplicate_found) {
            frappe.throw(__('Each Budget Head must be unique.'));
        }
    }
    
});

frappe.ui.form.on('VCM Budget Amendment Child Table', {
    proposed_amendment: function(frm, cdt, cdn) {
        calculate_proposed_amended_amount(frm);
    }
});

function calculate_proposed_amended_amount(frm) {
    let total = 0;
    $.each(frm.doc.budget_amendment_items || [], function(i, row) {
        //console.log("Budget child Table:", frm.doc.budget_items,row.original_amount, total );
        //We are doing this for origional amount as for budget creation based upon this value ALM will follow
        total += row.proposed_amendment || 0;
    });
    frm.set_value("total_proposed_amendment", total);
    frm.refresh_field("total_proposed_amendment");
}




function fetch_budget_data(frm) {
    //console.log("in fetch_budget_data entry:", frm.doc.name);
    if (!frm.doc.company || !frm.doc.fiscal_year || !frm.doc.cost_center) {
        frappe.msgprint(__('Please fill Company, Fiscal Year, and Cost Center.'));
        return;
    }

    frappe.call({
        method: 'vcm.erpnext_vcm.doctype.vcm_budget.vcm_budget.get_budget_items',
        args: {
            company: frm.doc.company,
            fiscal_year: frm.doc.fiscal_year,
            cost_center: frm.doc.cost_center,
            location: frm.doc.location
        },
        callback: function(response) {

            if (response.message.length === 0) {
                frappe.msgprint(__('No budget records found for this Company, LOcation, Fiscal Year, Location, and Cost Center.'));
                return;
            }            
            //console.log("in fetch_budget_data entry -2 :", response.message);
             // Clear the existing table
            frm.clear_table('budget_amendment_items');

            response.message.forEach(item => {
                let row = frm.add_child('budget_amendment_items');
                //console.log("in fetch_budget_data entry 2-1-1 :", item.budget_head, item.original_amount,  );
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