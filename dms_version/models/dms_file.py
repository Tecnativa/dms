# Copyright 2017-2020 MuK IT GmbH
# Copyright 2021 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class DmsFile(models.Model):
    _inherit = "dms.file"

    version_ids = fields.One2many(
        comodel_name="dms.version",
        inverse_name="file_id",
        string="Versions",
        readonly=True,
    )
    count_versions = fields.Integer(
        compute="_compute_count_versions", string="Count Versions"
    )

    def action_revert_version(self):
        for record in self:
            versions = self.env["dms.version"].sudo()
            content_tuple = versions.pop_version(record)
            record.with_context(dms_versioning=True).write(
                {"content": content_tuple[1], "name": content_tuple[0]}
            )

    def action_delete_versions(self):
        self.mapped("version_ids").sudo().unlink()

    @api.depends("version_ids")
    def _compute_count_versions(self):
        for record in self:
            record.count_versions = len(record.version_ids)

    def write(self, vals):
        if "content" in vals and not self.env.context.get("dms_versioning"):
            for record in self.filtered("storage_id.has_versioning"):
                if not record.require_migration:
                    versions = self.env["dms.version"].sudo()
                    versions.add_version(record, record.content)
                    if record.storage_id.clean_versions == "immediately":
                        versions.clean_versions(record.sudo())
        return super().write(vals)
