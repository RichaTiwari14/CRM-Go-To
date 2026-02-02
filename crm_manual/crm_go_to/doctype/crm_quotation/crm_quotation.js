// Copyright (c) 2026, CRM and contributors
// For license information, please see license.txt

// frappe.ui.form.on("CRM Quotation", {
// 	refresh(frm) {

// 	},
// });
/* =========================================================
   🔢 CALCULATION HELPERS (MUST BE DEFINED FIRST)
========================================================= */

function calculate_totals(frm) {
    let total_qty = 0;
    let total_amount = 0;

    (frm.doc.table_tgfh || []).forEach(row => {
        total_qty += flt(row.qty);
        total_amount += flt(row.amount);
    });

    frm.set_value("total_qty", total_qty);
    frm.set_value("total_amount", total_amount);

    const discount = flt(frm.doc.discount_amount);
    const tax = flt(frm.doc.tax_amount);

    const net_total = total_amount - discount;
    frm.set_value("net_total", net_total);
    frm.set_value("grand_total", net_total + tax);
}

function calculate_row(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    row.amount = flt(row.qty) * flt(row.rate);
    frm.refresh_field("table_tgfh");
    calculate_totals(frm);
}

function sync_status_with_docstatus(frm) {
    let status = "Draft";

    if (frm.doc.docstatus === 1) status = "Submitted";
    if (frm.doc.docstatus === 2) status = "Cancelled";

    frm.set_value("status", status);
    frm.set_df_property("status", "read_only", 1);
}


/* =========================================================
   📄 CRM QUOTATION MAIN FORM
========================================================= */

frappe.ui.form.on("CRM Quotation", {

    onload(frm) {
        sync_status_with_docstatus(frm);

        // Auto set party only for NEW quotation
        if (frm.is_new() && frm.doc.lead) {
            frm.set_value("quotation_to", "CRM Lead");
            frm.set_value("party", frm.doc.lead);
        }
    },

    refresh(frm) {
        sync_status_with_docstatus(frm);

        // 🔁 REVISION BUTTON
        if (
            !frm.is_new() &&
            frm.doc.is_latest &&
            ["Rejected", "Negotiation (Maybe)"].includes(frm.doc.workflow_state)
        ) {
            frm.add_custom_button("Revise Quotation", () => {
                frappe.call({
                    method: "crm_manual.crm_go_to.doctype.crm_quotation.api.revise_quotation",
                    args: { quotation: frm.doc.name },
                    callback(r) {
                        if (r.message) {
                            frappe.set_route("Form", "CRM Quotation", r.message);
                        }
                    }
                });
            });
        }

        calculate_totals(frm);
    },

    /* =====================================================
       🚀 SEND FOR APPROVAL → LEAD STAGE = QUOTATION SENT
       (SAFE WORKFLOW HOOK – YAHI SAHI JAGAH HAI)
    ===================================================== */
    before_workflow_action(frm) {
        if (
            frm.selected_workflow_action === "Send for Approval" &&
            frm.doc.lead
        ) {
            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: "CRM Lead",
                    name: frm.doc.lead,
                    fieldname: "lead_stage",
                    value: "Quotation Sent"
                }
            });
        }
    },

    /* =====================================================
       🎉 AFTER APPROVAL → CLIENT CREATED POPUP + REDIRECT
    ===================================================== */
    after_workflow_action(frm) {
        if (frm.doc.workflow_state === "Approved" && frm.doc.client_created) {
            frappe.msgprint({
                title: "Client Created 🎉",
                message: `Client <b>${frm.doc.client_created}</b> created successfully.`,
                indicator: "green",
                primary_action: {
                    label: "Open Client",
                    
                }
            });
        }
    },

    discount_amount: calculate_totals,
    tax_amount: calculate_totals
});


/* =========================================================
   📦 QUOTATION ITEM CHILD TABLE
========================================================= */

frappe.ui.form.on("Quotation Item", {
    qty: calculate_row,
    rate: calculate_row,
    table_tgfh_remove(frm) {
        calculate_totals(frm);
    }
});
