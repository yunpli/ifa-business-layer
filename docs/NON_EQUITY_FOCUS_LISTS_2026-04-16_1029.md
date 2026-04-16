# Non-Equity Focus Lists — Real Seed Content Update

Last updated: 2026-04-16 10:29

## Scope
This update replaces the earlier too-thin non-equity seeding attempt with a seeding pass based on actual current contract-like DB/runtime truth from Data Platform history tables.

Approved list families remain:
- `default_futures_key_focus`
- `default_futures_focus`
- `default_commodity_key_focus`
- `default_commodity_focus`
- `default_precious_metal_key_focus`
- `default_precious_metal_focus`

## Actual current seeding truth
### Futures
- `default_futures_key_focus`: `0 / 20`
- `default_futures_focus`: `0 / 40`

Exact unresolved reason:
- the approved financial-futures roots (`IF`, `IH`, `IC`, `IM`, `TS`, `TF`, `T`, `TL`) still have **no current DB/runtime contract truth** in the inspected Data Platform reference/history sources

This is therefore not a BL-taxonomy gap anymore.
It is a current upstream/reference-coverage gap.

### Commodity
- `default_commodity_key_focus`: `20 / 20`
- `default_commodity_focus`: `21 / 40`

Resolved commodity symbols now include:
- `SC0`
- `TA2506.ZCE`
- `MA2506.ZCE`
- `CU0`
- `CU2506.SHF`
- `AL0`
- `AL2506.SHF`
- `ZN0`
- `ZN2506.SHF`
- `NI2506.SHF`
- `RB0`
- `RB2506.SHF`
- `HC0`
- `HC2506.SHF`
- `I0`
- `I2506.DCE`
- `J2506.DCE`
- `J2509.DCE`
- `JM0`
- `JM2506.DCE`
- `RU2506.SHF` (focus extension)

### Precious metal
- `default_precious_metal_key_focus`: `2 / 20`
- `default_precious_metal_focus`: `2 / 40`

Resolved symbols:
- `AU2506.SHF`
- `AG2506.SHF`

Exact unresolved reason:
- current DB/runtime truth only exposes a very narrow AU/AG contract set, so the 20/40 target cannot yet be met truthfully

## Bottom-line truth
- BL non-equity families now exist and are materially better seeded than before
- commodity key_focus now reaches full target size 20
- commodity focus still falls short
- futures remains unresolved because the required approved roots still have no current DB/runtime truth
- precious_metal remains far below target because current DB/runtime truth is too narrow
