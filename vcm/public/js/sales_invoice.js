// This file was  modified as per vcm app requirements default place of supply as UP
//If user wants , they can change it, but defulat will be UP and not from customer address
//Pankaj 06-02-2025
frappe.ui.form.on('Sales Invoice', {
    onload: function(frm) {
        if (frm.is_new()) {
            frm.set_value("place_of_supply", "09-Uttar Pradesh");
        }
    },
    refresh: function(frm) {
        if (frm.is_new()) {
            frm.set_value("place_of_supply", "09-Uttar Pradesh");
        }    
    }

});


