# Copyright 2017-2020 MuK IT GmbH
# Copyright 2021 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.dms.tests.common import multi_users
from odoo.addons.dms.tests.test_storage import StorageLObjectTestCase


class StorageVersionTestCase(StorageLObjectTestCase):
    def setUp(self):
        super().setUp()
        self.version = self.env["dms.version"]

    @multi_users(
        lambda self: [[self.super_uid, True], [self.admin_uid, True]],
        callback="_setup_test_data",
    )
    def test_version_clean_write(self):
        storage = self.create_storage(sudo=True)
        storage.write(
            {
                "has_versioning": True,
                "clean_versions": "immediately",
                "stored_versions": 3,
            }
        )
        dms_file = self.create_file(storage=storage)
        for _ in range(5):
            dms_file.write({"content": self.content_base64()})
        self.assertEqual(len(dms_file.version_ids.ids), 3)
        self.assertEqual(dms_file.count_versions, 3)

    @multi_users(
        lambda self: [[self.super_uid, True], [self.admin_uid, True]],
        callback="_setup_test_data",
    )
    def test_version_clean_autovacuum(self):
        storage = self.create_storage(sudo=True)
        storage.write(
            {
                "has_versioning": True,
                "clean_versions": "autovacuum",
                "stored_versions": 3,
            }
        )
        dms_file = self.create_file(storage=storage)
        for _ in range(5):
            dms_file.write({"content": self.content_base64()})
        self.assertEqual(len(dms_file.version_ids.ids), 5)
        self.assertEqual(dms_file.count_versions, 5)
        storage.clean_file_versions()
        self.assertEqual(len(dms_file.version_ids.ids), 3)
        self.assertEqual(dms_file.count_versions, 3)

    @multi_users(
        lambda self: [[self.super_uid, True], [self.admin_uid, True]],
        callback="_setup_test_data",
    )
    def test_version_compress(self):
        storage = self.create_storage(sudo=True)
        storage.write(
            {
                "has_versioning": True,
                "clean_versions": "immediately",
                "stored_versions": 3,
                "compress_versions": True,
            }
        )
        dms_file = self.create_file(storage=storage)
        for _ in range(5):
            dms_file.write({"content": self.content_base64()})
        self.assertEqual(len(dms_file.version_ids.ids), 3)
        self.assertTrue(all(dms_file.version_ids.mapped("is_compress")))
        self.assertEqual(dms_file.version_ids[0].content, self.content_base64())

    @multi_users(
        lambda self: [[self.super_uid, True], [self.admin_uid, True]],
        callback="_setup_test_data",
    )
    def test_version_incremental(self):
        storage = self.create_storage(sudo=True)
        storage.write({"has_versioning": True, "incremental_versions": True})
        dms_file = self.create_file(storage=storage)
        for _ in range(5):
            dms_file.write({"content": self.content_base64()})
        self.assertEqual(len(dms_file.version_ids.ids), 5)
        for version in dms_file.version_ids.exists():
            self.assertEqual(version.content, self.content_base64())

    @multi_users(
        lambda self: [[self.super_uid, True], [self.admin_uid, True]],
        callback="_setup_test_data",
    )
    def test_version_incremental_compress(self):
        storage = self.create_storage(sudo=True)
        storage.write(
            {
                "has_versioning": True,
                "compress_versions": True,
                "incremental_versions": True,
            }
        )
        dms_file = self.create_file(storage=storage)
        for _ in range(5):
            dms_file.write({"content": self.content_base64()})
        self.assertEqual(len(dms_file.version_ids.ids), 5)
        for version in dms_file.version_ids.exists():
            self.assertEqual(version.content, self.content_base64())

    @multi_users(
        lambda self: [[self.super_uid, True], [self.admin_uid, True]],
        callback="_setup_test_data",
    )
    def test_version_incremental_clean(self):
        storage = self.create_storage(sudo=True)
        storage.write({"has_versioning": True, "incremental_versions": True})
        dms_file = self.create_file(storage=storage)
        for _ in range(5):
            dms_file.write({"content": self.content_base64()})
        domain = [
            ("file_id", "=", dms_file.id),
            ("previous_version", "=", False),
        ]
        oldest_version = self.version.search(domain, limit=1)
        newer_versions = dms_file.version_ids - oldest_version
        self.assertEqual(len(dms_file.version_ids.ids), 5)
        self.assertFalse(oldest_version.is_incremental)
        self.assertTrue(all(newer_versions.mapped("is_incremental")))
        storage.clean_file_versions()
        new_oldest_version = self.version.search(domain, limit=1)
        newer_versions = dms_file.version_ids.exists() - new_oldest_version
        self.assertEqual(len(dms_file.version_ids.ids), 3)
        self.assertNotEqual(oldest_version, new_oldest_version)
        self.assertFalse(new_oldest_version.is_incremental)
        self.assertTrue(all(newer_versions.mapped("is_incremental")))

    @multi_users(
        lambda self: [[self.super_uid, True], [self.admin_uid, True]],
        callback="_setup_test_data",
    )
    def test_version_delete(self):
        storage = self.create_storage(sudo=True)
        storage.write(
            {
                "has_versioning": True,
                "clean_versions": "immediately",
                "stored_versions": 3,
            }
        )
        dms_file = self.create_file(storage=storage)
        for _ in range(5):
            dms_file.write({"content": self.content_base64()})
        storage.action_delete_file_versions()
        self.assertEqual(len(dms_file.version_ids.ids), 0)
        self.assertEqual(dms_file.count_versions, 0)
