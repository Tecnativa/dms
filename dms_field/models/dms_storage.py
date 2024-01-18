# Copyright 2020 Creu Blanca
# Copyright 2024 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class DmsStorage(models.Model):
    _inherit = "dms.storage"

    @api.model
    def _build_documents_storage(self, storage):
        storage_directories = []
        model = self.env["dms.directory"]
        directories = model.search_parents([["storage_id", "=", storage.id]])
        for record in directories:
            storage_directories.append(model._build_documents_view_directory(record))
        return {
            "id": "storage_%s" % storage.id,
            "text": storage.name,
            "icon": "fa fa-database",
            "type": "storage",
            "data": {"odoo_id": storage.id, "odoo_model": "dms.storage"},
            "children": storage_directories,
        }

    @api.model
    def get_js_tree_data(self):
        return [record._build_documents_storage(record) for record in self.search([])]

    @api.constrains("model_ids", "save_type")
    def _constrain_model_ids(self):
        for storage in self:
            if storage.save_type == "attachment":
                continue
            if self.env["dms.directory"].search(
                [
                    ("storage_id", "=", storage.id),
                    ("is_template", "=", False),
                    ("is_root_directory", "=", True),
                    (
                        "res_model",
                        "not in",
                        storage.mapped("model_ids.model"),
                    ),
                ]
            ):
                raise ValidationError(
                    _("Some directories are inconsistent with the storage models")
                )
            if storage.model_ids and self.env["dms.directory"].search(
                [
                    ("storage_id", "=", storage.id),
                    ("is_template", "=", False),
                    ("is_root_directory", "=", True),
                    ("res_model", "=", False),
                ]
            ):
                raise ValidationError(
                    _("There are directories not associated to a record")
                )

    def _get_storage_from_dms_file(self, model):
        return self.env["dms.storage"].search(
            [
                ("model_ids.model", "=", model),
                ("save_type", "!=", "attachment"),
            ],
            limit=1,
        )

    def _get_template_from_res_model(self, res_model):
        self.ensure_one()
        return self.env["dms.directory"].search(
            [
                ("storage_id", "=", self.id),
                ("is_root_directory", "=", True),
                ("is_template", "=", True),
                ("res_model", "=", res_model),
            ],
            limit=1,
        )

    @api.model
    def create_directory_from_dms_file(self):
        """According to the model and the planned storage, we create the directory
        linked to that record and the subdirectories."""
        res_model = self.env.context.get("res_model")
        res_id = self.env.context.get("res_id")
        storage = self._get_storage_from_dms_file(res_model)
        if not storage:
            raise ValidationError(_("There is no storage linked to this model"))
        directory_model = self.env["dms.directory"]
        total_directories = directory_model.search_count(
            [
                ("is_root_directory", "=", True),
                ("res_model", "=", res_model),
                ("res_id", "=", res_id),
            ]
        )
        if total_directories > 0:
            raise ValidationError(_("There is already a linked directory created."))
        template_directory = storage._get_template_from_res_model(res_model)
        if not template_directory:
            raise ValidationError(_("There are no defined directory templates."))
        directory = directory_model.create(
            storage._prepare_directory_vals_from_dms_file(template_directory, res_id)
        )
        for child_directory in template_directory.child_directory_ids:
            directory_model.create(
                {
                    "name": child_directory.name,
                    "is_root_directory": False,
                    "parent_id": directory.id,
                }
            )
        return directory

    def _prepare_directory_vals_from_dms_file(self, directory, res_id):
        record = self.env[directory.res_model].browse(res_id)
        return {
            "storage_id": self.id,
            "res_id": res_id,
            "res_model": directory.res_model,
            "is_root_directory": directory.is_root_directory,
            # Set a unique directory name to avoid _check_name() contrain
            "name": "%s (%s)" % (record._description, record.display_name),
            "group_ids": directory.group_ids.ids,
        }
