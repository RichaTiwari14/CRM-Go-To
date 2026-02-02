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
        self.validate_conversion_requirements()
        self.apply_utm_attribution()
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
        if self.phone:
            value = self.phone.strip()

            import re
            pattern = r'^[+]?[\d\s-]{7,15}$'

            if not re.match(pattern, value):
                frappe.throw(
                    "Invalid contact number format. Use digits, spaces, + or - only."
                )
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


    def after_save(self):
        self.create_client_on_conversion()

    # --------------------------------------------------
    # SCRIPT 1 — Conversion Validation + Pipeline Exit
    # --------------------------------------------------

    def validate_conversion_requirements(self):

        if self.lead_stage != "Converted to Deal":
            return

        missing = []

        # Person / Company validation
        if self.is_company and not self.company_name:
            missing.append("Company Name")

        if not self.is_company and not self.first_name:
            missing.append("First Name")

        # Contact fields
        if not (self.email or self.phone):
            missing.append("Email or Phone")

        # Source & ownership
        if not self.lead_source:
            missing.append("Lead Source")

        if not self.lead_owner:
            missing.append("Lead Owner")

        if missing:
            frappe.throw(
                "Please complete the following fields before converting to deal:<br><br>"
                + "<br>".join(f"• {m}" for m in missing)
            )

        # Auto-close Lead & remove from pipeline
        self.lead_status = "Closed"
        self.inactivity_status = None
        self.response_delay_risk = 0
        self.next_follow_up = None
        self.expected_response_time = None

    # --------------------------------------------------
    # SCRIPT 2 — UTM Attribution + Lead Scoring
    # --------------------------------------------------

    def apply_utm_attribution(self):

        src = (self.utm_source or "").lower().strip()
        med = (self.utm_medium or "").lower().strip()
        camp = (self.utm_campaign or "").lower().strip()

        channel_map = {
            "google": "Paid Search",
            "gads": "Paid Search",
            "sem": "Paid Search",

            "facebook": "Paid Social",
            "fb": "Paid Social",
            "instagram": "Paid Social",
            "ig": "Paid Social",
            "meta": "Paid Social",
            "linkedin": "Paid Social",
            "youtube": "Video Campaign",

            "email": "Email Campaign",
            "newsletter": "Email Campaign",

            "referral": "Referral / Partner",
            "whatsapp": "Referral / Partner",

            "organic": "Organic Search",
            "seo": "Organic Search",

            "direct": "Direct Traffic"
        }

        self.attribution_channel = "Other"

        for key, val in channel_map.items():
            if key in src or key in med:
                self.attribution_channel = val
                break

        # Build clean marketing source
        parts = []
        if self.utm_source:
            parts.append(self.utm_source)
        if self.utm_medium:
            parts.append(self.utm_medium)
        if self.utm_campaign:
            parts.append(self.utm_campaign)

        self.marketing_source = " | ".join(parts)

        score_map = {
            "Referral / Partner": 9,
            "Paid Search": 8,
            "Paid Social": 6,
            "Email Campaign": 5,
            "Organic Search": 5,
            "Direct Traffic": 4,
            "Other": 3
        }

        self.lead_score = score_map.get(self.attribution_channel, 3)

    # --------------------------------------------------
    # SCRIPT 3 — Auto Client Creation (After Save)
    # --------------------------------------------------

    def create_client_on_conversion(self):

        if self.lead_stage != "Converted to Deal":
            return

        existing = frappe.db.get_value(
            "Client Master",
            {"source_lead": self.name}
        )

        if existing:
            return

        client = frappe.new_doc("Client Master")

        client.client_name = self.lead_name
        client.client_type = "Company" if self.is_company else "Individual"
        client.source_lead = self.name
        client.account_status = "Onboarding"

        client.primary_email = self.email
        client.primary_phone = self.phone
        client.first_name = self.first_name
        client.last_name = self.last_name
        client.company_name = self.company_name

        client.industry = self.get("industry")
        client.region = self.get("region")
        client.account_manager = self.lead_owner
        client.source = self.lead_source

        # Primary Contact
        if self.first_name or self.last_name or self.email:
            client.append("client_contact", {
                "contact_name": f"{self.first_name or ''} {self.last_name or ''}".strip(),
                "email": self.email,
                "phone": self.phone,
                "is_primary": 1
            })

        client.insert(ignore_permissions=True)

        # Timeline logs
        self.add_comment(
            "Info",
            f"Lead converted to Client ➜ <b>{client.name}</b>"
        )

        client.add_comment(
            "Info",
            f"Created from Lead ➜ <b>{self.name}</b>"
        )

        self.client_created = client.name
        frappe.msgprint("Client created with primary contact ✔")
    

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
ALLOWED_TRANSITIONS = {
    "New": [
        "Not Contacted",
        "Contacted",
        "Prospecting",
        "Quotation Sent"
    ],
    "Not Contacted": [
        "Contacted",
        "Prospecting",
        "Quotation Sent"
    ],
    "Contacted": [
        "Prospecting",
        "Quotation Sent"
    ],
    "Prospecting": [
        "Quotation Sent"
    ],
    "Quotation Sent": [
        "Follow Up",
        "Converted to Deal"
    ],
    "Follow Up": [
        "Converted to Deal"
    ]
}
BACKWARD_RULES = {
    "Quotation Sent": "Prospecting",
}


def get_previous_stage(current_stage):
    if current_stage not in VALID_FLOW:
        return None
    idx = VALID_FLOW.index(current_stage)
    return VALID_FLOW[idx - 1] if idx > 0 else None


def is_valid_stage_change(old, new, context=None):
    if not old or not new:
        return True

    # backward allowed only on rejection
    if context == "rejected" and BACKWARD_RULES.get(old) == new:
        return True

    allowed = ALLOWED_TRANSITIONS.get(old, [])
    return new in allowed




# def is_valid_stage_change(old, new, context=None):
#     # Forward only (step-by-step)
#     if (
#         new in VALID_FLOW
#         and old in VALID_FLOW
#         and VALID_FLOW.index(new) == VALID_FLOW.index(old) + 1
#     ):
#         return True

#     # Backward allowed only on rejection
#     if context == "rejected" and BACKWARD_RULES.get(old) == new:
#         return True

#     return False


# =========================================================
#  CALL LOG PREFILL
# =========================================================
def onload(doc):
    doc.set_onload("make_call_log_args", {
        "linked_lead": doc.name
    })

    
