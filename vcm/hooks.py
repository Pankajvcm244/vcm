app_name = "vcm"
app_title = "Vcm"
app_publisher = "pankaj.sharma@vcm.org.in"
app_description = "VCM ERP"
app_email = "pankaj.sharma@vcm.org.in"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "vcm",
# 		"logo": "/assets/vcm/logo.png",
# 		"title": "Vcm",
# 		"route": "/vcm",
# 		"has_permission": "vcm.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vcm/css/vcm.css"
# app_include_js = "/assets/vcm/js/vcm.js"

# include js, css files in header of web template
# web_include_css = "/assets/vcm/css/vcm.css"
# web_include_js = "/assets/vcm/js/vcm.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vcm/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

doctype_js = {    
    "Purchase Receipt": "public/js/purchase_receipt.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Material Request": "public/js/material_request.js",
    "Purchase Order": "public/js/purchase_order.js",
    "Purchase Invoice": "public/js/purchase_invoice.js",
    "Payment Entry": "public/js/payment_entry.js",

}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "vcm/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "vcm.utils.jinja_methods",
# 	"filters": "vcm.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "vcm.install.before_install"
# after_install = "vcm.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "vcm.uninstall.before_uninstall"
# after_uninstall = "vcm.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "vcm.utils.before_app_install"
# after_app_install = "vcm.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "vcm.utils.before_app_uninstall"
# after_app_uninstall = "vcm.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vcm.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }
override_doctype_class = {
    "POS Invoice": "vcm.erpnext_vcm.overrides.VCMPOSInv.VCMPOSInv",
    "Sales Invoice": "vcm.erpnext_vcm.overrides.VCMSalesInv.VCMSalesInv",
    "Purchase Order": "vcm.erpnext_vcm.overrides.VCMPurchaseOrder.VCMPurchaseOrder",
    "Purchase Invoice": "vcm.erpnext_vcm.overrides.VCMPurchaseInvoice.VCMPurchaseInvoice",
    "Payment Entry": "vcm.erpnext_vcm.overrides.VCMPaymentEntry.VCMPaymentEntry",
    "Journal Entry": "vcm.erpnext_vcm.overrides.VCMJournalEntry.VCMJournalEntry",
}


# Importing HKMPOSInvoice and VCMPOSInv from respective modules
from hkm.erpnext___custom.overrides import HKMPOSInvoice
from vcm.erpnext_vcm.overrides import VCMPOSInv
# Reassigning HKMPOS/SalesInvoice to use VCMPOSInv for unified behavior
HKMPOSInvoice = VCMPOSInv

from hkm.erpnext___custom.overrides import HKMSalesInvoice
from vcm.erpnext_vcm.overrides import VCMSalesInv
# Reassigning HKMPOS/SalesInvoice to use VCMPOSInv for unified behavior
HKMSalesInvoice = VCMSalesInv

#HKMPurchaseOrder is in folder purchase_order
from hkm.erpnext___custom.overrides.purchase_order import HKMPurchaseOrder
from vcm.erpnext_vcm.overrides import VCMPurchaseOrder
HKMPurchaseOrder = VCMPurchaseOrder

from hkm.erpnext___custom.overrides import HKMPurchaseInvoice
from vcm.erpnext_vcm.overrides import VCMPurchaseInvoice
HKMPurchaseInvoice = VCMPurchaseInvoice

from hkm.erpnext___custom.overrides import HKMPaymentEntry
from vcm.erpnext_vcm.overrides import VCMPaymentEntry
HKMPaymentEntry = VCMPaymentEntry

from hkm.erpnext___custom.overrides import HKMJournalEntry
from vcm.erpnext_vcm.overrides import VCMJournalEntry







#HKMJournalEntry = VCMJournalEntry

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

#doc_events = {
#    "Journal Entry": {
#        "before_submit": "vcm.erpnext_vcm.utilities.vcm_budget_update_usage.update_vcm_budget_from_jv",
#        "on_cancel": "vcm.erpnext_vcm.utilities.vcm_budget_update_usage.reverse_vcm_budget_from_jv"
#    }
#    
#}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vcm.tasks.all"
# 	],
# 	"daily": [
# 		"vcm.tasks.daily"
# 	],
# 	"hourly": [
# 		"vcm.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vcm.tasks.weekly"
# 	],
# 	"monthly": [
# 		"vcm.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "vcm.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "vcm.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vcm.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["vcm.utils.before_request"]
# after_request = ["vcm.utils.after_request"]

# Job Events
# ----------
# before_job = ["vcm.utils.before_job"]
# after_job = ["vcm.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"vcm.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Fixtures to add workflow in VCM Item Request
fixtures = [
    {
        "doctype": "Report",
    },
    {
        "doctype": "Custom DocPerm",
    },
    {
        "doctype": "POS Profile",
    },
    {
        "doctype": "Workflow",
    },
        {
        "doctype": "Workflow State",
    },
    {
        "doctype": "Custom Field",
        "filters": [
            [ "dt", "in", [
                "Store Requisition",
                "Material Request",
                "Purchase Order",
                "Purchase Receipt",
                "Purchase Invoice",
                "VCM Gate-In",
                # "Sales Invoice",
                # "Stock Entry",
                "Payment Entry",
                "Journal Entry",
                # "Customer",
                # "Asset",
                #"Supplier"
            ],],
        ],
    },
    {
        "doctype": "Role",
    }
]

