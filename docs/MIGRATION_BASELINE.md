# Migration Baseline

## Purpose

Business Layer Phase 1 currently manages these business-layer objects in schema `ifa2`:

- `focus_lists`
- `focus_list_items`
- `focus_list_rules`

The current operational approach remains:
- idempotent schema initialization via `scripts/focus_cli.py init-schema`
- idempotent default seed via `scripts/focus_cli.py seed-default`

## Current baseline strategy

This repo does **not** yet run a dedicated Alembic history of its own.
Instead, the baseline is documented here and mirrored in SQL:

- `docs/MIGRATION_BASELINE.md`
- `sql/001_business_layer_baseline.sql`

This is intentional for the cleanup pass:
- no behavior change
- no new runtime dependency
- no collection-layer expansion

## Managed tables

### `ifa2.focus_lists`
Business list definitions:
- owner scope
- list type
- asset orientation
- frequency orientation
- active flag

### `ifa2.focus_list_items`
Concrete list members:
- symbol
- display name
- item asset category
- priority
- source
- notes

### `ifa2.focus_list_rules`
List-level lightweight rules/metadata:
- target_size
- granularity
- owner_scope

## Operational rule

Until a future dedicated migration runner is added, any schema-related change to these three tables must update **both**:
1. `ifa_business_layer/schema.py`
2. `sql/001_business_layer_baseline.sql`

This keeps the code baseline and SQL baseline aligned.

## Future upgrade path

A later cleanup can introduce either:
- Alembic under this repo, or
- a shared migration authority with explicit ownership boundaries

That follow-up is non-blocking for Phase 1 because the current schema is already live and the current init path is idempotent.
