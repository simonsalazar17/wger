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
from unittest.mock import Mock

# Django
from django.test import SimpleTestCase, override_settings

# wger
from wger.exercises.tasks import setup_periodic_tasks


class ExerciseTaskCharacterizationTestCase(SimpleTestCase):
    @override_settings(
        WGER_SETTINGS={
            'SYNC_EXERCISES_CELERY': True,
            'SYNC_EXERCISE_IMAGES_CELERY': True,
            'SYNC_EXERCISE_VIDEOS_CELERY': True,
            'CACHE_API_EXERCISES_CELERY': True,
            'CACHE_API_EXERCISES_CELERY_FORCE_UPDATE': False,
        }
    )
    def test_setup_periodic_tasks_when_all_jobs_are_enabled_registers_four_jobs(self):
        sender = Mock()

        setup_periodic_tasks(sender)

        self.assertEqual(sender.add_periodic_task.call_count, 4)
        names = [call.kwargs['name'] for call in sender.add_periodic_task.call_args_list]
        self.assertEqual(
            names,
            [
                'Sync exercises',
                'Sync exercise images',
                'Sync exercise videos',
                'Cache API exercises',
            ],
        )
        task_names = [call.args[1].task for call in sender.add_periodic_task.call_args_list]
        self.assertEqual(
            task_names,
            [
                'wger.exercises.tasks.sync_exercises_task',
                'wger.exercises.tasks.sync_images_task',
                'wger.exercises.tasks.sync_videos_task',
                'wger.exercises.tasks.cache_api_exercises_task',
            ],
        )

    @override_settings(WGER_SETTINGS={
        'SYNC_EXERCISES_CELERY': False,
        'SYNC_EXERCISE_IMAGES_CELERY': False,
        'SYNC_EXERCISE_VIDEOS_CELERY': False,
        'CACHE_API_EXERCISES_CELERY': False,
        'CACHE_API_EXERCISES_CELERY_FORCE_UPDATE': False,
    })
    def test_setup_periodic_tasks_when_all_jobs_are_disabled_registers_none(self):
        sender = Mock()

        setup_periodic_tasks(sender)

        sender.add_periodic_task.assert_not_called()

    @override_settings(WGER_SETTINGS={
        'SYNC_EXERCISES_CELERY': True,
        'SYNC_EXERCISE_IMAGES_CELERY': False,
        'SYNC_EXERCISE_VIDEOS_CELERY': False,
        'CACHE_API_EXERCISES_CELERY': False,
        'CACHE_API_EXERCISES_CELERY_FORCE_UPDATE': False,
    })
    def test_setup_periodic_tasks_when_sender_rejects_registration_propagates_error(self):
        sender = Mock()
        sender.add_periodic_task.side_effect = RuntimeError('scheduler unavailable')

        with self.assertRaisesRegex(RuntimeError, 'scheduler unavailable'):
            setup_periodic_tasks(sender)
