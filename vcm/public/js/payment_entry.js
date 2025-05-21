frappe.ui.form.on("Payment Entry", {
    // onload: function(frm) {
    //     frm.set_query("custom_purchase_person", function() {
    //         return {
    //             filters: {
    //                 role: "Purchase User"
    //             },
    //             order_by: "full_name ASC"  // Sort alphabetically
    //         };
    //     });
    // },
    refresh: function(frm) {
        // fill purchase_person from PI and PO
        if (frm.doc.references && frm.doc.references.length > 0) {
            const ref = frm.doc.references[0]; // assuming single reference
            const doctype = ref.reference_doctype;
            const docname = ref.reference_name;
            if (doctype && docname) {
                frappe.db.get_doc(doctype, docname).then(source_doc => {
                    // Set value from source document's purchase_person
                    if (source_doc.custom_purchase_person) {
                        frm.set_value('custom_purchase_person', source_doc.custom_purchase_person);
                    }
                });
            }
        }
    },
    cost_center: function(frm) {
        fetch_budget_data(frm);
    },
    location: function(frm) {
        fetch_budget_data(frm);
    },
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