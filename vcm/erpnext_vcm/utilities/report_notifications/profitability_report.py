import frappe
from frappe.utils import nowdate

def send_profitability_report():
    report_name = "Profitability Analysis"

    filters = {
        "company": "TOUCHSTONE FOUNDATION VRINDAVAN - NCR",
        "based_on": "Cost Center",
        "fiscal_year": "2024-2025",
        "from_date": "2024-04-01",
        "to_date": "2025-03-31"
    }

    try:
        # Fetch report document
        report = frappe.get_doc("Report", report_name)
        columns, data = report.get_data(filters=filters, as_dict=True)

        # Generate HTML Table
        email_body = "<h2>Profitability Analysis Report</h2>"
        email_body += "<table border='1' cellspacing='0' cellpadding='5' style='border-collapse: collapse;'>"
        email_body += "<tr style='background-color: #f2f2f2; font-weight: bold;'>"
        email_body += "".join(f"<th style='padding: 8px; border: 1px solid #ddd;'>{col.get('label')}</th>" for col in columns)
        email_body += "</tr>"

        for row in data:
            email_body += "<tr>"
            email_body += "".join(f"<td style='padding: 8px; border: 1px solid #ddd;'>{row.get(col.get('fieldname'), '')}</td>" for col in columns)
            email_body += "</tr>"

        email_body += "</table>"

        # Send Email with Embedded HTML Report
        recipients = ["pankaj.sharma@vcm.org.in"]  
        frappe.sendmail(
            recipients=recipients,
            subject=f"{report_name} - {nowdate()}",
            message=email_body
        )

        frappe.msgprint("Profitability Report sent successfully!")

    except Exception as e:
        frappe.log_error(f"Error in sending profitability report: {str(e)}", "Profitability Report Error")
        frappe.throw("Failed to send Profitability Analysis Report. Please check error logs.")
