from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils.data import getdate
from frappe.model.naming import getseries
import datetime
from frappe import _
from frappe.utils import flt

from erpnext.accounts.doctype.pos_invoice.pos_invoice import (
    POSInvoice,
    get_stock_availability,
)

class VCMPOSInv(POSInvoice):
    def __init__(self, *args, **kwargs):
        super(VCMPOSInv, self).__init__(*args, **kwargs)
       

    def validate(self):
        super().validate()
        self.validate_if_zero_rate_item()
        self.validate_full_amount()
        self.cummulative_stock_availbility()
        return
        # FOR RTGP
        # self.validate_discount()
        # if self.coupon_code:
        # 	from erpnext.accounts.doctype.pricing_rule.utils import validate_coupon_code
        # 	validate_coupon_code(self.coupon_code)

    #############################################################################
        # changes done by Pankaj for different series for sales invoice based upon POS Profile
    #############################################################################
    # this code is to generate seperate Invoice series for FOC/Paid cutomers
    def autoname(self):
        
        # Get the current date and time
        now = datetime.datetime.now()
        # Get the current month in 2-digit format
        month = now.strftime("%m")
        # Get the current year in 2-digit format
        year = now.strftime("%y")

        #numbering series for Krishna Prasadam
        if (self.pos_profile == 'Krishna Prasadam'):    
            # select a document series name based on customer             
            if self.customer  == 'FOC':
                prefix = f"HKPFOC-{year}{month}-"
                self.name = prefix + getseries(prefix, 4)            
            elif  self.customer  == 'WALK_IN':          
                prefix = f"HKPPOS-{year}{month}-"         
                self.name = prefix + getseries(prefix, 4)            
            else:
                frappe.throw(f"Unknown customer:{self.customer} Error POSINV003 . Please select FOC or WALK_IN as customer before completing the order.")
        elif (self.pos_profile == 'Krishnamrita'): 
            # select a document series name based on customer             
            if self.customer  == 'FOC':
                prefix = f"HKAFOC-{year}{month}-"
                self.name = prefix + getseries(prefix, 4)            
            elif  self.customer  == 'WALK_IN' :          
                prefix = f"HKAPOS-{year}{month}-"         
                self.name = prefix + getseries(prefix, 4)            
            else:
                frappe.throw(f"Unknown customer:{self.customer} Error POSINV004 . Please select correct customer before completing the order.")
        elif (self.pos_profile == 'Pushpanjali'):  
            prefix = f"VPS-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5)           
        elif (self.pos_profile == 'Surabhi POS'):  
            prefix = f"TSP-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5)
        elif (self.pos_profile == 'Brajras POS'):  
            prefix = f"TBR-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5) 
        elif (self.pos_profile == 'Annakoot POS'):  
            prefix = f"TAK-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5) 
        elif (self.pos_profile == 'Amritsar POS'):  
            prefix = f"TAP-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5) 
        elif (self.pos_profile == 'NOIDA POS'):  
            prefix = f"TNP-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5) 
        elif (self.pos_profile == 'Gurugram POS'):  
            prefix = f"TGP-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5) 
        elif (self.pos_profile == 'Krishna Counter POS'):  
            prefix = f"TKC-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5) 
        elif (self.pos_profile == 'Gita Counter POS'):  
            prefix = f"TGC-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5)
        elif (self.pos_profile == 'Jagannath Counter POS'):  
            prefix = f"TJC-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5) 
        elif (self.pos_profile == 'Balram Counter POS'):  
            prefix = f"TBC-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5) 
        else:
            prefix = f"POS-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5)             
        #############################  Till here by Pankaj ############################

    def validate_full_amount(self):
        if self.paid_amount != self.rounded_total:
            frappe.throw("Please check the Paid Amount. It can't be less or more.")
        return

    def validate_if_zero_rate_item(self):
        for item in self.get("items"):
            valuation_rate = frappe.get_value("Item", item.item_code, "valuation_rate")
            if item.rate == 0:
                frappe.throw(
                    "Sale Rate of <b>Item: {}</b> can't be ZERO".format(item.item_name)
                )
            if item.rate < valuation_rate:
                frappe.throw(
                    "Sale Rate({0}) of <b>Item: {1}</b> can't be less than it's Valuation Rate ({2})".format(
                        item.rate, item.item_name, valuation_rate
                    )
                )
        return

    @frappe.whitelist()
    def get_gst_breakup(self):
        rows = []
        total_tax = 0
        for item in self.items:
            qty = item.qty
            rate = item.rate
            # item_record = frappe.get_doc('Item', item.item_code)
            GSTp = 0
            tax_templates = frappe.db.sql(
                """
											select item.gst_hsn_code, tax_template.name as template, tax_template.cumulative_tax as rate
											from `tabItem` item
											join `tabItem Tax` item_tax
												on item_tax.parent = item.name
											join `tabItem Tax Template` tax_template
												on tax_template.name = item_tax.item_tax_template
											where tax_template.company = '{}' and item.name = '{}'
											""".format(
                    self.company, item.item_code
                ),
                as_dict=1,
            )
            if len(tax_templates) > 0:
                tax_template = tax_templates[0]
                GSTp = tax_template["rate"]
                row_index = self.search_rows(rows, tax_template["gst_hsn_code"], GSTp)
                if row_index is None:
                    temp_data = {
                        "HSN": tax_template["gst_hsn_code"],
                        "GSTp": GSTp,
                        "Taxable": qty * rate,
                        "CGSTI": qty * rate * GSTp / 200,
                        "SGSTI": qty * rate * GSTp / 200,
                    }
                    rows.append(temp_data)
                else:
                    rows[row_index]["Taxable"] += qty * rate
                    rows[row_index]["CGSTI"] = (
                        rows[row_index]["CGSTI"] + qty * rate * GSTp / 200
                    )
                    rows[row_index]["SGSTI"] = (
                        rows[row_index]["SGSTI"] + qty * rate * GSTp / 200
                    )
        for row in rows:
            row["Taxable"] = round(row["Taxable"], 2)
            row["CGSTI"] = round(row["CGSTI"], 2)
            row["SGSTI"] = round(row["SGSTI"], 2)
            total_tax += row["CGSTI"] + row["SGSTI"]
        total_tax = round(total_tax, 2)
        cashier = frappe.db.get_value("User", self.owner, "full_name")
        return rows, total_tax, cashier

    @frappe.whitelist()
    def get_company_address(self):
        adds = frappe.db.sql(
            """
						select address.*
						from `tabAddress` address
						join `tabDynamic Link` link on link.parent = address.name
						where link.link_name = '{}' and link.link_doctype = 'Company'
						""".format(
                self.company
            ),
            as_dict=1,
        )
        address = adds[0]

        formatted_address = (
            "%(address_line1)s, %(address_line2)s, %(city)s, %(state)s - %(pincode)s"
            % address
        )

        return formatted_address

    @frappe.whitelist()
    def get_items_segregated(self):
        item_group_data = {}

        for item in self.items:
            # item_record = frappe.get_doc('Item', item.item_code)
            grp = item.item_group
            qty = item.qty
            if grp not in item_group_data:
                item_group_data.setdefault(
                    grp,
                    {
                        item.item_code: frappe._dict(
                            {"name": item.item_name, "qty": qty}
                        )
                    },
                )
            else:
                grp_data = item_group_data[grp]
                if item.item_code not in grp_data:
                    grp_data.setdefault(
                        item.item_code, {"name": item.item_name, "qty": qty}
                    )
                else:
                    grp_data[item.item_code]["qty"] = (
                        grp_data[item.item_code]["qty"] + qty
                    )
                item_group_data.setdefault(grp, grp_data)

        # For Restaurant : Get the count of this bill

        token = (
            frappe.db.sql(
                f"""
						SELECT count(name) as token
						FROM `tabPOS Invoice`
						WHERE pos_profile = '{self.pos_profile}'
						AND posting_date = '{self.posting_date}'
						AND posting_time < '{self.posting_time}'
						"""
            )[0][0]
            + 1
        )

        return item_group_data, token

    def search_rows(self, rows, HSN, GSTp):
        for idx, r in enumerate(rows):
            if r["HSN"] == HSN and r["GSTp"] == GSTp:
                return idx
        return None

    def cummulative_stock_availbility(self):
        # items = [item.item_code for item in self.get("items")]
        # unique_items = list(set(items))
        warehouse = self.set_warehouse
        unique_items_qty = {}
        for d in self.get("items"):
            if d.item_code in unique_items_qty:
                unique_items_qty[d.item_code] = unique_items_qty[d.item_code] + d.qty
            else:
                unique_items_qty[d.item_code] = d.qty

        for item in unique_items_qty:
            available_stock, is_stock_item = get_stock_availability(item, warehouse)
            if is_stock_item and flt(available_stock) < flt(unique_items_qty[item]):
                frappe.throw(
                    _(
                        "Stock quantity not enough for Item Code: {} under warehouse {}. Available quantity {}."
                    ).format(item, warehouse, available_stock, unique_items_qty[item]),
                    title=_("Item Unavailable"),
                )
        return

    def validate_discount(self):
        amount_threshold = 3000
        pos_profiles = [
            "POS - Donwcounter",
            "POS - RKM Book Counter",
            "POS - Temple Counter",
        ]
        if (not self.is_return) and self.pos_profile in pos_profiles:
            if (
                self.grand_total < amount_threshold
                and self.additional_discount_percentage != 0
            ):
                frappe.throw(
                    "Discount is not allowed for amount < {}".fomrat(amount_threshold)
                )
            if (
                self.grand_total >= amount_threshold
                and self.additional_discount_percentage != 5
            ):
                frappe.throw(
                    "Discount is not applied on amount >= {} or applied more".format(
                        amount_threshold
                    )
                )
        return



    ###########################################################
    #   Changes doen by Pankaj for second screen submit
    ############################################################
               
    def on_submit(self):
        super().on_submit()
        #print("Outstanding amoint is ", {self.outstanding_amount});
        #if customer is blank show error and stop
        if self.customer == "":
            frappe.throw("The Customer name is empty. Please start transaction from scratch again.")
        
        #if balance is not zero , it will lead to partial payment 
        if self.outstanding_amount != 0 :
            frappe.throw("To Be Paid should be zero.")

        
        # Checks for different POS counters
        if (self.pos_profile == "Krishna Prasadam"):  
            # check for WALK_IN customer, FOC as payment mode is not selected
            if self.customer == 'WALK_IN_KP':
                for payment in self.payments:
                    if payment.mode_of_payment == 'FOC':
                        if payment.amount != 0:
                            frappe.throw("FOC can not be payment method for WALK_IN_KP customer.")
            # check for FOC customer, Cash or UPI mode is not selected
            if self.customer == 'FOC':
                for payment in self.payments:
                    if (payment.mode_of_payment == 'Cash') or (payment.mode_of_payment == 'UPI'):
                        if payment.amount != 0:
                            frappe.throw("FOC FOC customer, Please select FOC as mode of payment.")
            if self.customer == 'FOC':
                if not self.custom_devotee_details:
                    frappe.throw("Please fill Devotee field before completing the order.")
                if not self.custom_additional_remarks:
                    frappe.throw("Please fill additional remarks for FOC before completing the order.")
                # check in FOC other payment mode is not selected
                for payment in self.payments:
                    if payment.mode_of_payment == 'FOC':
                        if payment.amount == 0:
                            frappe.throw("Please select FOC as mode of payment for FOC customer.")
            #everything is fine send email       
            self.send_email()

        # for Books and Para
        if ((self.pos_profile == 'Jagannath Counter POS' ) or (self.pos_profile == 'Krishna Counter POS') 
			or (self.pos_profile == 'Gita Counter POS') or (self.pos_profile == 'Gurugram POS')
			or (self.pos_profile == 'NOIDA POS') or (self.pos_profile == 'Amritsar POS')
            or (self.pos_profile == 'Balram Counter POS')  ): 
            
            if not self.custom_bnp_salesrep :
                frappe.throw("Please fill Sales Rep name before completing the order.")

            # make sure that in case of Pushpanjali 100Rs coupon as MOP, remarks with Coupon code is filled
            for payment in self.payments:
                    if payment.mode_of_payment == 'Pushpanjali Coupon':
                        if payment.amount != 0:
                           if not self.custom_additional_remarks:
                                frappe.throw("Please fill Pushpanjali coupon number in additional remarks before completing the order.")
                    
    def send_email(self):
        # check if doc is ready to submit and not in draft (state 0)
        if self.docstatus == 1:   
            recipient_doc = self.custom_devotee_email
            recipient_email = frappe.db.get_value("Devotee Details",recipient_doc,"email_id")
            subject = f'{self.pos_profile} counter: FOC for Rs. {self.grand_total} issued in your name'
            
            # Customize the message with POS invoice number and total billed amount
            if (self.pos_profile == 'Krishna Prasadam'): 
                message = (
                    f'Hare Krishna {self.custom_devotee_details},<br><br>'
                    f'FOC for Rs. {self.grand_total} issued in your name at {self.pos_profile}.<br>'
                    f'Remarks: {self.custom_additional_remarks}<br><br><br>'
                    f'If you have any issues, please contact {self.pos_profile} person.<br>'
                    f'Devdutt 7500003865 or Bhura 9720639844.<br>'
                    f'POS Invoice Number: {self.name}<br>'
                    f'Total Billed Amount: {self.grand_total}<br>'
                    f'Date of Posting: {self.posting_date}<br><br>'
                    f'Regards, <br> Systems and Process ERP Team<br>'
                )
            else:
                frappe.throw(f"Unknown POS Profile:{self.pos_profile} Error POSINV002 for sending email. Please contact ERP Team.")

            # Send email using frappe.sendmail
            frappe.sendmail(
                recipients=[recipient_email],
                subject=subject,
                message=message
            )




