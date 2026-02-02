// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

// frappe.ui.form.on("CRM Lead", {
// 	refresh(frm) {

// 	},
// });
/* ============================================================
   CRM LEAD — CLIENT SCRIPT (MERGED)
   ============================================================ */

/* ---------------- TAB VISIBILITY HELPERS ---------------- */

function hide_tabs_from_ui(frm) {
    const tabs = ["Call Logs", "Prospecting", "Quotations"];

    if (!frm.page || !frm.page.tabs) return;

    setTimeout(() => {
        tabs.forEach(tab => {
            try {
                frm.page.tabs
                    .find(`a:contains("${tab}")`)
                    .parent()
                    .hide();
            } catch (e) {
                // silent fail
            }
        });
    }, 0);
}

function show_tabs_in_ui(frm) {
    const tabs = ["Call Logs", "Prospecting", "Quotations"];

    if (!frm.page || !frm.page.tabs) return;

    setTimeout(() => {
        tabs.forEach(tab => {
            try {
                frm.page.tabs
                    .find(`a:contains("${tab}")`)
                    .parent()
                    .show();
            } catch (e) {
                // silent fail
            }
        });
    }, 0);
}

/* ---------------- MAIN CRM LEAD SCRIPT ---------------- */

frappe.ui.form.on("CRM Lead", {

    onload(frm) {
        if (frm.is_new()) {
            hide_tabs_from_ui(frm);
        }
    },

    validate(frm) {
        if (!frm.doc.contact_no) return;

        const value = frm.doc.contact_no.trim();
        const regex = /^[+]?[\d\s-]{7,15}$/;

        if (!regex.test(value)) {
            frappe.throw(
                __("Please enter a valid contact number (7–15 digits, + allowed)")
            );
        }
    },

    refresh(frm) {

        // company toggle
        frm.toggle_display("company_name", frm.doc.is_company);

        const advanced_fields = [
            "utm_source", "utm_medium", "utm_campaign",
            "sla_priority", "expected_response_time",
            "next_follow_up_date", "lead_score",
            "lead_health", "lead_status",
            "organization", "job_title", "website",
            "attribution_channel", "marketing_source",
            "inactivity_flag", "response_delay_risk",
            "inactivity_status", "last_follow_up",
            "has_client_created", "has_deal_created"
        ];

        if (frm.is_new()) {
            advanced_fields.forEach(f =>
                frm.set_df_property(f, "hidden", 1)
            );
            hide_tabs_from_ui(frm);
            return;
        }

        // After save
        advanced_fields.forEach(f =>
            frm.set_df_property(f, "hidden", 0)
        );
        show_tabs_in_ui(frm);

        // Go To Client
        frm.add_custom_button("Go To Client", () => {
            frappe.db.get_list("Client Master", {
                filters: { source_lead: frm.doc.name },
                fields: ["name"],
                limit: 1
            }).then(res => {
                if (res.length) {
                    frappe.set_route("Form", "Client Master", res[0].name);
                } else {
                    frappe.msgprint("No Client found for this Lead");
                }
            });
        }, "Actions");

        // Go To Deal
        frm.add_custom_button("Go To Deal", () => {
            frappe.db.get_list("CRM Deal", {
                filters: { source_lead: frm.doc.name },
                fields: ["name"],
                limit: 1
            }).then(res => {
                if (res.length) {
                    frappe.set_route("Form", "CRM Deal", res[0].name);
                } else {
                    frappe.msgprint("No Deal found for this Lead");
                }
            });
        }, "Actions");

        if (frm.doc.lead_stage === "Converted to Deal") {
            frm.set_df_property("lead_stage", "read_only", 1);
        }

        render_call_logs(frm);
        render_prospecting(frm);
        render_quotations(frm);
    },

    is_company(frm) {
        frm.toggle_display("company_name", frm.doc.is_company);
    },

    first_name(frm) {
        set_full_name(frm);
    },

    last_name(frm) {
        set_full_name(frm);
    }
});

/* ---------------- FULL NAME BUILDER ---------------- */

function set_full_name(frm) {
    let full = frm.doc.first_name || "";
    if (frm.doc.last_name) full += " " + frm.doc.last_name;
    frm.set_value("lead_name", full.trim());
}

/* ================= CALL LOGS ================= */

function render_call_logs(frm) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Call Log Go-To",
            filters: { linked_lead: frm.doc.name },
            fields: ["name", "call_type", "creation"],
            order_by: "creation desc"
        },
        callback(r) {
            const rows = r.message || [];

            let html = `
                <button class="btn btn-sm btn-dark mb-3"
                    onclick="frappe.new_doc('Call Log Go-To', { linked_lead: '${frm.doc.name}' })">
                    + Add Call Log
                </button>
            `;

            if (!rows.length) {
                html += `<p class="text-muted">No call logs yet.</p>`;
            }

            rows.forEach(d => {
                let badge = "secondary";
                if (d.call_type === "Incoming") badge = "success";
                if (d.call_type === "Outgoing") badge = "info";

                html += `
                    <div class="crm-card"
                        onclick="frappe.set_route('Form','Call Log Go-To','${d.name}')">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <div class="crm-title">${d.name}</div>
                                <div class="crm-sub">
                                    ${frappe.datetime.str_to_user(d.creation)}
                                </div>
                            </div>
                            <div class="crm-badge ${badge}">
                                ${d.call_type || "Unknown"}
                            </div>
                        </div>
                    </div>
                `;
            });

            frm.fields_dict.call_logs_html.$wrapper.html(html);
        }
    });
}

/* ================= PROSPECTING ================= */

function render_prospecting(frm) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Prospecting",
            filters: { lead: frm.doc.name },
            fields: ["name", "status", "is_latest", "revision_no", "creation"],
            order_by: "revision_no desc"
        },
        callback(r) {
            const rows = r.message || [];

            let html = `
                <button class="btn btn-sm btn-dark mb-3"
                    onclick="frappe.new_doc('Prospecting', { lead: '${frm.doc.name}' })">
                    + Create Prospecting
                </button>
            `;

            if (!rows.length) {
                html += `<p class="text-muted">No prospecting created.</p>`;
            }

            rows.forEach(d => {
                html += `
                    <div class="crm-card"
                        style="${d.is_latest ? 'border-left:4px solid #22c55e;' : ''}"
                        onclick="frappe.set_route('Form','Prospecting','${d.name}')">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <div class="crm-title">${d.name}</div>
                                <div class="crm-sub">
                                    Revision ${d.revision_no} • ${frappe.datetime.str_to_user(d.creation)}
                                </div>
                            </div>
                            <div class="crm-badge ${d.is_latest ? 'success' : 'info'}">
                                ${d.is_latest ? "Latest" : "History"}
                            </div>
                        </div>
                        <div class="mt-2 crm-sub">
                            Status: <b>${d.status || "Draft"}</b>
                        </div>
                    </div>
                `;
            });

            frm.fields_dict.prospecting_html.$wrapper.html(html);
        }
    });
}

/* ================= QUOTATIONS ================= */

function render_quotations(frm) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "CRM Quotation",
            filters: { lead: frm.doc.name },
            fields: ["name", "estimated_value", "workflow_state", "creation"],
            order_by: "creation desc"
        },
        callback(r) {
            const rows = r.message || [];

            let html = `
                <button class="btn btn-sm btn-dark mb-3"
                    onclick="frappe.new_doc('CRM Quotation', { lead: '${frm.doc.name}' })">
                    + Create Quotation
                </button>
            `;

            if (!rows.length) {
                html += `<p class="text-muted">No quotations yet.</p>`;
            }

            rows.forEach(d => {
                html += `
                    <div class="crm-card"
                        onclick="frappe.set_route('Form','CRM Quotation','${d.name}')">
                        <div class="d-flex justify-content-between">
                            <div>
                                <div class="crm-title">${d.name}</div>
                                <div class="crm-sub">${frappe.datetime.str_to_user(d.creation)}</div>
                            </div>
                            <div class="crm-badge warning">
                                ₹ ${d.estimated_value || 0}
                            </div>
                        </div>
                        <div class="mt-2 crm-sub">
                            Status: <b>${d.workflow_state || "-"}</b>
                        </div>
                    </div>
                `;
            });

            frm.fields_dict.quotations_html.$wrapper.html(html);
        }
    });
}

/* ============================================================
   LEAD INTERACTION LOG — SAME FILE
   ============================================================ */

frappe.ui.form.on("Lead Interaction Log", {
    notes(frm) {
        frm.set_value("last_follow_up", frappe.datetime.now_datetime());

        if (!frm.doc.next_follow_up) {
            frm.set_value(
                "next_follow_up",
                frappe.datetime.add_days(frappe.datetime.now_date(), 2)
            );
        }
    }
});
