# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class CRMLead(Document):

    # =========================================================
    # 🔁 STAGE CHANGE TIMESTAMP & RESET (SAFE)
    # =========================================================
    def before_save(self):
        #  Skip when SLA automation is running
        if frappe.flags.get("in_sla_automation"):
            return

        old_stage = self.get_db_value("lead_stage")
        new_stage = self.lead_stage

        if old_stage != new_stage:
            self.lead_stage_entered_on = now_datetime()
            self.inactivity_flag = 0
            self.inactivity_status = None
            self.response_delay_risk = "Low"

    # =========================================================
    #  MANUAL STAGE VALIDATION (ISO COMPLIANT)
    # =========================================================
    def validate(self):
        #  SLA engine bypass
        if frappe.flags.get("in_sla_automation"):
            return

        if not self.get_db_value("lead_stage"):
            return

        old = self.get_db_value("lead_stage")
        new = self.lead_stage

        if old == new:
            return

        #  backward block
        if new == "Contacted":
            frappe.throw(_("Lead cannot move back to Contacted"))

        if not is_valid_stage_change(old, new, context=self.get("stage_action")):
            frappe.throw(_(f"Invalid stage transition: {old} → {new}"))


# =========================================================
#  DASHBOARD CONFIG
# =========================================================
def get_dashboard_data():
    return {
        "heatmap": False,
        "fieldname": "lead",

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


# =========================================================
#  STAGE FLOW RULES
# =========================================================
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
    if current_stage not in VALID_FLOW:
        return None
    idx = VALID_FLOW.index(current_stage)
    return VALID_FLOW[idx - 1] if idx > 0 else None


def is_valid_stage_change(old, new, context=None):
    # Forward only (step-by-step)
    if (
        new in VALID_FLOW
        and old in VALID_FLOW
        and VALID_FLOW.index(new) == VALID_FLOW.index(old) + 1
    ):
        return True

    # Backward allowed only on rejection
    if context == "rejected" and BACKWARD_RULES.get(old) == new:
        return True

    return False


# =========================================================
#  CALL LOG PREFILL
# =========================================================
def onload(doc):
    doc.set_onload("make_call_log_args", {
        "linked_lead": doc.name
    })
