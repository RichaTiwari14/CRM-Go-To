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
            "estimated_value"   # ✅ allowed server-side
        ],
        order_by="creation desc"
    )


@frappe.whitelist()
def revise_quotation(quotation):
    old = frappe.get_doc("CRM Quotation", quotation)

    if old.workflow_state != "Rejected":
        frappe.throw("Only rejected quotations can be revised")

    # mark old as not latest
    old.is_latest = 0
    old.save(ignore_permissions=True)

    # create new revision
    new = frappe.copy_doc(old)
    new.name = None
    new.revision_count = (old.revision_count or 1) + 1
    new.is_latest = 1
    new.amended_from = old.name
    new.workflow_state = "Draft"
    new.status = "Draft"

    new.insert(ignore_permissions=True)

    return new.name
