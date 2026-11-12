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
from types import SimpleNamespace

# Django
from django.test import SimpleTestCase

# wger
from wger.core.api.permissions import AllowRegisterUser


class AllowRegisterUserCharacterizationTestCase(SimpleTestCase):
    def setUp(self):
        self.permission = AllowRegisterUser()

    def test_has_permission_when_profile_allows_registration_returns_true(self):
        request = SimpleNamespace(
            user=SimpleNamespace(
                is_anonymous=False,
                userprofile=SimpleNamespace(can_add_user=True),
            )
        )

        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_when_profile_disallows_registration_returns_false(self):
        request = SimpleNamespace(
            user=SimpleNamespace(
                is_anonymous=False,
                userprofile=SimpleNamespace(can_add_user=False),
            )
        )

        self.assertFalse(self.permission.has_permission(request, None))

    def test_has_permission_when_user_is_anonymous_returns_false(self):
        request = SimpleNamespace(user=SimpleNamespace(is_anonymous=True))

        self.assertFalse(self.permission.has_permission(request, None))

    def test_has_permission_when_authenticated_user_has_no_profile_denies_registration(self):
        request = SimpleNamespace(user=SimpleNamespace(is_anonymous=False))

        self.assertFalse(self.permission.has_permission(request, None))
