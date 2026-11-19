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

# Django
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import CardioLog


class CardioLogModelTestCase(WgerTestCase):
    """Test the domain rules for standalone cardio entries."""

    def make_log(self, **kwargs):
        return CardioLog(user_id=1, activity='Run', **kwargs)

    def test_duration_only_entry_is_valid(self):
        log = self.make_log(duration_minutes=30)

        log.full_clean()

    def test_distance_only_entry_is_valid_with_unit(self):
        log = self.make_log(distance=5, distance_unit=CardioLog.DISTANCE_UNIT_KILOMETERS)

        log.full_clean()

    def test_entry_accepts_both_duration_and_distance(self):
        log = self.make_log(
            duration_minutes=30,
            distance=5,
            distance_unit=CardioLog.DISTANCE_UNIT_KILOMETERS,
        )

        log.full_clean()

    def test_zero_duration_and_distance_are_valid(self):
        log = self.make_log(
            duration_minutes=0,
            distance=0,
            distance_unit=CardioLog.DISTANCE_UNIT_KILOMETERS,
        )

        log.full_clean()

    def test_entry_without_duration_or_distance_is_invalid(self):
        log = self.make_log()

        with self.assertRaises(ValidationError):
            log.full_clean()

    def test_distance_requires_a_unit(self):
        log = self.make_log(distance=5)

        with self.assertRaises(ValidationError):
            log.full_clean()

    def test_unit_cannot_be_set_without_distance(self):
        log = self.make_log(
            duration_minutes=30,
            distance_unit=CardioLog.DISTANCE_UNIT_KILOMETERS,
        )

        with self.assertRaises(ValidationError):
            log.full_clean()

    def test_negative_duration_is_invalid(self):
        log = self.make_log(duration_minutes=-1)

        with self.assertRaises(ValidationError):
            log.full_clean()

    def test_negative_distance_is_invalid(self):
        log = self.make_log(
            distance=-1,
            distance_unit=CardioLog.DISTANCE_UNIT_KILOMETERS,
        )

        with self.assertRaises(ValidationError):
            log.full_clean()

    def test_database_rejects_negative_duration(self):
        with self.assertRaises(IntegrityError):
            CardioLog.objects.create(user_id=1, activity='Invalid run', duration_minutes=-1)


class CardioLogWebTestCase(WgerTestCase):
    """Exercise cardio logging through the authenticated web interface."""

    def setUp(self):
        super().setUp()
        self.user_login('admin')

    def test_user_can_create_and_view_a_completed_activity(self):
        response = self.client.post(
            reverse('manager:cardio-overview'),
            {
                'activity': 'Evening run',
                'duration_minutes': '32.5',
                'distance': '5.2',
                'distance_unit': CardioLog.DISTANCE_UNIT_KILOMETERS,
                'notes': 'Easy pace',
            },
        )

        self.assertRedirects(response, reverse('manager:cardio-overview'))
        log = CardioLog.objects.get(activity='Evening run')
        self.assertEqual(log.user_id, 1)
        self.assertContains(self.client.get(reverse('manager:cardio-overview')), 'Evening run')
        self.assertContains(self.client.get(reverse('manager:cardio-overview')), '32.50 min')

    def test_user_can_update_an_activity(self):
        log = CardioLog.objects.create(user_id=1, activity='Walk', duration_minutes=20)

        response = self.client.post(
            reverse('manager:cardio-edit', kwargs={'pk': log.pk}),
            {'activity': 'Fast walk', 'duration_minutes': '25'},
        )

        self.assertRedirects(response, reverse('manager:cardio-overview'))
        log.refresh_from_db()
        self.assertEqual(log.activity, 'Fast walk')
        self.assertEqual(str(log.duration_minutes), '25.00')

    def test_user_cannot_edit_another_users_activity(self):
        log = CardioLog.objects.create(user_id=2, activity='Private run', duration_minutes=20)

        response = self.client.get(reverse('manager:cardio-edit', kwargs={'pk': log.pk}))

        self.assertEqual(response.status_code, 404)

    def test_user_can_delete_their_activity_after_confirmation(self):
        log = CardioLog.objects.create(user_id=1, activity='Short run', duration_minutes=10)

        confirmation = self.client.get(reverse('manager:cardio-delete', kwargs={'pk': log.pk}))
        response = self.client.post(reverse('manager:cardio-delete', kwargs={'pk': log.pk}))

        self.assertEqual(confirmation.status_code, 200)
        self.assertRedirects(response, reverse('manager:cardio-overview'))
        self.assertFalse(CardioLog.objects.filter(pk=log.pk).exists())

    def test_activity_requires_a_duration_or_distance(self):
        response = self.client.post(
            reverse('manager:cardio-overview'),
            {'activity': 'Unmeasured run'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a duration, a distance, or both.')
        self.assertFalse(CardioLog.objects.filter(activity='Unmeasured run').exists())

    def test_create_page_renders_one_form_containing_its_submit_button(self):
        response = self.client.get(reverse('manager:cardio-overview'))
        body = response.content.decode()
        form_markup = body.split('<form id="cardio-log-form"', maxsplit=1)[1].split(
            '</form>', maxsplit=1
        )[0]

        self.assertIn('id="id_activity"', form_markup)
        self.assertIn('Save activity', form_markup)
        self.assertIn('type="datetime-local"', body)
