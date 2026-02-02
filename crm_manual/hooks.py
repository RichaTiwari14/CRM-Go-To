app_name = "crm_manual"
app_title = "CRM-Go-To"
app_publisher = "CRM"
app_description = "CRM"
app_email = "crm@gmail.com"
app_license = "mit"

doctype_dashboard = {
    "CRM Lead": "crm_manual.crm_go_to.doctype.crm_lead.crm_lead.get_dashboard_data"
}
app_include_css = "/assets/crm_manual/css/crm_lead.css"

scheduler_events = {
    "daily": [
        "crm_manual.crm_go_to.doctype.utils.sla_engine.test_mark_not_contacted_1_min",
        "crm_manual.crm_go_to.doctype.utils.sla_engine.sla_stage_followup_engine",
        "crm_manual.crm_go_to.doctype.utils.sla_engine.update_lead_inactivity_status"
    ],
    "hourly": [
        "crm_manual.crm_go_to.doctype.utils.sla_engine.send_sla_breach_alerts"
    ]
}
doctype_js = {
    "CRM Lead": "public/js/crm_lead.js",
    "Lead Interaction Log": "public/js/crm_lead.js",
    "Client Master": "public/js/client_master.js",
    "CRM Quotation": "public/js/crm_quotation.js",
    "Prospecting": "public/js/prospecting.js"
}
# scheduler_events = {
#     "hourly": [
#         "crm_manual.crm_go_to.sla.lead_tat_checker.check_lead_tat"
#     ]
# }


# fixtures = [
#     {
#         "doctype": "Client Script"
#     },
#     {
#         "doctype": "Server Script"
#     },
#     {
#         "doctype": "Workflow"
#     },
#     {
#         "doctype": "Custom Field"
#     },
#     {
#         "doctype": "Property Setter"
#     }
# ]
# # Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "crm_manual",
# 		"logo": "/assets/crm_manual/logo.png",
# 		"title": "CRM-Go-To",
# 		"route": "/crm_manual",
# 		"has_permission": "crm_manual.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/crm_manual/css/crm_manual.css"
# app_include_js = "/assets/crm_manual/js/crm_manual.js"

# include js, css files in header of web template
# web_include_css = "/assets/crm_manual/css/crm_manual.css"
# web_include_js = "/assets/crm_manual/js/crm_manual.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "crm_manual/public/scss/website"

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

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "crm_manual/public/icons.svg"

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
# 	"methods": "crm_manual.utils.jinja_methods",
# 	"filters": "crm_manual.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "crm_manual.install.before_install"
# after_install = "crm_manual.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "crm_manual.uninstall.before_uninstall"
# after_uninstall = "crm_manual.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "crm_manual.utils.before_app_install"
# after_app_install = "crm_manual.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "crm_manual.utils.before_app_uninstall"
# after_app_uninstall = "crm_manual.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "crm_manual.notifications.get_notification_config"

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

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"crm_manual.tasks.all"
# 	],
# 	"daily": [
# 		"crm_manual.tasks.daily"
# 	],
# 	"hourly": [
# 		"crm_manual.tasks.hourly"
# 	],
# 	"weekly": [
# 		"crm_manual.tasks.weekly"
# 	],
# 	"monthly": [
# 		"crm_manual.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "crm_manual.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "crm_manual.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "crm_manual.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["crm_manual.utils.before_request"]
# after_request = ["crm_manual.utils.after_request"]

# Job Events
# ----------
# before_job = ["crm_manual.utils.before_job"]
# after_job = ["crm_manual.utils.after_job"]

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
# 	"crm_manual.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

