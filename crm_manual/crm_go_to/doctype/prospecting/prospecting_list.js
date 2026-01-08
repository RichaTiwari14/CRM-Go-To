frappe.listview_settings["Prospecting"] = {

    onload(listview) {

        listview.page.add_inner_button("Show Only Latest", () => {
            listview.filter_area.add([
                ["Prospecting", "is_latest", "=", 1]
            ]);
        });
    },

    button: {
        show(listview, doc) {
            return doc.docstatus === 0 && doc.is_latest === 1;
        },

        get_label() {
            return __("Revise");
        },

        get_description(doc) {
            return __("Create next revision of this prospect");
        },

        action(listview, doc) {
            frappe.call({
                method: "crm_manual.crm_go_to.doctype.prospecting.api.revise_prospecting",
                args: { prospect: doc.name },
                callback(r) {
                    if (!r.exc) {
                        frappe.show_alert("Revision created");
                        frappe.set_route("Form", "Prospecting", r.message);
                    }
                }
            });
        }
    }
};
