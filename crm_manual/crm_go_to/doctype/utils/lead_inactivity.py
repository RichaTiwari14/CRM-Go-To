import frappe
from frappe.utils import now_datetime, get_datetime


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
