# Copyright (c) 2025, pankaj.sharma@vcm.org.in and contributors
# For license information, please see license.txt

#import logging
#logging.basicConfig(level=logging.DEBUG)

from datetime import date
from hkm.erpnext___custom.overrides.purchase_order.whatsapp import (
    send_whatsapp_approval,
)
from frappe.model.document import Document
from frappe.model.workflow import get_workflow_name
from frappe.workflow.doctype.workflow_action.workflow_action import (
    get_doc_workflow_state,
)
from vcm.erpnext_vcm.utilities.vcm_dept_workflow_action import (
    get_approval_link,
    get_rejection_link,
)
import frappe
from frappe.utils.background_jobs import enqueue


def get_vcm_storereq_approval_level(doc):
    """
    Get ALM level for purchase order.
    """
    # frappe.errprint(doc.as_dict())
    #deciding_dept = getattr(doc, doc.department)
    #logging.debug(f"in get_vcm_storereq_approval_level before_save  {doc}, {doc.department}  ")

    for l in frappe.db.sql(
        f"""
                SELECT level.*
                FROM `tabVCM DEPT Approval` alm
                JOIN `tabVCM DEPT Approval Table` level
                    ON level.parent = alm.name
                WHERE alm.document = "{doc.doctype}"
                    AND alm.company = "{doc.company}"
                    AND level.department = "{doc.department}"    
                ORDER BY level.idx
                    """,
        as_dict=1,
    ):
        
    # frappe.errprint(f"{deciding_amount} {l.amount_condition}")
    #logging.debug(f"in get_vcm_storereq_approval_level before_save3  {l}, {l.department} ")
        if doc.department == l.department:
            return l
    return None


def assign_and_notify_next_authority(doc, method="Email"):
    user = None
    current_state = doc.workflow_state
    #logging.debug(f"in assign_and_notify_next_authority 1 {doc}, {current_state} ")
    states = ("Pending", "L1 Approved", "L2 Approved")
    approvers = (
        "l1_approver",
        "l2_approver",
        "final_approver",
    )
    if current_state in states:
        for i, state in enumerate(states):
            if current_state == state:
                for approver in approvers[i : len(approvers)]:
                    if (
                        getattr(doc, approver) is not None
                        and getattr(doc, approver) != ""
                    ):
                        user = getattr(doc, approver)
                        #logging.debug(f"in assign_and_notify_next_authority 1 {user}, {current_state} ")
                        break
                break
        if user is None:
            frappe.throw("Next authority is not Found. Please check Approval Flow.")
        close_assignments(doc)
        assign_to_next_approving_authority(doc, user)
        mobile_no = frappe.get_value("User", user, "mobile_no")
        if is_eligible_to_send_on_whatsapp(user, mobile_no) or method == "WhatsApp":
            allowed_options = get_allowed_options(user, doc)
            #send_whatsapp_approval(doc, user, mobile_no, allowed_options)
        else:
            send_email_approval(doc, user)

    if current_state == "Final Level Approved":
        #logging.debug(f"**in assign_and_notify_next_authority 8 {doc}, {current_state} ")
        close_assignments(doc, remove=True)
    frappe.db.commit()
    return


def is_eligible_to_send_on_whatsapp(user, mobile_no):
    #user_meta = frappe.get_meta("User")

    #if user_meta.has_field("purchase_order_whatsapp_approval"):
    #    if not frappe.get_value("User", user, "purchase_order_whatsapp_approval"):
    #        return False
    #po_approval_settings = frappe.get_cached_doc("HKM General Settings")
    #if po_approval_settings.po_approval_on_whatsapp and mobile_no:
    #    return True
    return False


def assign_to_next_approving_authority(doc, user):
    todo_doc = frappe.get_doc(
        {
            "doctype": "ToDo",
            "status": "Open",
            "allocated_to": user,
            "assigned_by": frappe.session.user,
            "reference_type": doc.doctype,
            "reference_name": doc.name,
            "date": date.today(),
            "description": "VCM StoreReq " + doc.name,
        }
    )
    #logging.debug(f"**in assign_to_next_approving_authority 1 {user}, {doc.doctype}, {doc.name}, {frappe.session.user} ")
    todo_doc.insert()
    return

def check_approver_assigned(doc):    
    user = None
    proposed_state = doc.workflow_state    

    #System Manager can approve any request
    user = frappe.session.user  # Get current logged-in user
    roles = frappe.get_roles(user)  # Get user roles
    # Check if System Manager is in the user's roles
    #logging.debug(f"in VCMStoreRequisition check_approver_assigned  {user}, {proposed_state} ")
    if "System Manager" in roles:
        return True
    # when we reach here workflow state is already set to next proposed state
    # we are not check reject request as it can happen at any stage and we need to check doc is at what state to decide rejecter
    if (proposed_state == "L1 Approved"):
        if (
                getattr(doc, "l1_approver") is not None
                and getattr(doc, "l1_approver") != ""
            ):
                approver_user = getattr(doc, "l1_approver")
                #logging.debug(f"in check_approver_assigned 1 {user}, {approver_user}, {proposed_state} ")
                if approver_user  != user:
                    frappe.throw("You are not allowed to approve this Store Req request.")
    if (proposed_state == "L2 Approved"):
        if (
                getattr(doc, "l2_approver") is not None
                and getattr(doc, "l2_approver") != ""
            ):
                approver_user  = getattr(doc, "l2_approver")
                #logging.debug(f"in check_approver_assigned 2 {user}, {approver_user}, {proposed_state} ")
                if approver_user  != user:
                    frappe.throw("You are not allowed to approve this Store Req request.")
    if (proposed_state == "Final Level Approved"):
        if (
                getattr(doc, "final_approver") is not None
                and getattr(doc, "final_approver") != ""
            ):
                approver_user  = getattr(doc, "final_approver")
                #logging.debug(f"in check_approver_assigned 3 {user}, {approver_user}, {proposed_state} ")
                if approver_user  != user:
                    frappe.throw("You are not allowed to approve this Store Req request.")
    return


def send_email_approval(doc, user):
    currency = frappe.get_cached_value("Company", doc.company, "default_currency")
    allowed_options = get_allowed_options(user, doc)
    #logging.debug(f"**in send_email_approval vcm item rew 1 {currency}, {allowed_options}")
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
            "vcm/erpnext_vcm/utilities/email_templates/store_requisition_template.html",
            template_data,
        ),
        "subject": "#Item Request :{} Approval".format(doc.name),
        "reference_doctype": doc.doctype,
        "reference_name": doc.name,
        "reply_to": doc.owner,
        "delayed": False,
        "sender": doc.owner,
    }
    #logging.debug(f"**in send_email_approval vcm item req2 {doc.name}, {doc.doctype}, {doc.owner}, {user} ")
    enqueue(
        method=frappe.sendmail, queue="short", timeout=300, is_async=True, **email_args
    )
    frappe.sendmail(
        recipients=[user],
        subject="#Item Request :{} Approval".format(doc.name),
        message=frappe.render_template(
            "vcm/erpnext_vcm/utilities/email_templates/store_requisition_template.html", template_data )
    )
    #logging.debug(f"**in send_email_approval vcm item req3  ************* ")

    return


def close_assignments(doc, remove=True):
    if remove:
        frappe.db.delete(
            "ToDo", {"reference_type": "VCM Item Request", "reference_name": doc.name}
        )
    else:
        frappe.db.set_value(
            "ToDo",
            {"reference_type": "VCM Item Request", "reference_name": doc.name},
            "status",
            "Closed",
        )
    return


def get_allowed_options(user: str, doc: Document):
    roles = frappe.get_roles(user)
    workflow = get_workflow_name(doc.get("doctype"))
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
    applicable_actions = []
    for transition in transitions:
        if transition["allowed"] in roles and (
            (transition["condition"] is None)
            or eval(transition["condition"].replace("frappe.session.user", "user"))
        ):
            applicable_actions.append(transition["action"])
    return set(applicable_actions)  ## Unique Actions