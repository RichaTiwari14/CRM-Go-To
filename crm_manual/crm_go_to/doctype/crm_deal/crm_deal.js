frappe.ui.form.on("CRM Deal", {
    refresh(frm) {

        // 🔹 Create Project (only if not created)
        if (!frm.doc.project_created) {
            frm.add_custom_button(
                "Create Project",
                () => {
                    frappe.call({
                        method: "crm_manual.crm_go_to.doctype.crm_deal.crm_deal.create_project_from_deal",
                        args: {
                            deal: frm.doc.name
                        },
                        callback(r) {
                            if (r.message && r.message.project) {
                                frappe.msgprint("Project created successfully");

                                // 🔁 IMPORTANT
                                frm.reload_doc();
                            }
                        }
                    });
                },
                "Actions"
            );
        }

        // 🔹 Go To Project (only after created)
        if (frm.doc.project_created && frm.doc.project) {
            frm.add_custom_button(
                "Go To Project",
                () => {
                    frappe.set_route(
                        "Form",
                        "Project Master",
                        frm.doc.project
                    );
                },
                "Actions"
            );
        }
    }
});
