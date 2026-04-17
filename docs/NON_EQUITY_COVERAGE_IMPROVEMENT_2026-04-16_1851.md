# Non-Equity Coverage Improvement

Last updated: 2026-04-16 18:51

## Scope
This narrow batch pushed practical BL coverage further under the corrected non-equity category model.
It did not reopen taxonomy design.

Artifact:
- `artifacts/non_equity_coverage_improvement_2026-04-16_1848.json`

## Current category coverage counts after this batch
- `default_commodity_key_focus`: `4 / 20`
- `default_commodity_focus`: `4 / 40`
- `default_metal_key_focus`: `8 / 20`
- `default_metal_focus`: `8 / 40`
- `default_precious_metal_key_focus`: `4 / 20`
- `default_precious_metal_focus`: `4 / 40`
- `default_black_chain_key_focus`: `6 / 20`
- `default_black_chain_focus`: `6 / 40`

## What improved
- coverage is now represented in cleaner category buckets instead of one mixed operational bucket
- metal and black-chain are now explicitly defined and populated
- precious-metal remains small but explicit
- commodity is now represented as the small commodity/chemical subset actually visible in source truth

## Why counts remain incomplete
- current accessible source universe is still small and uneven
- current resolvable symbols by category are capped by source truth, not by missing BL family names anymore

## Truthful judgment
This batch improves BL coverage quality and category cleanliness.
It does not achieve large counts because the current accessible source truth does not support them.
