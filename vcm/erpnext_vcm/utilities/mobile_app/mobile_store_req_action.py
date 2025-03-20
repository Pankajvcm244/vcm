import frappe
from frappe import _

@frappe.whitelist()
def storeRequisition_mobile_approval(docname):
    
    doctype = "VCM StoreRequisition"  

    if not docname:
        frappe.throw(_("Document name is required."))

    if not frappe.db.exists(doctype, docname):
        frappe.throw(_("Document {0} ({1}) does not exist.").format(doctype, docname))

    # Fetch the document
    doc = frappe.get_doc(doctype, docname)

    if not hasattr(doc, "workflow_state"):
        frappe.throw(_("Workflow state is missing in this document."))

    next_action = get_next_action(doc)

    if not next_action:
        frappe.throw(_("No valid action found for the current workflow state."))

    next_workflow_state, new_docstatus = get_next_workflow_state(next_action)

    if not next_workflow_state:
        frappe.throw(_("No valid next workflow state found."))

    # Ensure user has permission
    if not frappe.has_permission(doctype, "write", doc=doc):
        frappe.throw(_("You do not have permission to approve this document."))

    prev_workflow_state = doc.workflow_state

    # Apply workflow state update
    doc.workflow_state = next_workflow_state

    # Use standard ERPNext methods for state change
    if new_docstatus == 1:
        doc.submit()  # Submitting the document
    else:
        doc.save(ignore_permissions=True)  # Save as draft or update state

    if doc.workflow_state != next_workflow_state:
        frappe.throw(_("Failed to update workflow state. Expected: {0}, Found: {1}").format(next_workflow_state, doc.workflow_state))

    if doc.docstatus != new_docstatus:
        frappe.throw(_("Failed to update document status. Expected: {0}, Found: {1}").format(new_docstatus, doc.docstatus))



    doc.add_comment("Workflow", _('{0}').format(next_workflow_state))


    return {
        "status": "success",
        "message": _("Document {0} is now in '{1}' state.").format(docname, next_workflow_state),
        "previous_state": prev_workflow_state,
        "current_state": next_workflow_state,
        "next_action": next_action
    }

def get_next_action(doc):

    workflow_state = doc.workflow_state
    action = ""

    if workflow_state == "Pending":
        if doc.get("l1_approver"):
            action = "L1 Approve"
        elif doc.get("l2_approver"):
            action = "L2 Approve"
        else:
            action = "Final Approve"

    elif workflow_state == "L1 Approved":
        if doc.get("l2_approver"):
            action = "L2 Approve"
        else:
            action = "Final Approve"

    elif workflow_state == "L2 Approved":
        action = "Final Approve"

    return action

def get_next_workflow_state(action):
    """Returns the next workflow state and docstatus based on the action taken"""
    workflow_mapping = {
        "L1 Approve": ("L1 Approved", 0),
        "L2 Approve": ("L2 Approved", 0),
        "Final Approve": ("Final Level Approved", 1)  # Submitted state
    }
    return workflow_mapping.get(action, (None, None))








@frappe.whitelist()
def storeRequisition_mobile_rejection(docname=None):
    
    """Apply workflow action on a document and delete the ToDo"""

    doctype = "VCM StoreRequisition" 

    # Validate API access
    if not frappe.request:
        frappe.throw(_("API not hit."))

    # Validate input parameters
    if not doctype or not docname:
        frappe.throw(_(f"Doctype and docname is required"))

    if not frappe.db.exists(doctype, docname):
        frappe.throw(_("Document {0} ({1}) does not exist.").format(doctype, docname))


    doc = frappe.get_doc(doctype, docname)

    # Ensure the document has a workflow state
    if not hasattr(doc, "workflow_state"):
        frappe.throw(_("Workflow state is missing in this document."))

    doc.workflow_state = "Rejected"
    doc.save(ignore_permissions=True)


    if doc.workflow_state != "Rejected":
        frappe.throw(_("Workflow state update failed."))


    # Log the workflow change for tracking
    doc.add_comment("Workflow", _("Rejected"))
       

    return {
        "status": "success",
        "message": _(f"Document {docname} is now in '{doctype}' state."),
    }