# # crm_manual/crm_go_to/utils/raci_config.py

# LEAD_STAGE_RACI = {
#     "Not Contacted": {
#         "tat_hours": 72,
#         "responsible": "CRE",
#         "accountable": "Manager",
#     },
#     "Contacted": {
#         "tat_hours": 72,
#         "responsible": "Sales",
#         "accountable": "Manager",
#     },
#     "Prospecting": {
#         "tat_hours": 72,
#         "responsible": "Sales",
#         "accountable": "HOD",
#     },
#     "Quotation Sent": {
#         "tat_hours": 72,
#         "responsible": "Sales",
#         "accountable": "Manager",
#     },
#     "Negotiation (Maybe)": {
#         "tat_hours": 72,
#         "responsible": "Sales",
#         "accountable": "Manager",
#     }
# }

# SLA + RACI CONFIG (TEST MODE: 2 MIN)

SLA_RULES = {
    "New": {
        "tat_minutes": 2,
        "responsible": "Administrator",
        "accountable": "Manager",
        "on_breach_stage": "Not Contacted"
    },
    "Prospecting": {
        "tat_minutes": 2,
        "responsible": "Sales",
        "accountable": "HOD",
        "on_breach_stage": "Follow Up"
    },
    "Quotation Sent": {
        "tat_minutes": 2,
        "responsible": "Sales",
        "accountable": "Manager",
        "on_breach_stage": "Follow Up"
    }
}
