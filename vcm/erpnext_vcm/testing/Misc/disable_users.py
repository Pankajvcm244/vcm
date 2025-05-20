import frappe
#bench --site test.vcmerp.in execute vcm.erpnext_vcm.testing.Misc.disable_users.disable_all_users

def disable_all_users():
    users = frappe.get_all("User", filters={"enabled": 1}, fields=["name"])

    for user in users:
        if user.name not in ["Administrator", "Guest", "pankaj.sharma@vcm.org.in", "rahul.chaudhary@vcm.org.in", 
                             "teena.arora@vcm.org.in", "sahil.chitkara@vcm.org.in", "ajay.gaur@vcm.org.in", "lokesh.sisodiya@vcm.org.in",
                             "aman.soni@vcm.org.in", "sund@vcm.org.in", "prashant.yadav@vcm.org.in","pooja.rani@vcm.org.in",
                             "gaurav.vyas@vcm.org.in"
                            ]:
 
            frappe.db.set_value("User", user.name, "enabled", 0)
            print(f"Disabled user: {user.name}")

    frappe.db.commit()