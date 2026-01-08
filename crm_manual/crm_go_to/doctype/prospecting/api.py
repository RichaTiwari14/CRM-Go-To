import frappe

@frappe.whitelist()
def create_prospecting(lead):
    doc = frappe.new_doc("Prospecting")
    doc.lead = lead
    doc.prospect_name = frappe.db.get_value("CRM Lead", lead, "lead_name")
    doc.status = "In Discussion"
    doc.insert(ignore_permissions=True)
    frappe.db.set_value("CRM Lead", lead, "lead_stage", "Prospecting")
    return doc.name


@frappe.whitelist()
def revise_prospecting(prospect):
    old = frappe.get_doc("Prospecting", prospect)

    if old.docstatus == 1:
        frappe.throw("Submitted prospecting cannot be revised")

    # 🔑 Tell system this is a revision operation
    frappe.flags.in_prospecting_revision = True

    try:
        # Mark old as not latest
        old.is_latest = 0
        old.save(ignore_permissions=True)

        # Create new revision
        new = frappe.new_doc("Prospecting")
        new.update(old.as_dict())

        new.name = None
        new.docstatus = 0
        new.is_latest = 1
        new.revision_no = (old.revision_no or 0) + 1
        new.previous_prospecting = old.name

        new.insert(ignore_permissions=True)

    finally:
        # 🔑 Always clean up flag
        frappe.flags.in_prospecting_revision = False

    return new.name

