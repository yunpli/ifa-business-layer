# IFA Business Layer

## Purpose

`ifa-business-layer` owns the business-layer focus objects for iFA.
It manages owner-scoped focus/key-focus families and archive-target maintenance, not collection runtime.

## Phase-1 focus families

Canonical owner scope:
- `owner_type=default`
- `owner_id=default`

Seeded focus families:
- `default_stock_key_focus`
- `default_stock_focus`
- `default_macro_key_focus`
- `default_macro_focus`
- `default_tech_key_focus`
- `default_tech_focus`
- `default_asset_key_focus`
- `default_asset_focus`

Archive targets remain available:
- `default_archive_targets_minute`
- `default_archive_targets_15min`
- `default_archive_targets_daily`

## Data model

Managed tables:
- `ifa2.focus_lists`
- `ifa2.focus_list_items`
- `ifa2.focus_list_rules`

Key conventions:
- all default business objects use owner=`default/default`
- stock family is seeded from A-share symbols only, because current Tushare-backed tables in `ifa2` expose `stock_basic_current` but do not expose an equivalent HK/US stock universe here
- tech family is a thematic stock subset with `asset_type=tech` and item category `tech`
- asset family uses stable rolling canonical concepts (`AU0`, `CU0`, `SC0`, `M0`, `TA0`, etc.), never dated contracts
- asset phase-1 sub-buckets explicitly include `precious_metal`, `base_metal`, `energy`, `black_chain`, `agri`, `chemicals`

## Unified venv rule

Use the shared environment only:
- `/Users/neoclaw/repos/ifa-data-platform/.venv`

## CLI

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

Examples:

```bash
DATABASE_URL='postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp' \
IFA_DB_SCHEMA=ifa2 \
PYTHONPATH=/Users/neoclaw/repos/ifa-business-layer \
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/focus_cli.py init-schema

DATABASE_URL='postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp' \
IFA_DB_SCHEMA=ifa2 \
PYTHONPATH=/Users/neoclaw/repos/ifa-business-layer \
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/focus_cli.py seed-default
```

Inspect a seeded family:

```bash
DATABASE_URL='postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp' \
IFA_DB_SCHEMA=ifa2 \
PYTHONPATH=/Users/neoclaw/repos/ifa-business-layer \
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/focus_cli.py list-items --name default_asset_focus
```

## Seeding behavior

`seed-default` is idempotent and replace-style:
- upserts the canonical default families
- fully replaces rules/items for each seeded list
- removes legacy default owner `focus` / `key_focus` lists that are no longer part of the canonical set
- keeps archive-target lists under the same owner scope

## Documentation

Implementation notes:
- `docs/BUSINESS_LAYER_FOCUS_FAMILIES_V2.md`
- `docs/MIGRATION_BASELINE.md`
- `docs/BUSINESS_LAYER_DESIGN.md`

Phase-1 A-share 2.0 business contracts:
- `docs/A_SHARE_2_0_ONE_MAIN_THREE_SUPPORT_CONTRACT.md`
- `docs/A_SHARE_MAIN_AGENT_DELIVERY_CONTRACT.md`
- `docs/A_SHARE_SUPPORT_AGENTS_DELIVERY_CONTRACT.md`
- `docs/A_SHARE_FSJ_AND_EVIDENCE_MAPPING_V1.md`
- `docs/A_SHARE_FSJ_PERSISTENCE_CONTRACT_PHASE1_2026-04-22.md`
- `docs/A_SHARE_REPORT_PRODUCTION_SLA_AND_MAIN_QUEUE_2026-04-22.md`
