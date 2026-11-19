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
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

# wger
from wger.utils.uuid import uuid7


class CardioLog(models.Model):
    """A standalone cardio activity recorded by a user."""

    DISTANCE_UNIT_METERS = 'm'
    DISTANCE_UNIT_KILOMETERS = 'km'
    DISTANCE_UNIT_MILES = 'mi'
    DISTANCE_UNITS = (
        (DISTANCE_UNIT_METERS, 'm'),
        (DISTANCE_UNIT_KILOMETERS, 'km'),
        (DISTANCE_UNIT_MILES, 'mi'),
    )

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    activity = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    duration_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    distance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    distance_unit = models.CharField(
        max_length=2,
        choices=DISTANCE_UNITS,
        null=True,
        blank=True,
    )
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date', '-id']
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(duration_minutes__isnull=True) | models.Q(duration_minutes__gte=0)
                ),
                name='cardio_duration_non_negative',
            ),
            models.CheckConstraint(
                condition=models.Q(distance__isnull=True) | models.Q(distance__gte=0),
                name='cardio_distance_non_negative',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(duration_minutes__isnull=False) | models.Q(distance__isnull=False)
                ),
                name='cardio_log_has_metric',
            ),
            models.CheckConstraint(
                condition=(models.Q(distance__isnull=True) | models.Q(distance_unit__isnull=False)),
                name='cardio_log_distance_has_unit',
            ),
            models.CheckConstraint(
                condition=(models.Q(distance__isnull=False) | models.Q(distance_unit__isnull=True)),
                name='cardio_log_unit_requires_distance',
            ),
        ]

    def clean(self):
        super().clean()
        if self.duration_minutes is None and self.distance is None:
            raise ValidationError('Enter a duration, a distance, or both.')
        if self.distance is None and self.distance_unit is not None:
            raise ValidationError({'distance_unit': 'A distance unit requires a distance.'})
        if self.distance is not None and self.distance_unit is None:
            raise ValidationError({'distance_unit': 'Choose a unit for the distance.'})

    def get_owner_object(self):
        """Return this record for wger's generic owner permission check."""

        return self

    def __str__(self):
        return f'{self.activity} - {self.date:%Y-%m-%d}'
