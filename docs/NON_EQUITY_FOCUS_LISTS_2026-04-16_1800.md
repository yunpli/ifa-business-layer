# Non-Equity Focus Lists — Narrow Gap Batch Update

Last updated: 2026-04-16 18:00

## Scope
This update focuses narrowly on remaining Business Layer coverage gaps for:
- futures
- precious_metal
- commodity focus expansion

## Current counts after this batch
- `default_futures_key_focus`: `0 / 20`
- `default_futures_focus`: `0 / 40`
- `default_commodity_key_focus`: `20 / 20`
- `default_commodity_focus`: `21 / 40`
- `default_precious_metal_key_focus`: `4 / 20`
- `default_precious_metal_focus`: `4 / 40`

## What improved in this batch
- precious-metal coverage improved from `2` to `4`
- commodity key-focus remains full at `20`
- commodity focus remains `21`
- futures remains `0`

## Exact unresolved reasons
### Futures unresolved roots
No current DB/runtime contract truth found for:
- `IF`
- `IH`
- `IC`
- `IM`
- `TS`
- `TF`
- `T`
- `TL`

Therefore futures coverage is still blocked by upstream/reference truth, not BL logic.

### Commodity remaining unresolved roots
No current DB/runtime contract truth found for several approved roots, including:
- `LU`
- `FU`
- `BU`
- `PX`
- `PF`
- `SN`
- `AO`
- `FG`
- `SA`
- `SH`
- `BR`
- `NR`
- `M`
- `Y`
- `P`
- `OI`
- `RM`
- `C`
- `CS`
- `CF`
- `SR`
- `UR`

### Precious-metal unresolved reason
Current DB/runtime truth still exposes only a narrow AU/AG contract set, so 20/40 targets remain unreachable.

## Truthful judgment
- BL non-equity coverage improved again, but only modestly
- precious-metal improved to 4 total symbols
- commodity focus did not advance beyond 21
- futures remains unresolved due to missing upstream/current truth
- remaining shortfall is explicit and auditable, not hidden
