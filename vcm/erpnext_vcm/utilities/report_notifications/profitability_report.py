import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import nowdate


from frappe.utils import today, get_first_day, get_last_day
from frappe.desk.query_report import run
from datetime import datetime

def send_profitability_report():
   
    report_name = "Profitability Analysis"

    
    filters = {
        "company": "TOUCHSTONE FOUNDATION VRINDAVAN - NCR",
        "based_on": "Cost Center",
        "fiscal_year": "2024-2025",
        "from_date": "2024-04-01",
        "to_date": "2025-03-31"
    }

    report = frappe.get_doc("Report", report_name)
    columns, data = report.get_data(filters=filters, as_dict=True)

    table_html = "<h2>Profitability Analysis Report</h2>"
    table_html += "<table border='1' cellspacing='0' cellpadding='5'>"
    table_html += "<tr>" + "".join(f"<th>{col.get('label')}</th>" for col in columns) + "</tr>"

    for row in data:
        table_html += "<tr>" + "".join(f"<td>{row.get(col.get('fieldname'), '')}</td>" for col in columns) + "</tr>"

    table_html += "</table>"

    pdf_file = get_pdf(table_html)

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": f"{report_name}.pdf",
        "content": pdf_file,
        "is_private": 0
    })
    file_doc.save()

    recipients = ["pankaj.sharma@vcm.org.in"]  
    
    frappe.sendmail(
        recipients=recipients,
        subject=f"{report_name} - {nowdate()}",
        message="Please find the attached Profitability Analysis report.",
        attachments=[{"file_url": file_doc.file_url}]
    )

    frappe.db.commit()