# Non-Equity Focus Lists

Last updated: 2026-04-16

## Purpose
These Business Layer list families define non-equity scope for downstream consumers such as archive-forward intraday policy and cross-asset/operator watchlists.

Implemented list families:
- `default_futures_key_focus`
- `default_futures_focus`
- `default_commodity_key_focus`
- `default_commodity_focus`
- `default_precious_metal_key_focus`
- `default_precious_metal_focus`

## Intended sizing
Target sizing policy is:
- key_focus = 20
- focus = 40

## Current truthful limitation
Current DB/reference truth does not yet fully support those target sizes cleanly.
The lists are seeded from currently resolvable non-equity symbols already visible in current DB truth / accepted runtime universe.

As of the 2026-04-16 seeding batch:
- futures lists resolved 0 clean rows from current DB truth
- commodity lists resolved 6 rows
- precious_metal lists resolved 2 rows

That means the list families now exist as repo/business definitions, but current symbol coverage remains incomplete and should not be mistaken for full target-size completion.

## Why this still matters
Even partial list-family existence is important because:
- the BL taxonomy now exists for futures / commodity / precious_metal
- downstream code can reference stable list names and business meaning
- unresolved sizing shortfall is explicit and auditable rather than hidden
