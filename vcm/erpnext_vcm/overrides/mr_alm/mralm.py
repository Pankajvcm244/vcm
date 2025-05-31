from datetime import date

import logging
logging.basicConfig(level=logging.DEBUG)

from vcm.erpnext_vcm.utilities.whatsapp.mrwhatsapp import (
    send_whatsapp_approval,
)
from frappe.model.document import Document
from frappe.model.workflow import get_workflow_name
from frappe.workflow.doctype.workflow_action.workflow_action import (
    get_doc_workflow_state,
)
from vcm.erpnext_vcm.overrides.mr_alm.mrworkflow_action import (
    get_approval_link,
    get_rejection_link,
)
import frappe
from frappe.utils.background_jobs import enqueue


def get_mrn_alm_level(doc, amount_field="total"):
    """
    Get ALM level for MR
    """
    # frappe.errprint(doc.as_dict())
    #deciding_amount = getattr(doc, amount_field)

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
        
            if doc.department == l.department:
                #frappe.errprint(f"{deciding_amount} {l.amount_condition}")
                #logging.debug(f"in MR get_alm_level {l}, {l.department} ")
                return l
    return None


def assign_and_notify_mrn_next_authority(doc, method="Email"):
    user = None
    current_state = doc.workflow_state
    states = ("Pending", "L1 Approved", "L2 Approved")
    approvers = (
        "custom_l1_approver",
        "custom_l2_approver",
        "custom_final_approver",
    )
    logging.debug(f"in MR assign_and_notify_next_authority {doc.name}, {current_state}")
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
        mobile_no = frappe.get_value("User", user, "mobile_no")
        #logging.debug(f"in assign_and_notify_next_authority PO mobile {mobile_no}")
        if is_eligible_to_send_on_whatsapp(user, mobile_no) or method == "WhatsApp":            
            allowed_options = get_allowed_options(user, doc)
            #logging.debug(f"in assign_and_notify_next_authority calling send whatsapp {doc},{user},{mobile_no}, {allowed_options}  ")
            send_whatsapp_approval(doc, user, mobile_no, allowed_options)
        #else:
        send_email_approval(doc, user)

    #if current_state == "Final Level Approved":
    if current_state in ("Final Level Approved", "Rejected"):
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
    # po_approval_settings = frappe.get_cached_doc("VCM WhatsAPP Settings")
    # if po_approval_settings.po_whatsapp_enabled and mobile_no:
    #     return True
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
            "description": "Material Request approval for " + doc.name,
        }
    )
    todo_doc.insert()
    return

def check_approver_assigned(doc):    
    user = frappe.session.user
    proposed_state = doc.workflow_state      
    # when we reach here workflow state is already set to next proposed state
    # we are not check reject request as it can happen at any stage and we need to check doc is at what state to decide rejecter
    if (proposed_state == "L1 Approved"):
        if (
                getattr(doc, "custom_l1_approver") is not None
                and getattr(doc, "custom_l1_approver") != ""
            ):
                approver_user = getattr(doc, "custom_l1_approver")
                #logging.debug(f"in check_approver_assigned 1 {user}, {approver_user}, {proposed_state} ")
                if approver_user  != user:
                    frappe.throw("You are not allowed to approve this Material Request request.")
    if (proposed_state == "L2 Approved"):
        if (
                getattr(doc, "custom_l2_approver") is not None
                and getattr(doc, "custom_l2_approver") != ""
            ):
                approver_user  = getattr(doc, "custom_l2_approver")
                #logging.debug(f"in check_approver_assigned 2 {user}, {approver_user}, {proposed_state} ")
                if approver_user  != user:
                    frappe.throw("You are not allowed to approve this Material Request.")
    if (proposed_state == "Final Level Approved"):
        if (
                getattr(doc, "custom_final_approver") is not None
                and getattr(doc, "custom_final_approver") != ""
            ):
                approver_user  = getattr(doc, "custom_final_approver")
                #logging.debug(f"in check_approver_assigned 3 {user}, {approver_user}, {proposed_state} ")
                if approver_user  != user:
                    frappe.throw("You are not allowed to approve this Material Request.")
    return

def send_email_approval(doc, user):
    #logging.debug(f"in send_email_approval sending email {doc},{user}")
    currency = frappe.get_cached_value("Company", doc.company, "default_currency")
    allowed_options = get_allowed_options(user, doc)
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
            "vcm/erpnext_vcm/utilities/email_templates/mr_template.html",
            template_data,
        ),
        "subject": "#MR :{} Approval".format(doc.name),
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
            "ToDo", {"reference_type": "Material Request", "reference_name": doc.name}
        )
    else:
        frappe.db.set_value(
            "ToDo",
            {"reference_type": "Material Request", "reference_name": doc.name},
            "status",
            "Closed",
        )
    return

#this fucntions shows all possible next actions based upon current state
# If L2 Approved then alowoable actions are Final Approve and Reject
def get_allowed_options(user: str, doc: Document):
    roles = frappe.get_roles(user)
    workflow = get_workflow_name(doc.get("doctype"))
    if not workflow:
        return set()
    state = get_doc_workflow_state(doc)
    #logging.debug(f"**in get_allowed_options 1  ******{workflow }, {state}")
    transitions = frappe.get_all(
        "Workflow Transition",
        fields=[
            "allowed",
            "action",
            "`condition`",
        ],
        filters=[
            ["parent", "=", workflow],
            ["state", "=", state],
        ],
    )
    L1_APPROVER_FLAG = False
    L2_APPROVER_FLAG = False
    FINAL_APPROVER_FLAG = False
    if (getattr(doc, "custom_l1_approver") != ""):
        L1_APPROVER_FLAG = True
    if (getattr(doc, "custom_l2_approver") != ""):
        L2_APPROVER_FLAG = True 
    if (getattr(doc, "custom_final_approver") != ""):
        FINAL_APPROVER_FLAG = True     
    #logging.debug(f"**in get_allowed_options FLAGS {L1_APPROVER_FLAG},{L2_APPROVER_FLAG},{FINAL_APPROVER_FLAG} ")
    applicable_actions = []
    # when we reach here state is next proposed state of document.
    # is Draft document it will come here as pending
    for transition in transitions:
        if transition["allowed"] in roles:
            condition = transition["action"]
            #logging.debug(f"Evaluating condition {transition}, *{condition}  ")
            if (state  == "Pending"):
                if L1_APPROVER_FLAG:
                    if transition["action"] in ["L1 Approve", "Reject"]:
                        #logging.debug(f"**in get_allowed_options 2-1: {state}, {applicable_actions} ")
                        applicable_actions.append(transition["action"])
                elif L2_APPROVER_FLAG:
                    if transition["action"] in ["L2 Approve", "Reject"]:
                        logging.debug(f"**in get_allowed_options 3-1: {state}, {applicable_actions} ")
                        applicable_actions.append(transition["action"])
                elif FINAL_APPROVER_FLAG:
                    if transition["action"] in ["Final Approve", "Reject"]:
                        #logging.debug(f"**in get_allowed_options 4-1: {state}, {applicable_actions} ")
                        applicable_actions.append(transition["action"])
            elif (state  == "L1 Approved"):
                if L2_APPROVER_FLAG:
                    if transition["action"] in ["L2 Approve", "Reject"]:
                        #logging.debug(f"**in get_allowed_options L2-1: {state}, {applicable_actions} ")
                        applicable_actions.append(transition["action"])
                elif FINAL_APPROVER_FLAG:
                    if transition["action"] in ["Final Approve", "Reject"]:
                        #logging.debug(f"**in get_allowed_options L2-2: {state}, {applicable_actions} ")
                        applicable_actions.append(transition["action"])                            
            elif (state == "L2 Approved"):
                if FINAL_APPROVER_FLAG:
                    if transition["action"] in ["Final Approve", "Reject"]:
                        applicable_actions.append(transition["action"])                        
    #logging.debug(f"**in get_allowed_options 5  *************{applicable_actions} ")
    return set(applicable_actions)  ## Unique Actions


