// frappe.ui.form.on("Purchase Order", {
//     onload: function(frm) {
//         frm.set_query("custom_purchase_person", function() {
//             return {
//                 query: "vcm.erpnext_vcm.utilities.fetch_user_data.vcm_get_users_with_role",
//                 filters: {
//                     role: "Purchase User"
//                 }
//             };
//         });
//     }
// });

frappe.ui.form.on("Purchase Order", {
    onload: function(frm) {
        frm.set_query("custom_purchase_person", function() {
            return {
                filters: {
                    role: "Purchase User"
                },
                order_by: "full_name ASC"  // Sort alphabetically
            };
        });
    },
    // This code is linking all MRN linked to PO in custom_linked_material_request field
    refresh(frm) {
        if (frm.doc.docstatus !== 0) return;  // Only run for Draft

        if (!frm.doc.items || frm.doc.items.length === 0) return;

        let material_requests = new Set();

        frm.doc.items.forEach(row => {
            if (row.material_request) {
                material_requests.add(row.material_request);
            }
        });

        let requests_string = Array.from(material_requests).join(', ');
        frm.set_value('custom_linked_material_request', requests_string);
    },

    validate: function(frm) {
        if (!frm.doc.cost_center) {
            frappe.msgprint(__("Cost Center is mandatory."));
            frappe.validated = false;
        }
        
    },
    company:function(frm){
        frm.events.filter_company_items(frm);
    },
    cost_center: function(frm) {
        fetch_budget_data(frm);
    },
    location: function(frm) {
        fetch_budget_data(frm);
    },
    filter_company_items:function(frm){
            frm.set_query("item_code", "items", function(doc, cdt, cdn) {
                return {
                    //query: "erpnext.controllers.queries.item_query",
                    filters: { 
                        is_purchase_item: 1,
                        has_variants: 0,
                        is_stock_item: 0,
                        company: doc.company
                    },
                };                
            });    
    }
});


function fetch_budget_data(frm) {
    if (frm.doc.cost_center && frm.doc.location && frm.doc.company) {
        frappe.call({
            method: "vcm.erpnext_vcm.doctype.vcm_budget.vcm_budget.get_vcm_budget_head",
            args: {
                cost_center: frm.doc.cost_center,
                location: frm.doc.location,
                company: frm.doc.company
            },
            callback: function(response) {
                if (response.message) {
                    let budget_heads = response.message.budget_heads;

                    // Set query for Budget Head field
                    frm.set_query("budget_head", function() {
                        return {
                            filters: [["name", "in", budget_heads]]
                        };
                    });
                }
            }
        });
    }
}