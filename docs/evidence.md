# Final Project Evidence Page

This page indexes repository evidence for the course claims in [SAD.md](SAD.md). It contains project artifacts and commit references, not personal information.

## Feature and architecture

| Claim | Evidence |
| --- | --- |
| Cardio activity logging was requested as a separate activity flow | [wger issue #2510](https://github.com/wger-project/wger/issues/2510); design note in [DESIGN.md](DESIGN.md) |
| A dedicated cardio record and constraints were implemented | `wger/manager/models/cardio.py`; migration `wger/manager/migrations/0030_cardiolog.py`; implementation commit `23959c897` |
| Web create/list/edit/delete and owner scoping exist | `wger/manager/views/cardio.py`; `wger/manager/urls.py`; `wger/manager/templates/manager/cardio/`; tests in `wger/manager/tests/test_cardio_log.py` |
| REST resource supports create/update/delete and owner filtering | `wger/manager/api/serializers.py`; `wger/manager/api/views.py`; `wger/urls.py`; tests in `wger/manager/tests/test_cardio_api.py` |
| Logical architecture includes the feature | [logical-architecture.md](logical-architecture.md) |
| Updated use-case and domain diagrams include the feature | [use-case-diagram.puml](use-case-diagram.puml); [domain-model.md](domain-model.md) |
| Interaction diagram follows the real successful web path | [interaction-diagrams.md](interaction-diagrams.md), “Log Cardio Activity” section |

## Course design, security, and testing history

| Claim | Evidence |
| --- | --- |
| Strategy refactoring separated deletion behavior by model type | `wger/exercises/deletion_strategies.py`; `wger/exercises/sync.py`; commit `9fb79a245`; tests in `wger/exercises/tests/test_sync.py` |
| Information Expert refactoring moved routine calculations to the routine model | Commit `a918f8385`; `wger/manager/models/routine.py`; `wger/manager/api/serializers.py` |
| A7 characterization tests covered important existing behavior | Commit `23f3b7b0d`; tests in `wger/core/tests/test_api_permission_characterization.py`, `wger/exercises/tests/test_task_characterization.py`, and `wger/nutrition/tests/test_import_usda_products.py` |
| A7 defect was reproduced and fixed | Red commit `7f7507435`; green commit `b6f3df3be`; `wger/core/api/permissions.py` |
| Baseline coverage report measures line coverage | [coverage-report.md](coverage-report.md), generated before the cardio feature; reports 91% and records one earlier DNS-related error |
| Security control mitigated an untrusted upstream image URL | Commit `159805017`; `_is_trusted_wger_image_url()` and guarded fetch in `wger/nutrition/sync.py`; regression tests in `wger/nutrition/tests/test_sync.py` |
| Misuse and trust boundaries were documented | [misuse-case-diagram.md](misuse-case-diagram.md); [trust-boundary-diagram.md](trust-boundary-diagram.md) |
| Component inventory exists | [sbom.json](sbom.json), CycloneDX JSON with 342 components |

## Verification recorded for this draft

The final implementation was tested with:

```bash
DJANGO_SETTINGS_MODULE=settings.ci ./.venv/bin/python manage.py test --verbosity 1
```

Output summary: **Ran 2,282 tests in 177.079s; OK (skipped=36).** Ruff passed for changed feature files, and `makemigrations manager --check --dry-run` reported no model/migration drift. These are recorded from the implementation session; rerun them after any edits before submission.

## Evidence to restore or verify before submission

- The repository does not contain the earlier OSV/dependency scanner output or an advisory citation. Do not submit a named CVE/GHSA, affected range, or call-path claim until the original advisory has been opened and checked. The SBOM alone is not proof of vulnerability or reachability.
- The trust-boundary artifact now reflects commit `159805017`'s origin validation and disabled redirects; review the stated limits against the image-sync code before submission.
- No standalone Week 12 activity/state diagram was found in `docs/`; the diagrams in `SAD.md` are derived from the current cardio implementation. Compare them with the course's original artifact if one exists elsewhere.
- Verify the final accessibility behavior manually, and add the cardio strings to the project's translation workflow/catalogs before claiming translated feature coverage.
- The project contribution materials checked for this draft did not specify a DCO or CLA. Recheck before an upstream submission.
