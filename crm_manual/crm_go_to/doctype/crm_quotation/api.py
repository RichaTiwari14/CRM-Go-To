import frappe

@frappe.whitelist()
def get_quotations_for_lead(lead):
    return frappe.get_all(
        "CRM Quotation",
        filters={"lead": lead},
        fields=[
            "name",
            "docstatus",
            "creation",
            "grand_total"   # ✅ allowed server-side
        ],
        order_by="creation desc"
    )
