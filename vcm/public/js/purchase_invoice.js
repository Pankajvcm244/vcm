frappe.ui.form.on("Purchase Invoice", {
    onload: function(frm) {
        frm.set_query("custom_purchase_person", function() {
            return {
                query: "vcm.erpnext_vcm.utilities.fetch_user_data.vcm_get_users_with_role",
                filters: {
                    role: "Purchase User"
                }
            };
        });
    }
});