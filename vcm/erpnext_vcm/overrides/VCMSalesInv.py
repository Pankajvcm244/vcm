import frappe, erpnext
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils.data import getdate
from frappe.model.naming import getseries
from datetime import timedelta, date
import datetime 

class VCMSalesInv(SalesInvoice):
    def validate(self):
        super().validate()
        self.validate_if_zero_rate_item()
        self.validate_back_dated_entry()

    

    def autoname(self):
        # select a project name based on customer
        #dateF = getdate(self.posting_date)
        #company_abbr = frappe.get_cached_value("Company", self.company, "abbr")
        #year = dateF.strftime("%y")
        #month = dateF.strftime("%m")
        #prefix = f"{company_abbr}-{year}{month}-"
        #self.name = prefix + getseries(prefix, 4)
        
        #############################################################################
        # changes done by Pankaj for different series for sales invoice based upon POS Profile
        #############################################################################
        # Get the current date and time
        postingdate = getdate(self.posting_date)
        # Get the current month in 2-digit format
        #month = postingdate.strftime("%m")
        # Get the current year in 2-digit format
        #year = postingdate.strftime("%y")
        postingyear = postingdate.year
        postingmonth = postingdate.month    

        # Determine fiscal year
        if postingmonth < 4:  # If before April, it's part of the previous fiscal year
            fiscal_year = f"{(postingyear-1)% 100}{postingyear % 100}"
        else:
            fiscal_year = f"{postingyear % 100}{(postingyear + 1) % 100}"

        if self.pos_profile:
            # these are Sales invoice series for POS Profile closing
            # numbering series for Krishna Prasadam
            if (self.pos_profile == 'Krishna Prasadam Counter'):    
                # select a document series name based on customer 
                #handle WALK_IN or remaining customer like Akshaya patra here
                if self.is_return:
                    prefix = f"KPI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"KPI{fiscal_year}-"
                    self.name = prefix + getseries(prefix, 6)              
            elif (self.pos_profile == 'Krishnamrita'): 
                # select a document series name based on customer             
                if self.customer  == 'FOC':
                    prefix = f"KAI{fiscal_year}F-"
                    self.name = prefix + getseries(prefix, 5)            
                else:
                    if self.is_return:
                        prefix = f"KAI{fiscal_year}R-"
                        self.name = prefix + getseries(prefix, 5) 
                    else:   
                        prefix = f"KAI{fiscal_year}-"      
                        self.name = prefix + getseries(prefix, 6) 
            elif (self.pos_profile == 'Pushpanjali POS'):
                prefix = f"DRPS{fiscal_year}-"       
                self.name = prefix + getseries(prefix, 5)  
            elif (self.pos_profile == 'Surabhi POS'): 
                if self.is_return:
                    prefix = f"SPI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"SPI{fiscal_year}-"  
                    self.name = prefix + getseries(prefix, 6)
            elif (self.pos_profile == 'Brajras POS'):
                prefix = f"BRI{fiscal_year}-"   
                self.name = prefix + getseries(prefix, 6)
            elif (self.pos_profile == 'Annakoot POS'):
                prefix = f"AKI{fiscal_year}-"   
                self.name = prefix + getseries(prefix, 6)
            elif (self.pos_profile == 'Amritsar POS'):
                if self.is_return:
                    prefix = f"API{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"API{fiscal_year}-"  
                    self.name = prefix + getseries(prefix, 6) 
            elif (self.pos_profile == 'Noida POS'):
                if self.is_return:
                    prefix = f"NPI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"NPI{fiscal_year}-"  
                    self.name = prefix + getseries(prefix, 6)
            elif (self.pos_profile == 'Gurugram POS'):
                if self.is_return:
                    prefix = f"GPI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"GPI{fiscal_year}-"  
                    self.name = prefix + getseries(prefix, 6)
            elif (self.pos_profile == 'Krishna Counter POS'):
                if self.is_return:
                    prefix = f"KCI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"KCI{fiscal_year}-"   
                    self.name = prefix + getseries(prefix, 6)   
            elif (self.pos_profile == 'Gita Counter POS'): 
                if self.is_return:
                    prefix = f"GCI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"GCI{fiscal_year}-"   
                    self.name = prefix + getseries(prefix, 6)
            elif (self.pos_profile == 'Balram Counter POS'): 
                if self.is_return:
                    prefix = f"BCI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"BCI{fiscal_year}-"   
                    self.name = prefix + getseries(prefix, 6)
            elif (self.pos_profile == 'Jagannath Counter POS'): 
                if self.is_return:
                    prefix = f"JCI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"JCI{fiscal_year}-"   
                    self.name = prefix + getseries(prefix, 6)
            elif (self.pos_profile == 'Kumbh Mela_Merchandise POS'): 
                if self.is_return:
                    prefix = f"KMI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"KMI{fiscal_year}-"   
                    self.name = prefix + getseries(prefix, 6)
            elif (self.pos_profile == 'Rajbhog POS'): 
                if self.is_return:
                    prefix = f"DRI{fiscal_year}R-"
                    self.name = prefix + getseries(prefix, 5)
                else:
                    prefix = f"DRI{fiscal_year}-"   
                    self.name = prefix + getseries(prefix, 6)
        # 
        # these are Sales invoice series for direct creation of Sales Invoice
        # 
        #             
        elif (self.cost_center == 'Braj Nidhi Guest House - TSF') :
            #guest house sales invoice series
            if self.is_return:
                prefix = f"GHI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"GHI{fiscal_year}-"  
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Annakoot - TSF'):
            if self.is_return:
                prefix = f"AKI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"AKI{fiscal_year}-"  
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Brajras - TSF') :
            if self.is_return:
                prefix = f"BRI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"BRI{fiscal_year}-"  
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Surabhi - TSF'):
            if self.is_return:
                prefix = f"SPI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5) 
            else:
                prefix = f"SPI{fiscal_year}-"   
                self.name = prefix + getseries(prefix, 6)            
        elif (self.cost_center == 'Varanasi Laddu Feeding - TSF'):
            if self.is_return:
                prefix = f"LFI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"LFI{fiscal_year}-"  
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Noida Merchandise - TSF'):
            if self.is_return:
                prefix = f"NPI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"NPI{fiscal_year}-"   
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Amritsar Merchandise - TSF'):
            if self.is_return:
                prefix = f"API{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"API{fiscal_year}-"   
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Books - TSF'):
            if self.is_return:
                prefix = f"GCI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"GCI{fiscal_year}-"   
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Gifts - TSF'):
            if self.is_return:
                prefix = f"KCI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"KCI{fiscal_year}-"   
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'GGN Merchandise - TSF'):
            if self.is_return:
                prefix = f"GPI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"GPI{fiscal_year}-"   
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Kumbh Mela - TSF'):
            if self.is_return:
                prefix = f"KMI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"KMI{fiscal_year}-"  
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Krishnamrita Catering - TSF'):
            if self.is_return:
                prefix = f"KAI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"KAI{fiscal_year}-"  
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'KRISHNA PRASADAM COUNTER - HKMV'):
            if self.is_return:
                prefix = f"KPI{fiscal_year}R-"
                self.name = prefix + getseries(prefix, 5)
            else:
                prefix = f"KPI{fiscal_year}-"
                self.name = prefix + getseries(prefix, 6)
        elif (self.cost_center == 'Pushpanjali - VCMT'):
            prefix = f"DRPS{fiscal_year}-"
            self.name = prefix + getseries(prefix, 5)

        else:
            # rest sales invoice will follow this series
            prefix = f"SI-{fiscal_year}-" 
            self.name = prefix + getseries(prefix, 6)
            ######################till here changed by Pankaj #################################################

    def validate_if_zero_rate_item(self):
        for item in self.get("items"):
            if item.item_code:
                valuation_rate = frappe.get_value(
                    "Item", item.item_code, "valuation_rate"
                )
                if item.rate == 0:
                    frappe.throw(
                        "Sale Rate of <b>Item: {}</b> can't be ZERO".format(
                            item.item_name
                        )
                    )
                if item.rate < valuation_rate:
                    frappe.throw(
                        "Sale Rate({0}) of <b>Item: {1}</b> can't be less than it's Valuation Rate ({2})".format(
                            item.rate, item.item_name, valuation_rate
                        )
                    )
        return

    def validate_back_dated_entry(self):
        posting_date = getdate(self.posting_date)
        if is_last_day_of_month(getdate(posting_date)):
            return

        if not self.amended_from:
            latest_sales_invoice = frappe.get_all(
                "Sales Invoice",
                fields=["MAX(posting_date) as date"],
                filters=[["docstatus", "=", "1"], ["company", "=", self.company]],
            )
            latest_date = latest_sales_invoice[0]["date"]
            if latest_date is not None and posting_date < latest_date:
                frappe.throw(
                    f"Posting Date can't be earlier to the latest Sales Invoice i.e. on {latest_date}. If you still wish to make this entry, it can be done only on the last date of the month. Contact Accounts for help."
                )
        else:
            if self.posting_date != str(
                frappe.get_value("Sales Invoice", self.amended_from, "posting_date")
            ):
                frappe.throw(
                    "You can't have different date than original Sales Invoice."
                )
        return


def is_last_day_of_month(date_obj: date):
    # Get the next day's date
    next_day = date_obj + timedelta(days=1)

    # Check if the next day is in the next month
    return date_obj.month != next_day.month


@frappe.whitelist()
def directly_mark_cancelled(name):
    roles = frappe.get_roles(frappe.session.user)
    if "Accounts User" not in roles:
        frappe.throw(
            "Only Accounts Person is allowed to mark a Draft Sales Invoice directly to Cancelled."
        )
    document = frappe.get_doc("Sales Invoice", name)

    if document.docstatus != 0:
        frappe.throw("Only Draft document is allowed to be set as cancelled.")
    frappe.db.set_value("Sales Invoice", name, "docstatus", 2)
    frappe.db.commit()

@frappe.whitelist()
def before_insert(doc, method):
        doc.place_of_supply = frappe.get_value("Company", doc.company, "state")  # Default to company state