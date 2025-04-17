import logging
logging.basicConfig(level=logging.DEBUG)

from frappe.utils.data import get_url
from vcm.erpnext_vcm.overrides.po_alm.poworkflow_action import (
    return_already_approved_page,
)
import frappe, requests, json, imgkit
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow
from frappe.utils import cstr
from frappe.utils.verified_command import get_signed_params, verify_request
from frappe.workflow.doctype.workflow_action.workflow_action import (
    get_doc_workflow_state,
    return_success_page,
)
from frappe.utils.password import get_decrypted_password

def send_whatsapp_approval(doc, user, mobile_no, allowed_options):
    #logging.debug(f"VCM send_whatsapp_approval 1 {user}, {mobile_no}")
    approval_link = get_approval_link(doc, user, allowed_options)
    rejection_link = get_rejection_link(doc, user)
    send_whatsapp(doc, mobile_no, approval_link, rejection_link)

def get_short_link_name(long_link):
    doc = frappe.get_doc(
        {"doctype": "HKM Redirect", "redirect_to": long_link, "ephemeral": 1}
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def send_whatsapp(
    doc: Document, mobile_no: str, approval_link: str, rejection_link: str
):
    approval_link_name = get_short_link_name(approval_link)
    rejection_link_name = get_short_link_name(rejection_link)
    #logging.debug(f"**** send_whatsapp 1 {doc}, {approval_link_name}, {rejection_link_name}")

    whatsupsettings = frappe.get_doc("VCM WhatsAPP Settings")
    # Fetch the booking document
    #booking = frappe.get_doc("booking", booking_id)
    
    doctype = "VCM WhatsAPP Settings"  # Example of a singleton DocType
    fieldname = "token" 
    decrypted_value = get_decrypted_password(doctype, doctype, fieldname)
    #logging.debug(f"whatsup {name},{mobile}, {hall_name}, {booking_status},  {booking_id}, {whatsupsettings.template}, {date}, {from_time}, {to_time} ")
    # settings = frappe.get_cached_doc("VCM WhatsAPP Settings")
    #po_approval_settings = frappe.get_cached_doc("HKM General Settings")
    

    site_name = cstr(frappe.local.site)
    po_name  = doc.name

    po_image_link = f"https://{site_name}/api/method/vcm.erpnext_vcm.utilities.whatsapp.powhatsapp.get_purchase_order_image?docname={doc.name}"

    headers = {
         "Content-Type": "application/json",
         "Authorization": f"Basic {decrypted_value}"
    }


    data =  {
        "countryCode": "+91",
        "fullPhoneNumber": f"+91{mobile_no}",
        "callbackData": "some text here",
        "type": "Template",
        "template": {
            "name": f"{whatsupsettings.po_template}",
            "languageCode": "en",
            "headerValues": [
                doc.name
            ],            
            "bodyValues": [
                doc.department,
                doc.name,
                doc.supplier_name,
                doc.workflow_state,
                doc.grand_total
            ]
        }        
    } 
    # response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    #logging.debug(f"whatsup {jsondate}, {jsonstarttime}, {jsonendtime}")   
    try:
        response = requests.post(whatsupsettings.url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        logging.debug(f"******************whatsup message sent {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        #logging.debug(f"whatsup message sent error  {response.json()}, {str(e)}")
        frappe.throw(f"Error sending WhatsApp message: {str(e)}")


def get_approval_link(doc, user, allowed_options):
    if "Recommend" in allowed_options:
        return get_confirm_workflow_action_url(doc, "Recommend", user)
    if "First Approve" in allowed_options:
        return get_confirm_workflow_action_url(doc, "First Approve", user)
    if "Final Approve" in allowed_options:
        return get_confirm_workflow_action_url(doc, "Final Approve", user)
    else:
        frappe.throw(
            "Next ALM User is not allowed to approve the Document. Please ask for permission."
        )


def get_rejection_link(doc, user):
    return get_confirm_workflow_action_url(doc, "Reject", user)


def get_confirm_workflow_action_url(doc, action, user):
    logging.debug(f"VCM  get_confirm_workflow_action_url 1 {doc}, {action}, {user}")
    # this is like that with / and . do not change
    confirm_action_method = "/api/method/vcm.erpnext_vcm.utilities.whatsapp.powhatsapp.confirm_action"

    params = {
        "action": action,
        "doctype": doc.get("doctype"),
        "docname": doc.get("name"),
        "user": user,
    }

    return get_url(confirm_action_method + "?" + get_signed_params(params))


@frappe.whitelist(allow_guest=True)
def get_purchase_order_image(docname):
    docs = frappe.get_all("Purchase Order", fields=["*"], filters={"name": docname})
    if not docs:
        frappe.throw("Doesn't exist.")
    doc = frappe._dict(docs[0])
    items = frappe.get_all(
        "Purchase Order Item",
        fields=["*"],
        filters={"parent": doc.name},
        order_by="idx asc",
    )
    currency = frappe.get_cached_value("Company", doc.company, "default_currency")
    template_data = {
        "doc": doc,
        "currency": currency,
        "items": items,
        "document_link": frappe.utils.get_url_to_form("Purchase Order", doc.name),
    }
    message_html = frappe.render_template(
        "vcm/erpnext_vcm/utilities/whatsapp_template/powhatsapp_template.html",
        template_data,
    )
    img = imgkit.from_string(
        message_html,
        False,
        options={
            "format": "png",
        },
    )

    frappe.local.response.filename = f"approval_{doc.name}.png"
    frappe.local.response.filecontent = img
    frappe.local.response.type = "download"


@frappe.whitelist(allow_guest=True)
def confirm_action(doctype, docname, user, action):
    if not verify_request():
        return

    logged_in_user = frappe.session.user
    if logged_in_user == "Guest" and user:
        # to allow user to apply action without login
        frappe.set_user(user)

    doc = frappe.get_doc(doctype, docname)

    ### Additional by NRHD
    workflow_state = get_doc_workflow_state(doc)
    if (
        (workflow_state == "Final Level Approved" and action == "Final Approve")
        or (workflow_state == "First Level Approved" and action == "First Approve")
        or (workflow_state == "Recommended" and action == "Recommend")
    ):
        return_already_approved_page(doc)
    ###
    else:
        newdoc = apply_workflow(doc, action)
        frappe.db.commit()
        return_success_page(newdoc)

    # reset session user
    if logged_in_user == "Guest":
        frappe.set_user(logged_in_user)
