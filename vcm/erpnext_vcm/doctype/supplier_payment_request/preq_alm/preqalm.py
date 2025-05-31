from datetime import date

import logging
logging.basicConfig(level=logging.DEBUG)

from vcm.erpnext_vcm.utilities.whatsapp.preqwhatsapp import (
    send_whatsapp_approval,
)
from frappe.model.document import Document
from frappe.model.workflow import get_workflow_name
from frappe.workflow.doctype.workflow_action.workflow_action import (
    get_doc_workflow_state,
)
from vcm.erpnext_vcm.doctype.supplier_payment_request.preq_alm.preqworkflow_action import (
    get_approval_link,
    get_rejection_link,
)
import frappe
from frappe.utils.background_jobs import enqueue


def get_preq_alm_level(doc, amount_field="preq_amount"):
    """
    Get ALM level for Supplier PREQ.
    """
    # frappe.errprint(doc.as_dict())
    #logging.debug(f"in get_preq_alm_level PREQ {doc.name}, {amount_field}")
    deciding_amount = getattr(doc, amount_field)

    for l in frappe.db.sql(
        f"""
                SELECT level.*
                FROM `tabVCM PREQ DEPT ALM` alm
                JOIN `tabVCM PREQ DEPT ALM TABLE` level
                    ON level.parent = alm.name
                WHERE alm.document = "{doc.doctype}"
                    AND alm.company = "{doc.company}"
                    AND level.department = "{doc.department}"   
                ORDER BY level.idx
                    """,
        as_dict=1,
    ):
        #logging.debug(f"{deciding_amount} {l.amount_condition}")
        if eval(f"{deciding_amount} {l.amount_condition}"):
            return l
    return None


def assign_and_notify_next_preq_authority(doc, method="Email"):
    user = None
    current_state = doc.workflow_state
    states = ("L1 Approved", "L2 Approved", "L3 Approved")
    #logging.debug(f"in assign_and_notify_next_authority PREQ {doc.name}, {current_state}")
    approvers = (
        "l1_approving_authority",
        "l2_approving_authority",
        "l3_approving_authority",   
        "final_approving_authority",
    )
    #logging.debug(f"in assign_and_notify_next_authority PREQ {doc.name}, {current_state}")
    if current_state in states:
        for i, state in enumerate(states):
            if current_state == state:
                for approver in approvers[i : len(approvers)]:
                    if (
                        getattr(doc, approver) is not None
                        and getattr(doc, approver) != ""
                    ):
                        user = getattr(doc, approver)
                        break
                break
        if user is None:
            frappe.throw("Next authority is not Found. Please check ALM.")
        close_assignments(doc)
        assign_to_next_approving_authority(doc, user)
        #mobile_no = frappe.get_value("User", user, "mobile_no")
        #logging.debug(f"in assign_and_notify_next_authority PO mobile {mobile_no}")
        #if is_eligible_to_send_on_whatsapp(user, mobile_no) or method == "WhatsApp":            
        #    allowed_options = get_allowed_options(user, doc)
        #    logging.debug(f"in assign_and_notify_next_authority calling send whatsapp {doc},{user},{mobile_no}, {allowed_options}  ")
            #send_whatsapp_approval(doc, user, mobile_no, allowed_options)
        #else:
        send_email_approval(doc, user)

    #if current_state == "Final Level Approved":
    if current_state in ("Final Level Approved", "Prepared"):
        close_assignments(doc, remove=True)
    frappe.db.commit()
    return


def is_eligible_to_send_on_whatsapp(user, mobile_no):
    #logging.debug(f"VCM  is_eligible_to_send_on_whatsapp 1 {user}, {mobile_no}")
    # user_meta = frappe.get_meta("User")
    #logging.debug(f"VCM  is_eligible_to_send_on_whatsapp 2 {user_meta}")
    # if user_meta.has_field("purchase_order_whatsapp_approval"):
    #     if not frappe.get_value("User", user, "purchase_order_whatsapp_approval"):
    #         return False
    po_approval_settings = frappe.get_cached_doc("VCM WhatsAPP Settings")
    if po_approval_settings.po_whatsapp_enabled and mobile_no:
        return True
    return False


def assign_to_next_approving_authority(doc, user):
    #logging.debug(f"in assign_to_next_approving_authority PREQ {doc.name}, {user}")
    todo_doc = frappe.get_doc(
        {
            "doctype": "ToDo",
            "status": "Open",
            "allocated_to": user,
            "assigned_by": frappe.session.user,
            "reference_type": doc.doctype,
            "reference_name": doc.name,
            "date": date.today(),
            "description": "Payment Request approval for " + doc.supplier,
        }
    )
    todo_doc.insert()
    return


def send_email_approval(doc, user):    
    currency = frappe.get_cached_value("Company", doc.company, "default_currency")
    allowed_options = get_allowed_options(user, doc)
    #logging.debug(f"in send_email_approval sending email {doc},{user},{allowed_options}")
    template_data = {
        "doc": doc,
        "user": user,
        "currency": currency,
        "approval_link": get_approval_link(doc, user, allowed_options),
        "rejection_link": get_rejection_link(doc, user),
        "document_link": frappe.utils.get_url_to_form(doc.doctype, doc.name),
    }

    email_args = {
        "recipients": [user],
        "message": frappe.render_template(
            "vcm/erpnext_vcm/utilities/email_templates/preqemail_template.html",
            template_data,
        ),
        "subject": "#Payment Request:{} Approval".format(doc.name),
        "reference_doctype": doc.doctype,
        "reference_name": doc.name,
        "reply_to": doc.owner,
        "delayed": False,
        "sender": doc.owner,
    }
    enqueue(
        method=frappe.sendmail, queue="short", timeout=300, is_async=True, **email_args
    )
    return


def close_assignments(doc, remove=True):
    if remove:
        frappe.db.delete(
            "ToDo", {"reference_type": "Supplier Payment Request", "reference_name": doc.name}
        )
    else:
        frappe.db.set_value(
            "ToDo",
            {"reference_type": "Supplier Payment Request", "reference_name": doc.name},
            "status",
            "Closed",
        )
    return


def get_allowed_options(user: str, doc: Document):
    roles = frappe.get_roles(user)
    workflow = get_workflow_name(doc.get("doctype"))
    state = get_doc_workflow_state(doc)
    transitions = frappe.get_all(
        "Workflow Transition",
        fields=[
            "allowed",
            "action",
            "`condition`",
        ],
        filters=[
            ["parent", "=", workflow],
            ["state", "=", get_doc_workflow_state(doc)],
        ],
    )
    #logging.debug(f"**in PREQ get_allowed_options 1  ******{workflow }, {state}")
    applicable_actions = []
    for transition in transitions:
        if transition["allowed"] in roles and (
            (transition["condition"] is None)
            or eval(transition["condition"].replace("frappe.session.user", "user"))
        ):
            condition = transition["condition"]
            applicable_actions.append(transition["action"])
    return set(applicable_actions)  ## Unique Actions
