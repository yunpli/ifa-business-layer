# Business Layer Design

## Why a separate repository

This layer is intentionally separated from `ifa-data-platform` because it is a business-control plane, not a collection-runtime implementation.

Responsibilities here:
- owner-scoped business objects
- default key focus / focus / archive target sets
- maintenance scripts
- future customer customization boundary

Responsibilities not here:
- lowfreq collection logic
- midfreq collection logic
- archive collection logic

## Standard venv

This repo reuses the standard iFA platform virtual environment:
- `/Users/neoclaw/repos/ifa-data-platform/.venv`

No dedicated business-layer venv is allowed.

## Owner model

Phase 1 default:
- `owner_type=default`
- `owner_id=default`

Future-compatible expansion:
- `owner_type=customer`
- `owner_type=account`
- `owner_type=org`
- `owner_id=<tenant specific id>`

## Boundary between object classes

- `key_focus`: smallest, highest-conviction set, future high-frequency candidate pool
- `focus`: broader operational and reporting set
- `archive_targets`: history accumulation targets separated by frequency granularity

## Asset typing

`focus_lists.asset_type` describes list-level orientation:
- `multi_asset`
- future options: `stock`, `macro`, `futures`, `commodity`, `precious_metal`

Phase 1 implementation keeps `asset_type=multi_asset` for the default cross-asset pools while item-level classification stays in `focus_list_items.asset_category`.

`focus_list_items.asset_category` describes item-level category precisely.

## Relationship with symbol_universe

Current rule:
- stock defaults are seeded from explicit code list chosen to be compatible with current DB and future downstream collection
- future integration should validate stock symbols against `ifa2.symbol_universe` and/or `ifa2.stock_basic_current`

Macro / futures / commodity / precious metal objects are business-layer objects first. They should not be blocked by stock-specific registry design.

## Default compatibility with future customization

Default owner uses the same schema and scripts as future custom owners.
No special-case schema is introduced for `default`.

## Long-term maintenance

Maintenance is done through one CLI:
- `scripts/focus_cli.py`

Supports:
- schema init
- default seed
- list CRUD
- item CRUD
- batch upsert
- batch delete

This keeps the system scriptable and testable.
