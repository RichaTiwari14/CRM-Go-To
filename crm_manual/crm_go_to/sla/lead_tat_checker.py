import frappe
from frappe.utils import now_datetime
from datetime import timedelta
from crm_manual.crm_go_to.utils.raci_config import LEAD_STAGE_RACI


def check_lead_tat():
    leads = frappe.get_all(
        "CRM Lead",
        filters={
            "lead_stage": ["in", list(LEAD_STAGE_RACI.keys())],
            "inactivity_flag": 0
        },
        fields=[
            "name",
            "lead_stage",
            "lead_stage_entered_on",
            "lead_owner"
        ]
    )

    now = now_datetime()

    for lead in leads:
        if not lead.lead_stage_entered_on:
            continue

        rule = LEAD_STAGE_RACI.get(lead.lead_stage)
        if not rule:
            continue

        tat_limit = lead.lead_stage_entered_on + timedelta(
            hours=rule["tat_hours"]
        )

        if now > tat_limit:
            mark_lead_as_delayed(lead, rule)


# 🔴 4️⃣ AUTO ACTION AFTER TAT BREACH
def mark_lead_as_delayed(lead, rule):
    frappe.db.set_value(
        "CRM Lead",
        lead.name,
        {
            "inactivity_flag": 1,
            "inactivity_status": "Auto Marked - SLA Breach",
            "response_delay_risk": "High",
            "lead_stage": "Not Contacted"
        }
    )

    create_sla_comment(lead, rule)


# 🧾 5️⃣ SLA AUDIT COMMENT (ISO EVIDENCE)
def create_sla_comment(lead, rule):
    frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Info",
        "reference_doctype": "CRM Lead",
        "reference_name": lead.name,
        "content": (
            f"SLA breached for stage <b>{lead.lead_stage}</b><br>"
            f"TAT: {rule['tat_hours']} hrs<br>"
            f"Responsible: {rule['responsible']}<br>"
            f"Accountable: {rule['accountable']}"
        )
    }).insert(ignore_permissions=True)
