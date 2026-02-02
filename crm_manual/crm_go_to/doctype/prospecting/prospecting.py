# # Copyright (c) 2026, CRM and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class Prospecting(Document):
#     def before_save(self):
#         # Allow system revision saves
#         if frappe.flags.in_prospecting_revision:
#             return

#         # Block normal overwrite
#         if not self.is_new():
#             frappe.throw(
#                 "Direct editing is not allowed. Please use 'Revise Prospecting' to create a new version."
#             )

# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class Prospecting(Document):

    def before_save(self):
        # ✅ Allow system revision saves
        if frappe.flags.in_prospecting_revision:
            return

        # ❌ Block normal overwrite
        if not self.is_new():
            frappe.throw(
                "Direct editing is not allowed. Please use 'Revise Prospecting' to create a new version."
            )

    def after_insert(self):
        """
        🔁 On FIRST Prospecting creation:
        → Move Lead stage to 'Prospecting'
        """
        if self.lead:
            reset_lead_inactivity(self.lead)
        if not self.lead:
            return

        # Get current lead stage safely
        current_stage = frappe.db.get_value(
            "CRM Lead",
            self.lead,
            "lead_stage"
        )

        # Update only if not already ahead
        if current_stage in ("New", "Contacted"):
            frappe.db.set_value(
                "CRM Lead",
                self.lead,
                {
                    "lead_stage": "Prospecting"
                }
            )

            # 🧾 ISO audit comment
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "CRM Lead",
                "reference_name": self.lead,
                "content": (
                    f"Lead moved to <b>Prospecting</b> stage "
                    f"on creation of Prospecting <b>{self.name}</b>."
                )
            }).insert(ignore_permissions=True)

def reset_lead_inactivity(lead_name):
    frappe.db.set_value(
        "CRM Lead",
        lead_name,
        {
            "inactivity_flag": 0,
            "last_activity_on": now_datetime()
        }
    ) 