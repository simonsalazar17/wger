# Pull request draft: standalone cardio activity logging

## Problem

The current workout log represents strength exercise sets, so it does not provide a direct way to record activities such as running, walking, hiking, or swimming. This change follows the request in [wger issue #2510](https://github.com/wger-project/wger/issues/2510).

## What changed

- Added a dedicated `CardioLog` model and migration for activity, date/time, optional duration, optional distance and unit, and notes.
- Added model and database validation: duration or distance is required, distance needs a unit, and measurements cannot be negative.
- Added an authenticated web page in the Training menu to create, view, update, and delete a user's cardio entries.
- Added the owner-scoped `cardioactivity` REST endpoint with create, retrieve, update, and delete operations.
- Updated the logical architecture diagram and changelog.

## Verification

Run the focused feature tests with:

```bash
DJANGO_SETTINGS_MODULE=settings.ci python manage.py test wger.manager.tests.test_cardio_log wger.manager.tests.test_cardio_api
```

Run the complete test suite with:

```bash
DJANGO_SETTINGS_MODULE=settings.ci python manage.py test
```

The complete suite reported **2,281 tests run, OK, 36 skipped**. Ruff passed on the changed Python packages, and `makemigrations manager --check --dry-run` reported no model/migration drift. Django emitted the existing warning that `node_modules` is absent; a test's optional GitHub statistics request also logged a DNS error.

## Compatibility and scope

The feature adds a database table and API route; it does not change existing workout log data or payloads. Existing clients continue to use their current endpoints. This implementation covers the web application and REST API; PowerSync/mobile synchronization, heart-rate tracking, intervals, calorie estimates, and health-platform imports remain out of scope.

## Review focus

Please review whether `duration_minutes` is the right public API unit and whether the first version should keep distance units per entry. The current design keeps these values explicit, avoids altering the strength-log contract, and does not convert user-entered measurements.

## Self-review

- Added database check constraints as well as form/API validation after reviewing that field validators alone do not protect direct database writes.
- Added `CardioLog.get_owner_object()` after the first API update test showed that wger's generic permission class uses this hook to recognize ownership.
- Made a blank date default to the current time after the web test showed Django's generated form otherwise treated that field as required, despite the model default.

The change most likely to draw review feedback is the server-rendered page instead of a React screen. The React source is maintained in the separate `@wger-project/react-components` package, so this keeps the UI implementation in the same repository as its model and tests; it also means the feature is not yet part of the React workout flow.

## Project process notes

The [online contribution guide](https://wger.readthedocs.io/en/latest/contributing.html) says, “Before starting working on a new feature, please open an issue to discuss it with us,” and asks contributors to use a feature branch, add tests, run `ruff format` and `ruff check --fix`, and consider UI/UX. The pull request template likewise asks for tests, formatting, and a changelog entry for substantial work. Issue #2510 provides the discussion context. No DCO sign-off or CLA requirement appears in the checked contribution materials. This is a coursework fork change; no upstream pull request is being opened.
