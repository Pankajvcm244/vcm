# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class ItemCodePrinter(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company: DF.Link | None
		date: DF.Date | None
		day_after_expiry: DF.Int
		item_code: DF.Data | None
		manufacturing_date: DF.Date | None
		price_list: DF.Link | None
		quantity: DF.Int
		quantity_date: DF.Int
		quantity_exp: DF.Int
	# end: auto-generated types
	def validate (self):
		if (self.manufacturing_date) and  not self.day_after_expiry or not self.quantity_exp :
			return frappe.throw("Please enter day after it expired and quantity")
		if (self.day_after_expiry) and  not self.manufacturing_date or not self.quantity_exp :
			return frappe.throw("Please enter manufacturing date and quantity")
		if (self.quantity_exp) and  not self.manufacturing_date or not self.day_after_expiry :
			return frappe.throw("Please enter manufacturing date and day after it expired")

		