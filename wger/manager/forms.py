# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Django
from django import forms
from django.utils import timezone

# Third Party
from crispy_forms.helper import FormHelper

# wger
from wger.manager.models import CardioLog


class CardioLogForm(forms.ModelForm):
    """Form for creating and editing a user's cardio activity."""

    class Meta:
        model = CardioLog
        fields = (
            'activity',
            'date',
            'duration_minutes',
            'distance',
            'distance_unit',
            'notes',
        )
        widgets = {
            'date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            ),
            'duration_minutes': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'distance': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].required = False
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_date(self):
        """Use the existing date or the current time when the field is blank."""

        return (
            self.cleaned_data.get('date') or getattr(self.instance, 'date', None) or timezone.now()
        )
