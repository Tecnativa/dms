odoo.define("dms_widgets.size", function(require) {
    "use strict";

    var registry = require("web.field_registry");
    var field_utils = require("web.field_utils");
    var field_widgets = require("web.basic_fields");

    function format_size(bytes, field) {
        var thresh = 1024;
        if (Math.abs(bytes) < thresh) {
            return field_utils.format.float(bytes, field) + " B";
        }
        var units = ["KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
        var u = -1;
        do {
            bytes /= thresh;
            ++u;
        } while (Math.abs(bytes) >= thresh && u < units.length - 1);
        return field_utils.format.float(bytes, field) + " " + units[u];
    }

    var FieldDocumentSize = field_widgets.FieldFloat.extend({
        _renderReadonly: function() {
            this.$el.text(format_size(this.value, this.field, this.nodeOptions));
        },
    });

    registry.add("dms_size", FieldDocumentSize);

    return FieldDocumentSize;
});
