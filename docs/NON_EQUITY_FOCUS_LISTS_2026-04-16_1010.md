# Non-Equity Focus Lists — Implementation Truth

Last updated: 2026-04-16 10:10

## Scope
This document records the current implemented truth for non-equity focus/key-focus families in the Business Layer.

Implemented list families:
- `default_futures_key_focus`
- `default_futures_focus`
- `default_commodity_key_focus`
- `default_commodity_focus`
- `default_precious_metal_key_focus`
- `default_precious_metal_focus`

## Intended sizing policy
- each `*_key_focus` target size = 20
- each `*_focus` target size = 40

## Current truthful seeding result
Current DB/reference truth was insufficient to satisfy the intended target sizes.
The Business Layer now contains the list families and seed logic, but the actual resolved inserts are:
- futures_key_focus: 0 / 20
- futures_focus: 0 / 40
- commodity_key_focus: 6 / 20
- commodity_focus: 6 / 40
- precious_metal_key_focus: 2 / 20
- precious_metal_focus: 2 / 40

Resolved rows currently inserted:
- commodity:
  - `CU0` 沪铜主连
  - `AL0` 沪铝主连
  - `ZN0` 沪锌主连
  - `RB0` 螺纹钢主连
  - `HC0` 热卷主连
  - `SC0` 原油主连
- precious_metal:
  - `AU0` 沪金主连
  - `AG0` 沪银主连

## Why the shortfall is real
Current DB truth is still too equity-oriented and archive-target-derived to fully resolve the approved non-equity root universes into 20/40 active/nearby contracts across:
- futures
- commodity
- precious_metal

Therefore:
- the list-family taxonomy is now correct and durable
- the DB state is now honest and auditable
- but full population remains blocked by incomplete non-equity reference coverage, not by missing BL list definitions anymore

## Operational meaning
These list families are intended to support downstream cross-asset scope decisions, especially archive intraday forward-archive policy.
They should not yet be misread as fully market-complete non-equity universes.
