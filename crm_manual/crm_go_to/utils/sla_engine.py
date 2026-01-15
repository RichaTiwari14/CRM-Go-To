import frappe
from frappe.utils import now_datetime, time_diff_in_seconds

TEST_TAT_SECONDS = 120  # 👈 2 minutes for testing


def check_lead_sla():
    leads = frappe.get_all(
        "CRM Lead",
        filters={
            "lead_stage": "New",
            "lead_stage_entered_on": ["is", "set"]
        },
        fields=["name", "lead_stage_entered_on"]
    )

    now = now_datetime()

    for l in leads:
        elapsed = time_diff_in_seconds(now, l.lead_stage_entered_on)

        if elapsed >= TEST_TAT_SECONDS:
            mark_lead_not_contacted(l.name)


def mark_lead_not_contacted(lead_name):
    # 🔒 Prevent recursion & validation loops
    frappe.flags.in_sla_automation = True

    frappe.db.set_value(
        "CRM Lead",
        lead_name,
        {
            "lead_stage": "Not Contacted",
            "inactivity_flag": 1,
            "inactivity_status": "Auto Marked - SLA Breach",
            "response_delay_risk": 3,
            "stage_action": "sla"
        },
        update_modified=False   # 🔥 IMPORTANT
    )

    frappe.db.commit()  # 🔥 RELEASE LOCK IMMEDIATELY

    # ISO audit comment
    frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Info",
        "reference_doctype": "CRM Lead",
        "reference_name": lead_name,
        "content": (
            "SLA Breach: No activity within TAT.<br>"
            "Stage auto-moved to <b>Not Contacted</b>."
        )
    }).insert(ignore_permissions=True)
