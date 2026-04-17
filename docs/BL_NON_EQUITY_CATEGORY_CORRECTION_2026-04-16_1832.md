# BL Non-Equity Category Correction

Last updated: 2026-04-16 18:32

## Scope
This is a Business Layer correction batch focused on:
1. correcting the non-equity category model
2. resolving the contract-identity naming problem
3. aligning BL scripts/docs/DB truth to the corrected model

Artifacts:
- `scripts/inspect_contract_identity_roll.py`
- `artifacts/contract_identity_roll_2026-04-16_1828.json`
- `scripts/seed_non_equity_category_families.py`
- `artifacts/non_equity_category_families_2026-04-16_1830.json`
- `docs/NON_EQUITY_CATEGORY_MODEL_AND_CONTRACT_IDENTITY.md`

## 1. Current non-equity category truth
The intended Business Layer non-equity categories are now explicitly:
- `commodity`
- `metal`
- `precious_metal`
- `black_chain`

This corrects the earlier ambiguous mixed use of one broad `commodity` bucket.

## 2. Current naming / contract-identity truth
### Source-truth inspection result
Current DB/runtime truth shows that product roots persist while contract months vary.
Examples:
- `AU2506.SHF`
- `AG2506.SHF`
- `HC2506.SHF`
- `NI2506.SHF`
- `CU2506.SHF`
- `AL2506.SHF`
- `ZN2506.SHF`
- `RB2506.SHF`
- `I2506.DCE`
- `J2506.DCE`
- `J2509.DCE`
- `JM2506.DCE`

At the same time, current truth also contains rolling/main-style forms for some products:
- `AU0`
- `AG0`
- `CU0`
- `AL0`
- `ZN0`
- `RB0`
- `HC0`
- `I0`
- `JM0`

### What this means
The stable business identity is generally the product family/root,
not one permanently fixed month contract.

Therefore BL focus/key-focus should not naively treat one specific month code as the permanent identity.

## 3. Chosen design answer
Chosen design:
- Business Layer should use **root-level / rolling-product identity semantics**
- explicit month contracts may appear as current resolvable operational instances
- but they are not the long-term semantic identity

This is the correct interpretation for the current accessible source truth.

## 4. List/table/script/doc changes in the Business Layer repo
### Scripts added/used
- `scripts/inspect_contract_identity_roll.py`
- `scripts/seed_non_equity_category_families.py`

### Docs added
- `docs/NON_EQUITY_CATEGORY_MODEL_AND_CONTRACT_IDENTITY.md`
- `docs/BL_NON_EQUITY_CATEGORY_CORRECTION_2026-04-16_1832.md`

### DB/BL truth changed
Implemented/updated list families now include:
- `default_commodity_key_focus`
- `default_commodity_focus`
- `default_metal_key_focus`
- `default_metal_focus`
- `default_precious_metal_key_focus`
- `default_precious_metal_focus`
- `default_black_chain_key_focus`
- `default_black_chain_focus`

Each list family now carries a BL rule:
- `identity_strategy = root_or_rolling_contract`

## 5. What remains partial/unresolved
- current source universe is still small and uneven
- category counts are still bounded by current accessible truth
- some existing lists still contain explicit month contracts because that is what current DB/runtime truth resolves most directly
- a future refinement may be needed if we want a first-class product-root/rolling identifier field rather than symbol strings only

## Final truthful judgment
This batch fixes the Business Layer category model and naming semantics in repo truth.
The important correction is:
- we now have the correct explicit categories
- and we now have an explicit BL design answer for contract identity
- the BL repo no longer has to rely on the misleading mixed-category model as its intended final definition
