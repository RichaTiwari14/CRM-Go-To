# import frappe
# from frappe.model.document import Document
# from frappe.utils import nowdate, now_datetime

# class CRMQuotation(Document):

#     def on_update(self):
#         if frappe.flags.in_workflow:
#             self.handle_workflow_transitions()

#     def handle_workflow_transitions(self):
#         if self.workflow_state == "Pending Approval":
#             self.on_send_for_approval()

#     def on_send_for_approval(self):

#         if self.lead:
#             reset_lead_inactivity(self.lead)
#         if not self.lead:
#             return

#         frappe.db.set_value(
#             "CRM Lead",
#             self.lead,
#             "lead_stage",
#             "Quotation Sent"
#         )

#         frappe.get_doc({
#             "doctype": "Comment",
#             "comment_type": "Info",
#             "reference_doctype": "CRM Lead",
#             "reference_name": self.lead,
#             "content": (
#                 f"Quotation <b>{self.name}</b> sent for approval.<br>"
#                 f"Workflow State: {self.workflow_state}"
#             )
#         }).insert(ignore_permissions=True)

#     # ✅ FINAL APPROVAL
#     def on_submit(self):
#         if self.workflow_state == "Approved":
#             self.on_approved()

#     def on_approved(self):
#         if not self.lead:
#             return

#         client = create_client_from_quotation(self)
#         deal = create_deal_from_quotation(self, client)  # ✅ MISSING LINE (NOW ADDED)

#         frappe.db.set_value(
#             "CRM Lead",
#             self.lead,
#             {
#                 "lead_stage": "Converted to Deal",
#                 "has_client_created": 1,
#                 "has_deal_created": 1

#             }
#         )

#     def on_cancel(self):
#         if self.lead:
#             frappe.db.set_value(
#                 "CRM Lead",
#                 self.lead,
#                 "lead_stage",
#                 "Prospecting"
#             )


# def create_client_from_quotation(quotation):
#     existing = frappe.db.get_value(
#         "Client Master",
#         {"source_lead": quotation.lead},
#         "name"
#     )
#     if existing:
#         return existing

#     lead = frappe.get_doc("CRM Lead", quotation.lead)

#     client = frappe.new_doc("Client Master")
#     client.client_name = lead.lead_name
#     client.client_type = "Company" if lead.is_company else "Individual"
#     client.source_lead = lead.name
#     client.account_manager = lead.lead_owner
#     client.primary_email = lead.email
#     client.primary_phone = lead.phone
#     client.website = lead.website
#     client.first_name = lead.first_name
#     client.last_name = lead.last_name
#     client.company_name = lead.company_name
#     client.account_status = "Active"
#     client.onboarding_stage = "Initial"
#     client.start_date = nowdate()
#     client.insert(ignore_permissions=True)

#     return client.name


# def create_deal_from_quotation(quotation, client):
#     existing = frappe.db.get_value(
#         "CRM Deal",
#         {"quotation_reference": quotation.name},
#         "name"
#     )
#     if existing:
#         return existing

#     deal = frappe.new_doc("CRM Deal")
#     deal.client = client
#     deal.source_lead = quotation.lead
#     deal.quotation_reference = quotation.name
#     deal.deal_value = quotation.grand_total
#     deal.status = "Open"
#     deal.start_date = nowdate()
#     deal.insert(ignore_permissions=True)

#     return deal.name

# def reset_lead_inactivity(lead_name):
#     frappe.db.set_value(
#         "CRM Lead",
#         lead_name,
#         {
#             "inactivity_flag": 0,
#             "last_activity_on": now_datetime()
#         }
#     ) 

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, now_datetime


class CRMQuotation(Document):

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def is_lead_based(self):
        """
        Quotation created from Lead context
        """
        return bool(self.lead and not self.client)

    def is_client_based(self):
        """
        Quotation created from Client context
        """
        return bool(self.client)

    # --------------------------------------------------
    # WORKFLOW HANDLING
    # --------------------------------------------------

    def on_update(self):
        if frappe.flags.in_workflow:
            self.handle_workflow_transitions()

    def handle_workflow_transitions(self):
        if self.workflow_state == "Pending Approval":
            self.on_send_for_approval()

    def on_send_for_approval(self):
        """
        Pending Approval:
        - Lead-based → update lead stage
        - Client-based → do NOTHING to lead
        """

        if not self.is_lead_based():
            return

        reset_lead_inactivity(self.lead)

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

    # --------------------------------------------------
    # FINAL APPROVAL
    # --------------------------------------------------

    def on_submit(self):
        if self.workflow_state == "Approved":
            self.on_approved()

    def on_approved(self):
        """
        Approval:
        - Lead-based → create client + deal + convert lead
        - Client-based → create deal ONLY
        """

        client = None

        # CASE 1: Lead-based quotation
        if self.is_lead_based():
            client = create_client_from_quotation(self)

            frappe.db.set_value(
                "CRM Lead",
                self.lead,
                {
                    "lead_stage": "Converted to Deal",
                    "has_client_created": 1,
                    "has_deal_created": 1
                }
            )

        # CASE 2: Client-based quotation (repeat business)
        elif self.is_client_based():
            client = self.client

        # Safety
        if not client:
            return

        # ✅ DEAL CREATION (ALWAYS)
        create_deal_from_quotation(self, client)

    # --------------------------------------------------
    # CANCEL
    # --------------------------------------------------

    def on_cancel(self):
        """
        Cancel:
        - Lead-based → rollback lead stage
        - Client-based → no lead impact
        """

        if not self.is_lead_based():
            return

        frappe.db.set_value(
            "CRM Lead",
            self.lead,
            "lead_stage",
            "Prospecting"
        )


# ======================================================
# HELPERS
# ======================================================

def create_client_from_quotation(quotation):
    """
    Create client only once per lead
    """
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
    """
    One deal per quotation (multiple quotations allowed per client)
    """
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


def reset_lead_inactivity(lead_name):
    frappe.db.set_value(
        "CRM Lead",
        lead_name,
        {
            "inactivity_flag": 0,
            "last_activity_on": now_datetime()
        }
    )
