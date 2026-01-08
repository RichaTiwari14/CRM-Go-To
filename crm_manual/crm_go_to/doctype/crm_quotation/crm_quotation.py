# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document

class CRMQuotation(Document):

    def on_update(self):

        # ---- When quotation gets APPROVED ----
        if self.workflow_state == "Approved":
            self.handle_approval_routing()

        # ---- When quotation is REJECTED ----
        if self.workflow_state == "Rejected":
            self.handle_rejection_routing()


    def handle_approval_routing(self):

        # Update Lead Stage → Converted to Deal
        frappe.db.set_value(
            "CRM Lead",
            self.lead,
            "lead_stage",
            "Converted to Deal"
        )

        # Trigger existing client creation pipeline
        frappe.enqueue(
            "crm_manual.api.lead_to_client.convert_lead_to_client",
            lead_id=self.lead,
            quotation=self.name
        )

        frappe.msgprint("Quotation Approved ✔ Lead moved to Deal & Client Conversion triggered")


    def handle_rejection_routing(self):

        # Send lead back to Prospecting
        frappe.db.set_value(
            "CRM Lead",
            self.lead,
            "lead_stage",
            "Prospecting"
        )

        # Increment revision count
        self.revision_count = (self.revision_count or 0) + 1

        frappe.msgprint("Quotation Rejected ❌ Returned to Prospecting for revision")

