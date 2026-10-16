# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Standard Library
from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Callable
from typing import Any

# wger
from wger.exercises.models import (
    DeletionLog,
    Exercise,
    ExerciseImage,
    ExerciseVideo,
    Translation,
)
from wger.manager.models import (
    SlotEntry,
    WorkoutLog,
)


class DeletionStrategy(ABC):
    """Delete one kind of object described by an upstream deletion-log entry."""

    @abstractmethod
    def delete(self, entry: dict[str, Any], print_fn: Callable[[str], Any]) -> None:
        pass


class ExerciseDeletionStrategy(DeletionStrategy):
    """Delete an exercise after moving its references to an optional replacement."""

    def delete(self, entry: dict[str, Any], print_fn: Callable[[str], Any]) -> None:
        uuid = entry['uuid']
        replaced_by_uuid = entry['replaced_by']

        try:
            replacement = Exercise.objects.get(uuid=replaced_by_uuid)
        except Exercise.DoesNotExist:
            replacement = None

        try:
            exercise = Exercise.objects.get(uuid=uuid)
        except Exercise.DoesNotExist:
            return

        slot_entry_count = None
        log_count = None
        if replacement:
            # Exercise.delete() repoints these references; count them first for reporting.
            slot_entry_count = SlotEntry.objects.filter(exercise=exercise).count()
            log_count = WorkoutLog.objects.filter(exercise=exercise).count()

        exercise.delete(replace_by=replaced_by_uuid if replacement else None)

        replacement_info = f' (replaced by {replacement.uuid})' if replacement else ''
        print_fn(f'Deleted exercise {uuid}{replacement_info}')
        if slot_entry_count:
            print_fn(f'- replaced in {slot_entry_count} routines')
        if log_count:
            print_fn(f'- replaced in {log_count} workout logs')


class ModelDeletionStrategy(DeletionStrategy):
    """Shared deletion behavior for exercise-related models without replacements."""

    model = None
    label = ''

    def deletion_message(self, entry: dict[str, Any]) -> str:
        return f'Deleted {self.label} {entry["uuid"]}'

    def delete(self, entry: dict[str, Any], print_fn: Callable[[str], Any]) -> None:
        try:
            obj = self.model.objects.get(uuid=entry['uuid'])
        except self.model.DoesNotExist:
            return

        obj.delete()
        print_fn(self.deletion_message(entry))


class TranslationDeletionStrategy(ModelDeletionStrategy):
    model = Translation
    label = 'translation'

    def deletion_message(self, entry: dict[str, Any]) -> str:
        return f'Deleted translation {entry["uuid"]} ({entry["comment"]})'


class ImageDeletionStrategy(ModelDeletionStrategy):
    model = ExerciseImage
    label = 'image'


class VideoDeletionStrategy(ModelDeletionStrategy):
    model = ExerciseVideo
    label = 'video'


DELETION_STRATEGIES: dict[str, DeletionStrategy] = {
    DeletionLog.MODEL_EXERCISE: ExerciseDeletionStrategy(),
    DeletionLog.MODEL_TRANSLATION: TranslationDeletionStrategy(),
    DeletionLog.MODEL_IMAGE: ImageDeletionStrategy(),
    DeletionLog.MODEL_VIDEO: VideoDeletionStrategy(),
}


def deletion_strategy_for(model_type: str) -> DeletionStrategy | None:
    return DELETION_STRATEGIES.get(model_type)
