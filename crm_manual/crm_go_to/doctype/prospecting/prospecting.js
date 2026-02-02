// Copyright (c) 2026, CRM and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Prospecting", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Prospecting", {
    refresh(frm) {

        /* ---------- REVISION HISTORY ---------- */
        if (frm.doc.lead && frm.fields_dict.revision_history) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Prospecting",
                    filters: { lead: frm.doc.lead },
                    fields: ["name", "revision_no", "is_latest"],
                    order_by: "revision_no desc"
                },
                callback(r) {
                    let html = "<ul class='list-unstyled'>";
                    (r.message || []).forEach(p => {
                        html += `
                            <li style="margin-bottom:4px">
                              <a href="/app/prospecting/${p.name}">
                                Revision ${p.revision_no || 0}
                                ${p.is_latest ? "<b>(Latest)</b>" : ""}
                              </a>
                            </li>`;
                    });
                    html += "</ul>";
                    frm.fields_dict.revision_history.$wrapper.html(html);
                }
            });
        }

        /* ---------- REVISE BUTTON (ONLY FOR LATEST) ---------- */
        if (!frm.is_new() && frm.doc.is_latest) {
            frm.add_custom_button(
                "Revise Prospecting",
                () => {
                    frappe.call({
                        method: "crm_manual.crm_go_to.doctype.prospecting.api.revise_prospecting",
                        args: { prospect: frm.doc.name },
                        callback(r) {
                            if (r.message) {
                                frappe.set_route("Form", "Prospecting", r.message);
                            }
                        }
                    });
                },
                "Actions"
            );
        }

        /* ---------- OLD VERSIONS READ-ONLY UX ---------- */
        if (!frm.is_new() && !frm.doc.is_latest) {
            frm.disable_save();
            frm.set_intro(
                "This is an old revision. You cannot edit it.",
                "orange"
            );
        }
    }
});
