import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class CRMQuotation(Document):

    def on_update(self):
        if frappe.flags.in_workflow:
            self.handle_workflow_transitions()

    def handle_workflow_transitions(self):
        if self.workflow_state == "Pending Approval":
            self.on_send_for_approval()

    def on_send_for_approval(self):
        if not self.lead:
            return

        frappe.db.set_value(
            "CRM Lead",
            self.lead,
            "lead_stage",
            "Quotation Sent"
        )

        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "CRM Lead",
            "reference_name": self.lead,
            "content": (
                f"Quotation <b>{self.name}</b> sent for approval.<br>"
                f"Workflow State: {self.workflow_state}"
            )
        }).insert(ignore_permissions=True)

    # ✅ FINAL APPROVAL
    def on_submit(self):
        if self.workflow_state == "Approved":
            self.on_approved()

    def on_approved(self):
        if not self.lead:
            return

        client = create_client_from_quotation(self)
        deal = create_deal_from_quotation(self, client)  # ✅ MISSING LINE (NOW ADDED)

        frappe.db.set_value(
            "CRM Lead",
            self.lead,
            {
                "lead_stage": "Converted to Deal",
                "client_created": client,
                "deal_created": deal
            }
        )

    def on_cancel(self):
        if self.lead:
            frappe.db.set_value(
                "CRM Lead",
                self.lead,
                "lead_stage",
                "Prospecting"
            )


def create_client_from_quotation(quotation):
    existing = frappe.db.get_value(
        "Client Master",
        {"source_lead": quotation.lead},
        "name"
    )
    if existing:
        return existing

    lead = frappe.get_doc("CRM Lead", quotation.lead)

    client = frappe.new_doc("Client Master")
    client.client_name = lead.lead_name
    client.client_type = "Company" if lead.is_company else "Individual"
    client.source_lead = lead.name
    client.account_manager = lead.lead_owner
    client.primary_email = lead.email
    client.primary_phone = lead.phone
    client.website = lead.website
    client.first_name = lead.first_name
    client.last_name = lead.last_name
    client.company_name = lead.company_name
    client.account_status = "Active"
    client.onboarding_stage = "Initial"
    client.start_date = nowdate()
    client.insert(ignore_permissions=True)

    return client.name


def create_deal_from_quotation(quotation, client):
    existing = frappe.db.get_value(
        "CRM Deal",
        {"quotation_reference": quotation.name},
        "name"
    )
    if existing:
        return existing

    deal = frappe.new_doc("CRM Deal")
    deal.client = client
    deal.source_lead = quotation.lead
    deal.quotation_reference = quotation.name
    deal.deal_value = quotation.grand_total
    deal.status = "Open"
    deal.start_date = nowdate()
    deal.insert(ignore_permissions=True)

    return deal.name
