# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


FORWARD_ORDER = [
    "New",
    "Contacted",
    "Prospecting",
    "Quotation",
    "Converted to Deal"
]

class CallLogGoTo(Document):

    def after_insert(self):
        if self.linked_lead:
            reset_lead_inactivity(self.linked_lead)
        if not self.linked_lead:
            return

        lead = frappe.get_doc("CRM Lead", self.linked_lead)

        current_stage = lead.lead_stage
        target_stage = "Contacted"

        # Move only forward — never backward
        if FORWARD_ORDER.index(target_stage) > FORWARD_ORDER.index(current_stage):
            frappe.db.set_value(
                "CRM Lead",
                self.linked_lead,
                {"lead_stage": target_stage}
            )


@frappe.whitelist()
def make_from_lead(lead):
    doc = frappe.new_doc("Call Log Go-To")
    doc.linked_lead = lead
    doc.insert(ignore_permissions=True)  # Safe insert
    return doc.name  


def reset_lead_inactivity(lead_name):
    frappe.db.set_value(
        "CRM Lead",
        lead_name,
        {
            "inactivity_flag": 0,
            "last_activity_on": now_datetime()
        }
    )    