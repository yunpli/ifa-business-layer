# IFA Business Layer

## Purpose

`ifa-business-layer` is the independent business-control repository for iFA Business Layer Phase 1.
It manages business objects only, not data collection runtime logic.

Phase 1 scope:
- key focus
- focus
- archive targets
- tech-only focus subsets (`tech_key_focus`, `tech_focus`)
- owner-scoped defaults
- maintenance CLI
- schema baseline for the business-layer-managed objects

Phase 1 default owner:
- `owner_type=default`
- `owner_id=default`

## Unified venv rule

This repo must reuse the existing iFA standard environment:
- `/Users/neoclaw/repos/ifa-data-platform/.venv`

Rules:
- do not create a dedicated business-layer venv
- run development, CLI, and tests in the shared unified venv
- if dependencies are missing, add them to the unified venv only

## Database / schema requirements

Database:
- `ifa_db`

Schema:
- `ifa2`

Business Layer Phase 1 currently manages these tables:
- `ifa2.focus_lists`
- `ifa2.focus_list_items`
- `ifa2.focus_list_rules`

Schema initialization remains idempotent for now:
- `scripts/focus_cli.py init-schema`

Migration/history baseline:
- `docs/MIGRATION_BASELINE.md`
- `sql/001_business_layer_baseline.sql`

## Supported CLI commands

Primary maintenance CLI:
- `scripts/focus_cli.py`

Commands:
- `init-schema`
- `seed-default`
- `list-lists`
- `list-items`
- `add-list`
- `delete-list`
- `add-item`
- `delete-item`
- `bulk-upsert`
- `bulk-delete`

These cover:
- list CRUD
- item CRUD
- batch item upsert/delete
- maintenance of key focus / focus / archive target objects
- inspection/maintenance of tech-only lists through the same workflow

## Package layout

This repo uses one clear package layout only:
- root package: `ifa_business_layer/`

No parallel `src/` package layout should remain after cleanup.

## Intentionally out of scope in Phase 1

The following are intentionally NOT included in this phase:
- lowfreq data collection development
- midfreq data collection development
- archive collection/runtime development
- new frequency granularities beyond minute / 15min / daily
- customer-specific owner expansion beyond schema/documentation readiness
- collection-layer consumption integration

## Notes

Technology-only concept is represented within the existing model as dedicated stock-only lists under the canonical owner scope:
- `tech_key_focus` (`list_type=key_focus`, `asset_type=stock`)
- `tech_focus` (`list_type=focus`, `asset_type=stock`)

Seed selection logic is pragmatic/manual for Phase 1: a curated A-share technology list spanning semiconductors, AI compute, software, optics, electronics, industrial automation, and platform/infrastructure names. Overlap with broader default lists is allowed by design in this phase.

Business Layer Phase 1 is functionally complete for its requested scope.
This repo should now be treated as the owner of the business-layer object model and maintenance surface, while data collection remains outside scope until a later phase.
