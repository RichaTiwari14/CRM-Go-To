# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Prospecting(Document):
    def before_save(self):
        # Allow system revision saves
        if frappe.flags.in_prospecting_revision:
            return

        # Block normal overwrite
        if not self.is_new():
            frappe.throw(
                "Direct editing is not allowed. Please use 'Revise Prospecting' to create a new version."
            )

