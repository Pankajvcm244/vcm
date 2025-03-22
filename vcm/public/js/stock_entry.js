frappe.ui.form.on("Stock Entry", {
    company:function(frm){
        frm.events.filter_company_items(frm);
    },
    filter_company_items:function(frm){
            frm.set_query("item_code", "items", function(doc, cdt, cdn) {
                return {
                    //query: "erpnext.controllers.queries.item_query",
                    filters: { 
                        is_stock_item: 1,
                        company: doc.company
                    },
                };                
            });    
    }
});