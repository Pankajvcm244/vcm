from datetime import date
import frappe

import logging
logging.basicConfig(level=logging.DEBUG)


from frappe.model.document import Document
from frappe.model.workflow import get_workflow_name
from frappe.workflow.doctype.workflow_action.workflow_action import (
    get_doc_workflow_state,
)
from vcm.erpnext_vcm.overrides.stock_alm.stockworkflow_action import (
    get_approval_link,
    get_rejection_link,
)
import frappe
from frappe.utils.background_jobs import enqueue


def get_stock_alm_level(doc, amount_field="total"):
    """
    Get ALM level for stock entry.
    """
    for l in frappe.db.sql(
        f"""
                SELECT level.*
                FROM `tabVCM Warehouse ALM` alm
                JOIN `tabVCM Warehouse ALM Child Table` level
                    ON level.parent = alm.name
                WHERE alm.document = "{doc.doctype}"
                    AND alm.company = "{doc.company}"
                    AND level.target_warehouse = "{doc.to_warehouse}"    
                ORDER BY level.idx
                    """,
        as_dict=1,
    ):
        
        if doc.to_warehouse == l.target_warehouse:
            return l
    return None



def assign_and_notify_next_authority(doc, method="Email"):
    logging.debug(f"in assign_and_notify_next_authority s{doc},")
    user = None
    current_state = doc.workflow_state
    states = ("Checked", "Recommender","First Level Approved")
    approvers = (
        "recommender",
        "first_approver",
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
                        break
                break
        if user is None:
            frappe.msgprint("Next authority is not Found. Please check ALM.")
            # frappe.throw("Next authority is not Found. Please check ALM.")
        close_assignments(doc)
        logging.debug(f"in assign_and_notify_next_authority  2{doc},")
        assign_to_next_approving_authority(doc, user)
        send_email_approval(doc, user)

    if current_state in ("Final Level Approved", "Prepared"):
        close_assignments(doc, remove=True)
    frappe.db.commit()
    return



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
            "description": "Stock Entry Approval for Material Transfer <b>",
        }
    )
    todo_doc.insert()
    return


def send_email_approval(doc, user):
    logging.debug(f"in send_email_approval sending email {doc},{user}")
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
            "vcm/erpnext_vcm/utilities/email_templates/stockentry.html",
            template_data,
        ),
        "subject": "#STE :{} Approval".format(doc.name),
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
            "ToDo", {"reference_type": "Stock Entry", "reference_name": doc.name}
        )
    else:
        frappe.db.set_value(
            "ToDo",
            {"reference_type": "Stock Entry", "reference_name": doc.name},
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
    #logging.debug(f"**in HKM get_allowed_options 1  ******{workflow }, {state}")
    applicable_actions = []
    for transition in transitions:
        if transition["allowed"] in roles and (
            (transition["condition"] is None)
            or eval(transition["condition"].replace("frappe.session.user", "user"))
        ):
            applicable_actions.append(transition["action"])
    return set(applicable_actions)  ## Unique Actions
