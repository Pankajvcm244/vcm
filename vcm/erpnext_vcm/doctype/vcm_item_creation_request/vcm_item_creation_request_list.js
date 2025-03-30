frappe.listview_settings["VCM Item Creation Request"] = {
    add_fields: ["status"],
    get_indicator: function (doc) {
      if (doc.status == "Pending") {
        return [__("Pending"), "yellow", "status,=,Pending"];
      } else if (doc.status == "Created") {
        return [__("Created"), "green", "status,=,Created"];
      } else if (doc.status == "Rejected") {
        return [__("Rejected"), "red", "status,=,Rejected"];
      }
    },
  };
  