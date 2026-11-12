# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# Standard Library
import json
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile

# Django
from django.core.management import load_command_class

# wger
from wger.core.tests.base_testcase import WgerTestCase


class ImportUsdaProductsCharacterizationTestCase(WgerTestCase):
    dataset_name = 'fixture.zip'

    def valid_usda_product(self):
        return {
            'fdcId': 123456,
            'description': 'plain oats',
            'foodNutrients': [
                {'nutrient': {'id': 1008, 'unitName': 'kcal'}, 'amount': 370},
                {'nutrient': {'id': 1003, 'unitName': 'g'}, 'amount': 13},
                {'nutrient': {'id': 1005, 'unitName': 'g'}, 'amount': 67},
                {'nutrient': {'id': 1004, 'unitName': 'g'}, 'amount': 7},
            ],
        }

    def make_archive(self, folder, contents):
        archive_path = f'{folder}/{self.dataset_name}'
        with ZipFile(archive_path, 'w') as archive:
            if contents is not None:
                archive.writestr('foods.json', contents)
        return archive_path

    def run_import(self, folder, output):
        command = load_command_class('wger.nutrition', 'import-usda-products')
        command.stdout = output
        command.handle(dataset=self.dataset_name, folder=folder, mode='update')
        return command

    def test_import_when_archive_has_valid_product_passes_extracted_ingredient_to_processor(self):
        with TemporaryDirectory() as folder:
            self.make_archive(folder, json.dumps(self.valid_usda_product()))
            output = StringIO()
            command = load_command_class('wger.nutrition', 'import-usda-products')
            command.stdout = output

            with patch.object(command, 'process_ingredient') as process_ingredient:
                command.handle(dataset=self.dataset_name, folder=folder, mode='update')

        ingredient_data = process_ingredient.call_args.args[0]
        self.assertEqual(ingredient_data.remote_id, '123456')
        self.assertEqual(ingredient_data.name, 'Plain Oats')
        self.assertEqual(ingredient_data.energy, 370)
        self.assertIn('Finished!', output.getvalue())

    def test_import_when_archive_is_empty_raises_no_files_error(self):
        with TemporaryDirectory() as folder:
            self.make_archive(folder, None)

            with self.assertRaisesRegex(Exception, 'No files found in the ZIP archive'):
                self.run_import(folder, StringIO())

    def test_import_when_records_are_malformed_or_incomplete_skips_them_and_continues(self):
        contents = '\n'.join(['not json', '{}', json.dumps(self.valid_usda_product())])
        with TemporaryDirectory() as folder:
            self.make_archive(folder, contents)
            output = StringIO()
            command = load_command_class('wger.nutrition', 'import-usda-products')
            command.stdout = output

            with patch.object(command, 'process_ingredient') as process_ingredient:
                command.handle(dataset=self.dataset_name, folder=folder, mode='update')

        self.assertEqual(process_ingredient.call_count, 1)
        self.assertIn('Error while decoding JSON', output.getvalue())
        self.assertIn('KeyError while extracting ingredient info', output.getvalue())
        self.assertIn("Counter({'skipped': 1})", output.getvalue())
