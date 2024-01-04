# Copyright 2024 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, models


class DmsStorage(models.Model):
    _inherit = "dms.storage"

    def _prepare_directory_vals_from_dms_file(self, directory, res_id):
        """If hr.employee, create a copy of the corresponding access group and add the
        employee's user."""
        vals = super()._prepare_directory_vals_from_dms_file(
            directory=directory, res_id=res_id
        )
        if directory.res_model != "hr.employee":
            return vals
        employee = self.env[directory.res_model].browse(res_id)
        groups = self.env["dms.access.group"]
        for group in directory.group_ids:
            group_name = _("Autogenerate group from %(model)s (%(name)s)") % {
                "model": employee._description,
                "name": employee.display_name,
            }
            new_group = group.copy({"name": group_name, "directory_ids": False})
            if employee.user_id:
                new_group.write({"explicit_user_ids": [(4, employee.user_id.id)]})
            groups += new_group
        vals.update({"group_ids": groups.ids})
        return vals
