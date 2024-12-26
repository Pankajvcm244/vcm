from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate
from frappe.model.naming import getseries
import datetime 
from erpnext.accounts.doctype.pos_invoice.pos_invoice import POSInvoice

class VCMPOSInvoice(POSInvoice):
    def validate(self):
        super().validate()   

    # this code is to send email to FOC devotee, if someone is using thier name for FOC issue           
    def on_submit(self):
        super().on_submit()

        #print("Outstanding amoint is ", {self.outstanding_amount});
        #if customer is blank show error and stop
        if self.customer == "":
            frappe.throw("The Customer name is empty. Please start transaction from scratch again.")
        
        #if balance is not zero , it will lead to partial payment 
        if self.outstanding_amount != 0 :
            frappe.throw("To Be Paid amount should be zero.")

        # for Krishna Prasadam
        if (self.pos_profile == "Krishna Prasadam"):  
            # check for WALK_IN_KP customer, FOC as payment mode is not selected
            if self.customer == 'WALK_IN_KP':
                for payment in self.payments:
                    if payment.mode_of_payment == 'FOC':
                        if payment.amount != 0:
                            frappe.throw("FOC can not be payment method for WALK_IN customer.")

            if self.customer == 'FOC':
                 # check for FOC customer, Cash or UPI mode is not selected
                for payment in self.payments:
                    if (payment.mode_of_payment == 'Cash') or (payment.mode_of_payment == 'UPI'):
                        if payment.amount != 0:
                            frappe.throw("FOC FOC customer, Please select FOC as mode of payment.")

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

        # for Books and Para Counters        
        elif((self.pos_profile == "Krishna Counter POS") or (self.pos_profile == "Gita Counter POS") 
                or (self.pos_profile == "Gurugram POS") or (self.pos_profile == "NOIDA POS") 
                or (self.pos_profile == "Balram Counter POS") or (self.pos_profile == "Jagannath Counter POS")):  
        
            if not self.custom_bnp_salesrep: 
                frappe.throw("Please fill Sales Rep field before completing the order.")
            if payment.mode_of_payment == 'Coupon':
                if not self.custom_additional_remarks:
                    frappe.throw("Please fill Coupon Code field in remarks before completing the order.")            
               
        # for Krishna Amrita        
        elif(self.pos_profile == "Krishnamrita"):  
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

        #Krishna Amrita has no FOC, everything is payabale, so no email required        
        else(self.pos_profile == "Pushpanjali")  
            if self.customer == 'FOC':
                frappe.throw("We can not have FOC in Pushpanjali. Please select WALK_IN as customer.")
        

        
    
    def send_email(self):
        # check if doc is ready to submit and not in draft (state 0)
        if self.docstatus == 1:   
            
            
            # Customize the message with POS invoice number and total billed amount
            if (self.pos_profile == 'Krishna Prasadam'):
                recipient_doc = self.custom_devotee_email
                recipient_email = frappe.db.get_value("Devotee Details",recipient_doc,"email_id")
                subject = f'{self.pos_profile} counter: FOC for Rs. {self.grand_total} issued in your name'
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
            elif (self.pos_profile == 'Krishnamrita'):
                recipient_doc = self.custom_devotee_email
                recipient_email = frappe.db.get_value("Devotee Details",recipient_doc,"email_id")
                subject = f'{self.pos_profile} counter: FOC for Rs. {self.grand_total} issued in your name'
                message = (
                    f'Hare Krishna {self.custom_devotee_details},<br><br>'
                    f'FOC for Rs. {self.grand_total} issued in your name at {self.pos_profile}.<br>'
                    f'Remarks: {self.custom_additional_remarks}<br><br>'
                    f'If you have any issues, please contact {self.pos_profile} person.<br>'
                    f'Shishupal 9719047755 .<br>'
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
        else:
            prefix = f"POS-{year}{month}-"         
            self.name = prefix + getseries(prefix, 5)             
        #############################  Till here by Pankaj ############################