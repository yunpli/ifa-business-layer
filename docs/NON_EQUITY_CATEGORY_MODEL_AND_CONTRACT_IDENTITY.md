# Non-Equity Category Model and Contract Identity

Last updated: 2026-04-16

## Current Business Layer category model
The intended non-equity Business Layer categories are now explicitly:
1. `commodity`
2. `metal`
3. `precious_metal`
4. `black_chain`

This replaces the earlier ambiguous/mixed use of one broad `commodity` bucket as the final category model.

## Current list families
Implemented list-family names now include:
- `default_commodity_key_focus`
- `default_commodity_focus`
- `default_metal_key_focus`
- `default_metal_focus`
- `default_precious_metal_key_focus`
- `default_precious_metal_focus`
- `default_black_chain_key_focus`
- `default_black_chain_focus`

## Contract-identity truth
### What the source truth shows
Current DB/runtime truth shows two kinds of identifiers:
1. explicit month contracts, e.g.
   - `AU2506.SHF`
   - `HC2506.SHF`
   - `NI2506.SHF`
2. rolling/main-style identifiers, e.g.
   - `AU0`
   - `AG0`
   - `CU0`
   - `AL0`
   - `RB0`
   - `HC0`
   - `I0`
   - `JM0`

This means the business object being monitored is usually **not** a permanently fixed month code.
The stable thing is the product/root family, with month contracts rolling over time.

### Chosen design answer
Business Layer should treat non-equity focus/key-focus identity as:
- **root-level / rolling-product identity first**
- with current explicit contracts stored only as currently resolvable practical instances

In other words, the design direction is closest to:
- **A + B combined**
  - root-level identities matter most
  - rolling/main-contract-like identities are acceptable operational realizations
  - fixed one-off month contracts should not be treated as the permanent business identity

### Practical implication
If a current list contains:
- `AU2506.SHF`
- `AU0`

that should be interpreted as practical current resolvable coverage of the `AU` product family,
not as a claim that `2506` is the permanent BL identity.

## Current partial truth
Some lists still contain explicit contracts because that is what current DB/runtime truth resolves most clearly.
That is acceptable as a temporary operational representation,
but the durable BL meaning should be read as product-family / rolling identity, not one static month contract forever.

## What remains partial
- category sizes are still limited by current accessible source truth
- some category families are still small
- the repo still needs later refinement if we want a cleaner first-class root/rolling representation in storage rather than current symbol strings only
