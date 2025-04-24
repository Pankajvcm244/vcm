// Copyright (c) 2020, Tara Technologies
// For license information, please see license.txt



frappe.ui.form.on("Journal Entry", {
	refresh: function (frm) {
		frm.add_custom_button(__("Unlink VCM Bank Transaction"), function () {

			frappe.warn('Are you sure you want to proceed?',
				'This will unallocate this entry from its connected Bank Trasaction Entry.',
				() => {
					frappe.call({
						method: 'vcm.erpnext_vcm.overrides.VCMJournalEntry.unallocate_bank_transaction',
						args: { "je": frm.doc.name }
					});
				},
				'Continue',
				true // Sets dialog as minimizable
			)
		}, __("Actions"));
	},
	onload: function (frm) {
		frm.set_query("suspense_jv", "accounts", function (doc, cdt, cdn) {
			return {
				query: "hkm.erpnext___custom.extend.queries.uncleared_suspense_voucher_query",
				filters: {
					'company': frm.doc.company
				}
			}
		});

	},
	setup_queries: function () {
		frm.set_query("suspense_jv", "accounts", function (doc, cdt, cdn) {
			return {
				query: "hkm.erpnext___custom.extend.queries.uncleared_suspense_voucher_query",
				filters: {
					'company': frm.doc.company
				}
			}
		});
	},


});
$.extend(erpnext.journal_entry, {
	account_query: function (frm) {
		var filters = {
			company: frm.doc.company,
			is_group: 0
		};
		return { filters: filters };
	},
});
