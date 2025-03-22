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
    validate: function(frm) {
        if (!frm.doc.cost_center) {
            frappe.msgprint(__("Cost Center is mandatory."));
            frappe.validated = false;
        }
        
    },
    company:function(frm){
        frm.events.filter_company_items(frm);
    },
    filter_company_items:function(frm){
            frm.set_query("item_code", "items", function(doc, cdt, cdn) {
                return {
                    //query: "erpnext.controllers.queries.item_query",
                    filters: { 
                        is_purchase_item: 1,
                        has_variants: 0,
                        company: doc.company
                    },
                };                
            });    
    }
});
