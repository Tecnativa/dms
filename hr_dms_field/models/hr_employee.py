# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model_create_multi
    def create(self, vals_list):
        """Create a directory when creating the employee."""
        res = super().create(vals_list)
        storage = self.env["dms.storage"]._get_storage_from_dms_file(self._name)
        if not storage:
            return res
        for item in res:
            storage.with_context(
                res_model=self._name, res_id=item.id
            ).create_directory_from_dms_file()
        return res
