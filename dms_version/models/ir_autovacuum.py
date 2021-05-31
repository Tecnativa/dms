# Copyright 2017-2020 MuK IT GmbH
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AutoVacuum(models.AbstractModel):
    _inherit = "ir.autovacuum"

    @api.model
    def power_on(self, *args, **kwargs):
        res = super().power_on(*args, **kwargs)
        self.env["dms.storage"].clean_file_versions()
        return res
