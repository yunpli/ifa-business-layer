# Non-Equity Focus Lists — Coverage Improvement Truth

Last updated: 2026-04-16 10:43

## Scope
This update records the improved non-equity Business Layer seeding after switching to actual contract-like DB/runtime truth sources from Data Platform history tables.

## Current truthful coverage
### Futures
- `default_futures_key_focus`: `0 / 20`
- `default_futures_focus`: `0 / 40`

Exact unresolved reason:
- approved financial-futures roots (`IF`, `IH`, `IC`, `IM`, `TS`, `TF`, `T`, `TL`) still have no current DB/runtime truth in the inspected sources

### Commodity
- `default_commodity_key_focus`: `20 / 20`
- `default_commodity_focus`: `21 / 40`

This is a material improvement over the prior attempt.
It proves current commodity-like contract truth is rich enough to support key-focus fully and focus partially.

### Precious metal
- `default_precious_metal_key_focus`: `2 / 20`
- `default_precious_metal_focus`: `2 / 40`

Exact unresolved reason:
- current DB/runtime truth still only exposes a narrow AU/AG contract set

## Bottom-line truth
- commodity key-focus is now fully populated to target
- commodity focus is still partial
- futures remains unresolved due to absent upstream/reference truth
- precious-metal remains thin due to narrow current contract truth

This is the current honest Business Layer state.
