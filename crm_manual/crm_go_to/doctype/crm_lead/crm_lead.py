# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CRMLead(Document):
    def validate(self):
        if not self.get_db_value("lead_stage"):
            return

        old = self.get_db_value("lead_stage")
        new = self.lead_stage

        if old == new:
            return

        if new == "Contacted":
            frappe.throw("Lead cannot move back to Contacted")

        if not is_valid_stage_change(old, new, context=self.get("stage_action")):
            frappe.throw(f"Invalid stage transition: {old} → {new}")


def get_dashboard_data():
    return {
        "heatmap": False,
        "fieldname": "lead",

        # 👇 yahan mapping add ki
        "non_standard_fieldnames": {
            "Call Log Go-To": "linked_lead"
        },

        "transactions": [
            {
                "label": _("Interactions"),
                "items": ["Call Log Go-To"]
            },
            {
                "label": _("Prospecting"),
                "items": ["Prospecting"]
            },
            {
                "label": _("Sales"),
                "items": ["CRM Quotation"]
            }
        ]
    }

VALID_FLOW = [
    "New",
    "Contacted",
    "Prospecting",
    "Quotation",
    "Converted to Deal"
]

BACKWARD_RULES = {
    "Quotation": "Prospecting",
}

def get_previous_stage(current_stage):
    idx = VALID_FLOW.index(current_stage)
    return VALID_FLOW[idx - 1] if idx > 0 else None


def is_valid_stage_change(old, new, context=None):
    # Forward allowed only step-by-step
    if new in VALID_FLOW and VALID_FLOW.index(new) == VALID_FLOW.index(old) + 1:
        return True

    # Allowed backward rules only on NO
    if context == "rejected" and BACKWARD_RULES.get(old) == new:
        return True

    return False
def onload(doc):
    doc.set_onload("make_call_log_args", {
        "linked_lead": doc.name
    })
