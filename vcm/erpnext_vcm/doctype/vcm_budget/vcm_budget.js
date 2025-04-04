// Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
// For license information, please see license.txt


frappe.ui.form.on('VCM Budget', {
    refresh: function(frm) {
        //console.log("Refresh", frm.doc.budget_items);
        calculate_total_amount(frm);
        calculate_amended_amount(frm);
        calculate_used_amount(frm);
        calculate_balance_amount(frm);
        calculate_Payment_Entry_amount(frm);
        calculate_Purchase_Invoice_amount(frm);
        calculate_Purchase_Order_amount(frm);
        calculate_JE_amount(frm);
        calculate_used_percentage(frm);
        calculate_salary_amount(frm);
        calculate_fa_amount(frm);
        calculate_pool_amount(frm);

    },
    budget_items_add: function(frm, cdt, cdn) {
        calculate_total_amount(frm);
        calculate_amended_amount(frm);
        calculate_used_amount(frm);
        calculate_balance_amount(frm);
        calculate_Payment_Entry_amount(frm);
        calculate_Purchase_Invoice_amount(frm);
        calculate_Purchase_Order_amount(frm);
        calculate_JE_amount(frm);
        calculate_salary_amount(frm);
        calculate_fa_amount(frm);
        calculate_pool_amount(frm);
    },
    budget_items_remove: function(frm, cdt, cdn) {
        calculate_total_amount(frm);
        calculate_amended_amount(frm);
        calculate_used_amount(frm);
        calculate_balance_amount(frm);
        calculate_Payment_Entry_amount(frm);
        calculate_Purchase_Invoice_amount(frm);
        calculate_Purchase_Order_amount(frm);
        calculate_JE_amount(frm);
        calculate_salary_amount(frm);
        calculate_fa_amount(frm);
        calculate_pool_amount(frm);
    },
    before_save: function(frm) {
        console.log("Before Save: Child Table Data", frm.doc.budget_items);
        frm.doc.budget_items.forEach(row => {
            row.original_amount = row.original_amount || 0.00;
            row.budget_head = row.budget_head || "Unknown";  // Default value
            row.amended_till_now = row.amended_till_now || 0.00;                       
            row.proposed_amendment = row.proposed_amendment || 0.00;
            row.proposed_by = row.proposed_by || "Unknown";
            row.paid_payment_entry = row.paid_payment_entry || 0;
            row.unpaid_purchase_invoice = row.unpaid_purchase_invoice || 0;
            row.unpaid_purchase_order = row.unpaid_purchase_order || 0;
            row.additional_je = row.additional_je || 0;
            row.current_budget = row.original_amount +  row.amended_till_now  || 0.00;            
            row.used_budget = row.paid_payment_entry + row.unpaid_purchase_invoice + row.unpaid_purchase_order + row.additional_je || 0.00; 
            row.balance_budget = row.current_budget - row.used_budget || 0.00;
        });
    },
    after_save: function(frm) {
        console.log("After Save: Child Table Data", frm.doc.budget_items);
    },
    validate: function(frm) {
        let budget_heads = [];
        let duplicate_found = false;

        $.each(frm.doc.budget_items || [], function(i, row) {
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
    }
});

frappe.ui.form.on('VCM Budget Child Table', {
    original_amount: function(frm, cdt, cdn) {
        calculate_total_amount(frm);
        calculate_amended_amount(frm);
        calculate_used_amount(frm);
        calculate_balance_amount(frm);
    }

});

function calculate_total_amount(frm) {
    let total = 0;
    $.each(frm.doc.budget_items || [], function(i, row) {
        //console.log("Budget child Table:", frm.doc.budget_items,row.original_amount, total );
        //We are doing this for origional amount as for budget creation based upon this value ALM will follow
        total += row.original_amount || 0;
    });
    frm.set_value("total_amount", total);
    frm.refresh_field("total_amount");
}

function calculate_amended_amount(frm) {
    let total = 0;
    $.each(frm.doc.budget_items || [], function(i, row) {
        //console.log("Budget child Table:", frm.doc.budget_items,row.original_amount, total );
        //We are doing this for origional amount as for budget creation based upon this value ALM will follow
        total += row.amended_till_now || 0;
    });
    frm.set_value("total_amended_amount", total);
    frm.refresh_field("total_amended_amount");
}

function calculate_used_percentage(frm) {
    let percent = 0;
    percent = (frm.doc.total_used_amount / (frm.doc.total_amount + frm.doc.total_amended_amount )) * 100;
    frm.set_value("used_percent", percent);
    frm.refresh_field("used_percent");
}

function calculate_balance_amount(frm) {
    let total = 0;
    $.each(frm.doc.budget_items || [], function(i, row) {
        //console.log("Budget child Table:", frm.doc.budget_items,row.original_amount, total );
        //We are doing this for origional amount as for budget creation based upon this value ALM will follow
        total += row.balance_budget || 0;
    });
    frm.set_value("total_balance_amount", total);
    frm.refresh_field("total_balance_amount");
}

function calculate_used_amount(frm) {
    let total = 0;
    $.each(frm.doc.budget_items || [], function(i, row) {
        //console.log("Budget child Table:", frm.doc.budget_items,row.original_amount, total );
        //We are doing this for origional amount as for budget creation based upon this value ALM will follow
        total += row.used_budget || 0;
    });
    frm.set_value("total_used_amount", total);
    frm.refresh_field("total_used_amount");
}

function calculate_Payment_Entry_amount(frm) {
    let total = 0;
    $.each(frm.doc.budget_items || [], function(i, row) {
        //console.log("Budget child Table:", frm.doc.budget_items,row.original_amount, total );
        //We are doing this for origional amount as for budget creation based upon this value ALM will follow
        total += row.paid_payment_entry || 0;
    });
    frm.set_value("total_paid_payment_entry", total);
    frm.refresh_field("total_paid_payment_entry");
}

function calculate_Purchase_Invoice_amount(frm) {
    let total = 0;
    $.each(frm.doc.budget_items || [], function(i, row) {
        //console.log("Budget child Table:", frm.doc.budget_items,row.original_amount, total );
        //We are doing this for origional amount as for budget creation based upon this value ALM will follow
        total += row.unpaid_purchase_invoice || 0;
    });
    frm.set_value("total_unpaid_purchase_invoice", total);
    frm.refresh_field("total_unpaid_purchase_invoice");
}

function calculate_Purchase_Order_amount(frm) {
    let total = 0;
    $.each(frm.doc.budget_items || [], function(i, row) {
        //console.log("Budget child Table:", frm.doc.budget_items,row.unpaid_purchase_order, total );
        //We are doing this for origional amount as for budget creation based upon this value ALM will follow
        total += row.unpaid_purchase_order || 0;
    });
    frm.set_value("total_unpaid_purchase_order", total);
    frm.refresh_field("total_unpaid_purchase_order");
}

function calculate_JE_amount(frm) {
    let total = 0;
    $.each(frm.doc.budget_items || [], function(i, row) {
        //console.log("Budget child Table:", frm.doc.budget_items,row.original_amount, total );
        //We are doing this for origional amount as for budget creation based upon this value ALM will follow
        total += row.additional_je || 0;
    });
    frm.set_value("total_additional_je", total);
    frm.refresh_field("total_additional_je");
}


function calculate_salary_amount(frm) {
    let salary_used = 0;
    let salary_balance = 0;
    //console.log("calculate_salary_amount:" );
    $.each(frm.doc.budget_items || [], function(i, row) {
        if (row.budget_head === "Salaries & Wages") {  // ✅ Check only Salary Budget Head           
            salary_used += row.used_budget || 0;
            salary_balance += row.balance_budget || 0;  
            //console.log("calculate_salary_amount 1:", row.used_budget,row.balance_budget, salary_balance );
        }
    });

    // ✅ Set the calculated values to Salary fields
    frm.set_value("salary_used", salary_used);
    frm.set_value("salary_balance", salary_balance); 
    frm.refresh_field("salary_used");
    frm.refresh_field("salary_balance");
}

function calculate_fa_amount(frm) {
    let fa_used = 0;
    let fa_balance = 0;

    $.each(frm.doc.budget_items || [], function(i, row) {
        if (row.budget_head === "Fixed Assets") {  // ✅ Check only Salary Budget Head
            fa_used += row.used_budget || 0;
            fa_balance += row.balance_budget || 0;  
        }
    });

    // ✅ Set the calculated values to Salary fields
    frm.set_value("fa_used", fa_used);
    frm.set_value("fa_balance", fa_balance); 
    frm.refresh_field("fa_used");
    frm.refresh_field("fa_balance");
}

function calculate_pool_amount(frm) {
    let pool_budget_used = 0;
    let pool_budget_balance = 0;
    let pool_budget_total = 0;

    $.each(frm.doc.budget_items || [], function(i, row) {
        if (row.budget_head !== "Fixed Assets" && row.budget_head !== "Salaries & Wages" ) {  
            pool_budget_used += row.used_budget || 0;
            pool_budget_balance += row.balance_budget || 0;
            pool_budget_total += row.current_budget || 0;  
            //console.log("calculate_pool_1 :", pool_budget_used, pool_budget_balance, pool_budget_total);
        }
    });

    frm.set_value("pool_budget_used", pool_budget_used);
    frm.set_value("pool_budget_balance", pool_budget_balance); 
    frm.set_value("pool_budget_total", pool_budget_total);
    frm.refresh_field("pool_budget_used");
    frm.refresh_field("pool_budget_balance");
    frm.refresh_field("pool_budget_total");
    //console.log("calculate_pool_amount:", pool_budget_used, pool_budget_balance, pool_budget_total);
}