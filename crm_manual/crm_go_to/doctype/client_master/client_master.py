import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, now_datetime, date_diff, get_datetime


class ClientMaster(Document):

    def on_update(self):
        # avoid infinite loop
        if frappe.flags.in_health_calc:
            return

        frappe.flags.in_health_calc = True
        self.calculate_health()
        frappe.flags.in_health_calc = False

    def calculate_health(self):
        # --- AUTO CALCULATED SCORES ---
        communication = calculate_communication_score(self)
        engagement = calculate_engagement_score(self)
        risk = calculate_risk_score(self)

        # delivery can stay manual for now
        delivery = self.delivery_score or 80

        # set component scores
        self.communication_score = communication
        self.engagement_score = engagement
        self.risk_score = risk
        self.delivery_score = delivery

        # --- FINAL HEALTH SCORE ---
        health_score = (
            (delivery * 0.30) +
            (communication * 0.25) +
            (engagement * 0.25) -
            (risk * 0.20)
        )

        health_score = max(min(int(health_score), 100), 0)

        if health_score >= 75:
            status = "Healthy"
        elif health_score >= 40:
            status = "At Risk"
        else:
            status = "Critical"

        self.health_score = health_score
        self.health_status = status
        self.last_health_update = now_datetime()

def calculate_communication_score(client):
    last_call = frappe.db.get_value(
        "Call Log Go-To",
        {"client": client.name},
        "creation",
        order_by="creation desc"
    )

    if not last_call:
        return 10

    last_call_dt = get_datetime(last_call)
    days = date_diff(nowdate(), last_call_dt.date())

    if days <= 3:
        return 100
    elif days <= 7:
        return 70
    elif days <= 14:
        return 40
    else:
        return 10

def calculate_engagement_score(client):
    interactions = 0

    interactions += frappe.db.count(
        "Call Log Go-To",
        {"client": client.name}
    )

    interactions += frappe.db.count(
        "CRM Quotation",
        {"client": client.name}
    )

    if interactions >= 5:
        return 100
    elif interactions >= 3:
        return 70
    elif interactions >= 1:
        return 40
    return 10

def calculate_risk_score(client):
    breaches = frappe.db.count(
        "CRM Lead",
        {
            "client_created": client.name,
            "response_delay_risk": "High"
        }
    )

    if breaches >= 2:
        return 60
    elif breaches == 1:
        return 30
    return 0
