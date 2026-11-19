# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Django
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import CardioLog


class CardioLogApiTestCase(WgerTestCase):
    """Exercise cardio logging through the REST API."""

    def setUp(self):
        super().setUp()
        self.user_login('admin')

    def test_api_creates_and_returns_a_cardio_activity(self):
        response = self.client.post(
            reverse('cardioactivity-list'),
            {
                'activity': 'Pool swim',
                'duration_minutes': '40',
                'distance': '1.5',
                'distance_unit': CardioLog.DISTANCE_UNIT_KILOMETERS,
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201, response.content)
        log = CardioLog.objects.get(pk=response.json()['id'])
        self.assertEqual(log.user_id, 1)
        self.assertEqual(log.activity, 'Pool swim')
        self.assertEqual(str(log.duration_minutes), '40.00')

    def test_api_updates_an_existing_cardio_activity(self):
        log = CardioLog.objects.create(user_id=1, activity='Walk', duration_minutes=20)

        response = self.client.patch(
            reverse('cardioactivity-detail', kwargs={'pk': log.pk}),
            {'duration_minutes': '35'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200, response.content)
        log.refresh_from_db()
        self.assertEqual(str(log.duration_minutes), '35.00')

    def test_api_rejects_negative_duration(self):
        response = self.client.post(
            reverse('cardioactivity-list'),
            {'activity': 'Invalid run', 'duration_minutes': '-1'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertFalse(CardioLog.objects.filter(activity='Invalid run').exists())

    def test_api_does_not_expose_another_users_activity(self):
        log = CardioLog.objects.create(user_id=2, activity='Private activity', duration_minutes=30)

        response = self.client.get(reverse('cardioactivity-detail', kwargs={'pk': log.pk}))

        self.assertEqual(response.status_code, 404)

    def test_api_deletes_the_current_users_activity(self):
        log = CardioLog.objects.create(user_id=1, activity='Short run', duration_minutes=10)

        response = self.client.delete(reverse('cardioactivity-detail', kwargs={'pk': log.pk}))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(CardioLog.objects.filter(pk=log.pk).exists())
