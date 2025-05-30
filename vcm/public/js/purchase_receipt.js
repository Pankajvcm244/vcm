// import {get_EZPL_string} from "./barcode-printing.js";
// This file was taken from hkm app and modified as per vcm app requirements
//Pankaj 17-01-2025

frappe.ui.form.on('Purchase Receipt', {
    onload(frm) {
        //console.log("Purchase Receipt.js entry:", frm.doc.name);
        frm.add_custom_button(
          __("Print labels from Purchase Receipt"),
          function () {
            frappe.call({
              method:
                "vcm.erpnext_vcm.utilities.fetch_items_from_purchase_receipt.get_PR_items",
              args: {
                pr_doc_id: frm.doc.name,
              },
              callback: (r) => {
                var doc = frappe.model.sync(r.message);
                frappe.set_route("Form", doc[0].doctype, doc[0].name);
              },
            });
          },
          "Utilities"
        );        
    },
    on_submit: function(frm) {
        if (frm.doc.custom_gate_in_reference) {  // Assuming there's a link field in Purchase Receipt pointing to Gate In
            frappe.call({
                method: 'frappe.client.set_value',
                args: {
                    doctype: 'VCM Gate-In',
                    name: frm.doc.custom_gate_in_reference, // The linked Gate In document
                    fieldname: 'status',
                    value: 'Received'
                }
            });
        }
    },
    custom_gate_in_reference: function(frm) {
        if (!frm.doc.custom_gate_in_reference) return;

        // Fetch all items from the selected Purchase Order
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "VCM Gate-In",
                name: frm.doc.custom_gate_in_reference
            },
            callback: function(r) {
                if (r.message) {
                    let gatein_data = r.message;
                    // Fetch and set the Purchase Person 
                    //Gate in still has Purchase_person while oters are customized
                    if (gatein_data.purchase_person) {
                        frm.set_value("custom_purchase_person", gatein_data.purchase_person);
                        frm.set_df_property('custom_purchase_person', 'read_only', 1);  // Make read-only
                    } else {
                        frm.set_value("custom_purchase_person", "Not Available");
                    }                    
                }
            }
        });
    },
    supplier: function(frm) {
        frm.set_value('custom_gate_in_reference', null);  // Clear old selection
        frm.refresh_field('custom_gate_in_reference');    // Ensure it reloads with the new filter
    },

    refresh(frm) {
        //Show only Gate-In whose status is Pending
        frm.fields_dict['custom_gate_in_reference'].get_query = function(doc) {
            return {
                filters: {
                    status: 'Pending',  // Only show Gate In records where status is 'Pending'
                    supplier: frm.doc.supplier,  // Show only records for the selected supplier
                    docstatus: ["!=", 2]  // Exclude Cancelled Gate In records
                }
            };
        };
        frm.add_custom_button(__("Print Small VCM Labels directly"), function(){
            frappe.ui.form.qz_connect()
            .then(function () {
                var config = qz.configs.create("Godex G500");            // Exact printer name from OS
                var print_data =[];
                var shift =200;

                var stock_qty ={}
                for(var index in frm.doc.items){
                    stock_qty[frm.doc.items[index]['item_code']] = frm.doc.items[index]['qty'];
                }
                //console.log(frm.doc.items);
                //frm.doc.items.forEach(a => console.log(a['do_not_print_in_barcodes']));

                let d = new frappe.ui.Dialog({
                                title: 'Select Price List',
                                fields: [
                                    {
                                        label: 'Price List',
                                        fieldname: 'price_list',
                                        fieldtype: 'Link',
                                        options:'Price List'
                                    }
                                ],
                                primary_action_label: 'Print',
                                primary_action(values) {
                                    frappe.call({
                                        method: 'vcm.erpnext_vcm.godex_print.filter_sellable_items',
                                        args: {
                                            //items: frm.doc.items.filter(a => a['do_not_print_in_barcodes']==false).map(a => a['item_code']),
                                            items: frm.doc.items
                                                //.filter(a => a['do_not_print_in_barcodes'] == false)
                                                .map(a => a['item_code']),
                                            company:frm.doc.company,
                                            price_list:values.price_list
                                        },
                                        freeze: true,
                                        callback: (r) => {
                                            //console.log(r.message);
                                            //console.log(stock_qty)
                                            var items_detailed = r.message;
                                            var total_items =[];
                                            for(var index in items_detailed){
                                                var qty = stock_qty[items_detailed[index]['code']];
                                                if(items_detailed[index]['name']!=null){
                                                    for(var i=0;i<qty;i++){
                                                        total_items.push({
                                                            "name" : items_detailed[index]['name'],
                                                            "code" : items_detailed[index]['code'],
                                                            "rate" : items_detailed[index]['rate'],
                                                        });
                                                    }
                                                }
                                            }
                                            //console.log(total_items);
                                            for(var j=0; j<total_items.length; j=j+4){
                                                var group_string="";
                                                    for(var g=0; g< 4; g++){
                                                        if(j + g < total_items.length){
                                                            group_string +=
                                                                `\nBA3,`+ (6 + (g * shift)) + `,10,1,1,40,0,0,` + total_items[j + g]["code"] +  
                                                                `\nAA,` + (6 + (g * shift)) + `,55,1,1,0,0E,` + total_items[j + g]["code"] +
                                                                `\nAB,` + (6 + (g * shift)) + `,75,1,1,0,0E,Rs.` + total_items[j + g]["rate"];
                                                        }
                                                    }
                                                    print_data.push(frm.events.get_EZPL_string_small(frm,group_string));
                                                }
                                            return qz.print(config, print_data)
                                        },
                                        error: (r) => {
                                            // on error
                                        }
                                    })
                                    d.hide();
                                }
                            });
                
                d.show();

            })
            .then(frappe.ui.form.qz_success)
            .catch(err => {
                frappe.ui.form.qz_fail(err);
                frappe.throw("Print error on qz error.");
            });
            //perform desired action such as routing to new form or fetching etc.
        }, __("Utilities"));
        
        frm.add_custom_button(__("Print Large VCM Labels directly"), function(){
            frappe.ui.form.qz_connect()
            .then(function () {
                var config = qz.configs.create("Godex G500");            // Exact printer name from OS
                var print_data =[];
                var shift =310;

                var stock_qty ={}
                for(var index in frm.doc.items){
                    stock_qty[frm.doc.items[index]['item_code']] = frm.doc.items[index]['qty'];
                }
                //console.log(frm.doc.items);
                //frm.doc.items.forEach(a => console.log(a['do_not_print_in_barcodes']));

                let d = new frappe.ui.Dialog({
                                title: 'Select Price List',
                                fields: [
                                    {
                                        label: 'Price List',
                                        fieldname: 'price_list',
                                        fieldtype: 'Link',
                                        options:'Price List'
                                    }
                                ],
                                primary_action_label: 'Print',
                                primary_action(values) {
                                    frappe.call({
                                        method: 'vcm.erpnext_vcm.godex_print.filter_sellable_items',
                                        args: {
                                            //items: frm.doc.items.filter(a => a['do_not_print_in_barcodes']==false).map(a => a['item_code']),
                                            items: frm.doc.items
                                                //.filter(a => a['do_not_print_in_barcodes'] == false)
                                                .map(a => a['item_code']),
                                            company:frm.doc.company,
                                            price_list:values.price_list
                                        },
                                        freeze: true,
                                        callback: (r) => {
                                            //console.log(r.message);
                                            //console.log(stock_qty)
                                            var items_detailed = r.message;
                                            var total_items =[];
                                            for(var index in items_detailed){
                                                var qty = stock_qty[items_detailed[index]['code']];
                                                if(items_detailed[index]['name']!=null){
                                                    for(var i=0;i<qty;i++){
                                                        total_items.push({
                                                            "name" : items_detailed[index]['name'],
                                                            "code" : items_detailed[index]['code'],
                                                            "rate" : items_detailed[index]['rate'],
                                                        });
                                                    }
                                                }
                                            }
                                            //console.log(total_items);
                                            for(var j=0;j<total_items.length;j=j+2){
                                                var group_string="";
                                                    for(var g=0;g<2;g++){
                                                        if((j+g)<total_items.length){
                                                            group_string += `\nBA3,`+(4+g*shift)+`,8,1,2,63,0,0,`+total_items[j+g]['code']+
                                                                                    `\nAB,`+(4+g*shift)+`,70,1,1,0,0E,`+total_items[j+g]['code']+
                                                                                    `\nAA,`+(4+g*shift)+`,104,1,1,0,0E,`+total_items[j+g]['name']+
                                                                                    `\nAC,`+(4+g*shift)+`,131,1,1,0,0E,Rs.`+total_items[j+g]['rate']
                                                        }
                                                    }
                                                    print_data.push(frm.events.get_EZPL_string(frm,group_string));
                                                }
                                            return qz.print(config, print_data)
                                        },
                                        error: (r) => {
                                            // on error
                                        }
                                    })
                                    d.hide();
                                }
                            });
                
                d.show();

            })
            .then(frappe.ui.form.qz_success)
            .catch(err => {
                frappe.ui.form.qz_fail(err);
                frappe.throw("Print error on qz error.");
            });
            //perform desired action such as routing to new form or fetching etc.
        }, __("Utilities"));

        
    },
    

    get_EZPL_string:function(frm,data){
        // Please refer to documentation for seetings : https://www.godexprinters.co.uk/downloads/manuals/desktop/EZPL_EN_J_20180226.pdf
        var settings = `
                        ^Q23,3
                        ^W76
                        ^H10
                        ^P1
                        ^S2
                        ^AD
                        ^C1
                        ^R8
                        ~Q+8
                        ^O0
                        ^D0
                        ^E18
                        ~R255
                        ^L
                        `
        var end = `\nE`
        var str =settings+data+ end
        var arr_data =  str.split("\n");
        var final_data = "";
        for(var index in arr_data){
            final_data +=  arr_data[index].trim() + "\x0D";}
        return final_data;
    },

    get_EZPL_string_small: function (frm, data) {
        // Please refer to documentation for seetings : https://www.godexprinters.co.uk/downloads/manuals/desktop/EZPL_EN_J_20180226.pdf
        var settings = `
                            ^Q15,3 
                            ^W100    
                            ^H10   
                            ^P1   
                            ^S2    
                            ^AD  
                            ^C1   
                            ^R8
                            ~Q+0   
                            ^O0   
                            ^D0    
                            ^E18     
                            ~R255   
                            ^L      
                            `;
        var end = `\nE`;
        var str = settings + data + end;
        // Split into lines and append carriage return at the end of each line
        var arr_data = str.split("\n");
        var final_data = "";
        for (var index in arr_data) {
          final_data += arr_data[index].trim() + "\x0D";
        }
        return final_data;
    }
})
