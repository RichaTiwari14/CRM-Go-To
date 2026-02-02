# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMDeal(Document):
	pass

@frappe.whitelist()
def create_project_from_deal(deal):
    deal = frappe.get_doc("CRM Deal", deal)

    if deal.project_created:
        frappe.throw("Project already created")

    project = frappe.new_doc("Project Master")
    project.project_name = deal.deal_name
    project.deal = deal.name
    project.client = deal.client
    project.project_owner = deal.account_manager
    project.start_date = frappe.utils.today()
    project.planned_end_date = deal.expected_close_date
    project.status = "Draft"
    project.insert(ignore_permissions=True)

    deal.project_created = 1
    deal.project= project.name
    deal.status = "In Progress"
    deal.save(ignore_permissions=True)

    return {
        "project": project.name
    }
