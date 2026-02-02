import frappe
from frappe.utils import now_datetime, get_datetime


SLA_DAYS = 3

FOLLOW_UP_STAGE = "Follow Up"

TRACKED_STAGES = [
    "Contacted",
    "Prospecting",
    "Quotation Sent"
]


def test_mark_not_contacted_1_min():
    leads = frappe.get_all(
        "CRM Lead",
        filters={"lead_stage": "New"},
        fields=["name", "lead_stage_entered_on", "owner"]
    )

    for lead in leads:
        if not lead.lead_stage_entered_on:
            continue

        diff_minutes = (
            now_datetime() - get_datetime(lead.lead_stage_entered_on)
        ).total_seconds() / 60

        if diff_minutes >= 4320:  #72 hours
            frappe.db.set_value(
                "CRM Lead",
                lead.name,
                {
                    "lead_stage": "Not Contacted",
                    "inactivity_flag": 1
                }
            )

            # 🔔 System Notification
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": "Lead Inactive (Test Mode). Marked as Not Contacted",
                "type": "Alert",
                "for_user": lead.owner,
                "document_type": "CRM Lead",
                "document_name": lead.name
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def sla_stage_followup_engine():
    leads = frappe.get_all(
        "CRM Lead",
        filters={
            "lead_stage": ["in", TRACKED_STAGES],
            "docstatus": 0
        },
        fields=[
            "name",
            "lead_stage",
            "last_activity_on",
            "owner"
        ]
    )

    for lead in leads:
        if not lead.last_activity_on:
            continue

        inactive_days = (
            now_datetime() - get_datetime(lead.last_activity_on)
        ).days

        if inactive_days >= SLA_DAYS:
            frappe.db.set_value(
                "CRM Lead",
                lead.name,
                {
                    "lead_stage": FOLLOW_UP_STAGE,
                    "inactivity_flag": 1
                }
            )

            # 🔔 System Notification
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"Lead moved to Follow Up due to inactivity",
                "type": "Alert",
                "for_user": lead.owner,
                "document_type": "CRM Lead",
                "document_name": lead.name
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def update_lead_inactivity_status():
    today = get_datetime(now_datetime())

    leads = frappe.get_all(
        "CRM Lead",
        filters={"status": "Open"},
        fields=[
            "name",
            "lead_owner",
            "last_follow_up",
            "next_follow_up"
        ]
    )

    for l in leads:
        last = get_datetime(l.last_follow_up) if l.last_follow_up else None
        next_due = get_datetime(l.next_follow_up) if l.next_follow_up else None

        # No follow-up yet → Idle
        if not last:
            frappe.db.set_value(
                "CRM Lead", l.name, "inactivity_status", "Idle"
            )
            continue

        # Overdue → At-Risk
        if next_due and next_due < today:
            frappe.db.set_value(
                "CRM Lead", l.name, "inactivity_status", "At-Risk"
            )

            if l.lead_owner:
                frappe.sendmail(
                    recipients=l.lead_owner,
                    subject="⚠ Lead Follow-up Overdue",
                    message=(
                        f"Lead <b>{l.name}</b> follow-up is overdue. "
                        "Please take action."
                    )
                )

        # Otherwise → Active
        else:
            frappe.db.set_value(
                "CRM Lead", l.name, "inactivity_status", "Active"
            )


def send_sla_breach_alerts():
    leads = frappe.get_all(
        "CRM Lead",
        filters={
            "response_delay_risk": 1,
            "status": "Open"
        },
        fields=[
            "name",
            "lead_owner",
            "expected_response_time"
        ]
    )

    for l in leads:
        if not l.lead_owner:
            continue

        frappe.sendmail(
            recipients=l.lead_owner,
            subject="⚠ SLA Breach Risk — Lead Reminder",
            message=f"""
                Lead <b>{l.name}</b> is approaching SLA breach.<br>
                Expected Response: <b>{l.expected_response_time}</b><br>
                Please take action now.
            """
        )