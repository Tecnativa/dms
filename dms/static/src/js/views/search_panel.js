/* Copyright 2021 Tecnativa - Víctor Martínez
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define("dms.SearchPanel", function(require) {
    "use strict";

    const core = require("web.core");
    const SearchPanel = require("web.SearchPanel");
    const _t = core._t;
    SearchPanel.include({
        _renderCategory: function() {
            var res = this._super.apply(this, arguments);
            if (this.model === "dms.directory") {
                var str_search = '<span class="o_search_panel_label_title"><b>';
                var pos_start = res.search(str_search) + str_search.length;
                var pos_end = pos_start + res.substring(pos_start).search("</b>");
                res = res.substring(0, pos_start) + _t("Root") + res.substring(pos_end);
            }
            return res;
        },
        _getCategoryDomain: function() {
            var domain = this._super.apply(this, arguments);
            var field_name_need_check = false;
            if (this.model === "dms.file") {
                field_name_need_check = "directory_id";
            } else if (this.model === "dms.directory") {
                field_name_need_check = "parent_id";
            }
            if (field_name_need_check) {
                domain.forEach(function(item, key) {
                    if (item[0] === field_name_need_check && item[1] === "child_of") {
                        domain[key] = [item[0], "=", item[2]];
                    }
                });
            }
            if (
                domain.length === 0 &&
                field_name_need_check &&
                this.model === "dms.directory"
            ) {
                domain.push([field_name_need_check, "=", false]);
            }
            return domain;
        },
    });
});
