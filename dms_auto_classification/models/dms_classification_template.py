# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VihotecOperationReason(models.Model):
    _name = "dms.classification.template"
    _order = "sequence, name"
    _description = "Dms Classification Template"

    name = fields.Char(required=True)
    sequence = fields.Integer(required=True, default=10)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        store=True,
        index=True,
        default=lambda self: self.env.company.id,
        required=True,
    )
    filename_pattern = fields.Char()
    directory_pattern = fields.Char()
