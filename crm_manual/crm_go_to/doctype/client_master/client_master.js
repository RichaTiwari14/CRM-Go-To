// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Client Master", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Client Master", {
    refresh(frm) {
        if (!frm.doc.name) return;
        render_quotations(frm);
        render_deals(frm);
        frm.add_custom_button(
            "New Quotation",
            () => {
                const route_opts = {
                    client: frm.doc.name
                };

                // Auto-fill Lead if linked
                if (frm.doc.source_lead) {
                    route_opts.lead = frm.doc.source_lead;
                }

                frappe.new_doc("CRM Quotation", route_opts);
            },
            "Create"
        );
        if (frm.doc.health_status === "Critical") {
            frm.dashboard.set_headline_alert(
                "Client Health Critical ⚠",
                "red"
            );
        }
        if (frm.doc.health_status === "At Risk") {
            frm.dashboard.set_headline_alert(
                "Client Needs Attention",
                "orange"
            );
        }
    }
});

function render_quotations(frm) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "CRM Quotation",
            filters: { client: frm.doc.name },
            fields: ["name", "estimated_value", "workflow_state", "creation"],
            order_by: "creation desc"
        },
        callback(r) {
            const rows = r.message || [];
            let html = "";

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

            frm.fields_dict.quotations_list.$wrapper.html(html);
        }
    });
}

function render_deals(frm) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "CRM Deal",
            filters: { client: frm.doc.name },
            fields: [
                "name",
                "expected_value",
                "deal_status",
                "creation"
            ],
            order_by: "creation desc"
        },
        callback(r) {
            const rows = r.message || [];
            let html = "";

            if (!rows.length) {
                html += `<p class="text-muted">No deals yet.</p>`;
            }

            rows.forEach(d => {
                html += `
                    <div class="crm-card"
                        onclick="frappe.set_route('Form','CRM Deal','${d.name}')">
                        <div class="d-flex justify-content-between">
                            <div>
                                <div class="crm-title">${d.name}</div>
                                <div class="crm-sub">
                                    ${frappe.datetime.str_to_user(d.creation)}
                                </div>
                            </div>
                            <div class="crm-badge success">
                                ₹ ${d.expected_value || 0}
                            </div>
                        </div>
                        <div class="mt-2 crm-sub">
                            Status: <b>${d.deal_status || "-"}</b>
                        </div>
                    </div>
                `;
            });

            frm.fields_dict.deal_list.$wrapper.html(html);
        }
    });
}
