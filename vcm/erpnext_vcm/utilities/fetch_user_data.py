import frappe
# we were using this in PO purchase person filtering, but now w eare doign that via js
# @frappe.whitelist()
# def vcm_get_users_with_role(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
#     """Fetch users who have the 'Purchase User' role"""
    
#     #role = filters.get("role") if filters else "Purchase User"
#     role = "Purchase User"
#     users = frappe.get_all(
#         "User",
#         filters={"name": ["in", frappe.get_all("Has Role", filters={"role": role}, pluck="parent")]},
#         pluck="name"
#     )

#     return [(user,) for user in users]  # Return as list of tuples
