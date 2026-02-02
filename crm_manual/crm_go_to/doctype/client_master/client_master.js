// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Client Master", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Client Master", {
    refresh(frm) {
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
