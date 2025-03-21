frappe.ui.form.on("Purchase Invoice", {
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