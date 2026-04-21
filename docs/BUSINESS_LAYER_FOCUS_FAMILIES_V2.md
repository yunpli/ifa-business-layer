# Business Layer Focus Families V2

## Scope

This document defines the canonical business-layer focus/key-focus families under the default owner scope.

Owner semantics:
- `owner_type=default`
- `owner_id=default`

## Canonical families

Eight canonical focus families are seeded:

| Family | Key focus | Focus | Notes |
|---|---|---|---|
| stock | `default_stock_key_focus` | `default_stock_focus` | A-share only in phase 1 |
| macro | `default_macro_key_focus` | `default_macro_focus` | Curated macro indicators |
| tech | `default_tech_key_focus` | `default_tech_focus` | Thematic stock subset |
| asset | `default_asset_key_focus` | `default_asset_focus` | Rolling canonical futures/asset concepts |

Archive targets are maintained separately and are not part of the focus-family replacement scope.

## Why A-share only for stock

Current business-layer seed input reads from `ifa2.stock_basic_current`, which exposes Tushare-backed A-share symbols. There is no equivalent HK/US stock universe table available in this repo/schema for the same seed path.

Result:
- HK/US stock symbols are excluded in phase 1
- this is intentional, not an omission
- revisit only after ifa-data-platform provides a supported HK/US source with the same maintenance contract

## Asset canonical identity

Asset families must use stable canonical concepts instead of dated contracts.

Accepted examples:
- `AU0`, `AG0`
- `CU0`, `AL0`, `ZN0`
- `SC0`, `FU0`
- `RB0`, `HC0`, `I0`, `JM0`
- `M0`, `Y0`, `C0`, `CF0`
- `TA0`, `MA0`, `PP0`, `RU0`, `SA0`

Rejected examples for canonical business focus identity:
- `CU2506.SHF`
- `TA2509.ZCE`
- `RB2510.SHF`

Dated contracts may still exist in downstream data/runtime layers, but the business-layer focus identity must remain rolling and stable.

## Asset phase-1 sub-buckets

Phase 1 explicitly covers these asset sub-buckets:
- `precious_metal`
- `base_metal`
- `energy`
- `black_chain`
- `agri`
- `chemicals`

These are represented by:
- `focus_lists.asset_type='asset'`
- `focus_list_items.asset_category=<sub_bucket>`
- `focus_list_rules.sub_buckets` documenting the seeded bucket set

## Seeding logic

Seeder entrypoint:
- `scripts/focus_cli.py seed-default`

Implementation behavior:
1. initialize schema if needed
2. fetch stock candidates from `ifa2.stock_basic_current`
3. build curated list specs for stock / macro / tech / asset / archive targets
4. prune legacy default-owner `focus` and `key_focus` lists not in the canonical spec set
5. replace rules and items for each canonical list

Replace-style seeding is intentional so old temporary defaults do not linger.

## Schema used

No new family table is required in V2.

Existing tables remain authoritative:
- `ifa2.focus_lists`
- `ifa2.focus_list_items`
- `ifa2.focus_list_rules`

Important field usage:
- `focus_lists.owner_type`, `focus_lists.owner_id`: tenant/owner boundary
- `focus_lists.list_type`: `key_focus`, `focus`, `archive_targets`
- `focus_lists.asset_type`: family-level identity (`stock`, `macro`, `tech`, `asset`, `multi_asset`)
- `focus_list_items.asset_category`: item-level category or asset sub-bucket
- `focus_list_rules`: target size, owner scope, theme, canonical identity policy, asset sub-bucket declaration

## Usage

Initialize schema:

```bash
PYTHONPATH=/Users/neoclaw/repos/ifa-business-layer \
DATABASE_URL='postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp' \
IFA_DB_SCHEMA=ifa2 \
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/focus_cli.py init-schema
```

Seed default owner families:

```bash
PYTHONPATH=/Users/neoclaw/repos/ifa-business-layer \
DATABASE_URL='postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp' \
IFA_DB_SCHEMA=ifa2 \
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/focus_cli.py seed-default
```

Inspect one family:

```bash
PYTHONPATH=/Users/neoclaw/repos/ifa-business-layer \
DATABASE_URL='postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp' \
IFA_DB_SCHEMA=ifa2 \
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/focus_cli.py list-items --name default_asset_key_focus
```
