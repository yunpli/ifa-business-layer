from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4
from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp')
OUT = Path('artifacts/non_equity_coverage_improvement_2026-04-16_1848.json')

TARGETS = {
    'default_commodity_focus': {'asset_category': 'commodity', 'target_size': 40},
    'default_metal_key_focus': {'asset_category': 'metal', 'target_size': 20},
    'default_metal_focus': {'asset_category': 'metal', 'target_size': 40},
    'default_precious_metal_key_focus': {'asset_category': 'precious_metal', 'target_size': 20},
    'default_precious_metal_focus': {'asset_category': 'precious_metal', 'target_size': 40},
    'default_black_chain_key_focus': {'asset_category': 'black_chain', 'target_size': 20},
    'default_black_chain_focus': {'asset_category': 'black_chain', 'target_size': 40},
}

CLASS_MAP = {
    'SC': 'commodity', 'TA': 'commodity', 'MA': 'commodity', 'RU': 'commodity',
    'CU': 'metal', 'AL': 'metal', 'ZN': 'metal', 'NI': 'metal', 'PB': 'metal',
    'AU': 'precious_metal', 'AG': 'precious_metal',
    'RB': 'black_chain', 'HC': 'black_chain', 'I': 'black_chain', 'J': 'black_chain', 'JM': 'black_chain',
}

def root_of(symbol: str) -> str:
    out = []
    for ch in symbol:
        if ch.isalpha():
            out.append(ch)
        else:
            break
    return ''.join(out)

with engine.begin() as conn:
    rows = conn.execute(text(
        "select distinct ts_code from ifa2.futures_history union select distinct ts_code from ifa2.futures_15min_history union select distinct ts_code from ifa2.futures_minute_history union select distinct ts_code from ifa2.futures_60min_history union select distinct ts_code from ifa2.commodity_15min_history union select distinct ts_code from ifa2.commodity_minute_history union select distinct ts_code from ifa2.commodity_60min_history union select distinct ts_code from ifa2.precious_metal_15min_history union select distinct ts_code from ifa2.precious_metal_minute_history union select distinct ts_code from ifa2.precious_metal_60min_history"
    )).fetchall()
    universe = {}
    for (symbol,) in rows:
        cat = CLASS_MAP.get(root_of(symbol))
        if cat:
            universe.setdefault(cat, []).append(symbol)
    for cat in universe:
        universe[cat] = sorted(set(universe[cat]))

    payload = {'lists': []}
    for list_name, spec in TARGETS.items():
        list_id = conn.execute(text("select id from ifa2.focus_lists where name=:name"), {'name': list_name}).scalar_one()
        current = conn.execute(text("select symbol from ifa2.focus_list_items where list_id=cast(:id as uuid) order by priority"), {'id': str(list_id)}).fetchall()
        current_symbols = [r[0] for r in current]
        desired = universe.get(spec['asset_category'], [])[:spec['target_size']]
        conn.execute(text("delete from ifa2.focus_list_items where list_id=cast(:id as uuid)"), {'id': str(list_id)})
        for i, sym in enumerate(desired, start=1):
            conn.execute(text("insert into ifa2.focus_list_items (id, list_id, symbol, name, asset_category, priority, source, notes, is_active, created_at, updated_at) values (cast(:id as uuid), cast(:list_id as uuid), :symbol, :name, :asset_category, :priority, 'coverage_improvement_2026-04-16', '', true, now(), now())"), {'id': str(uuid4()), 'list_id': str(list_id), 'symbol': sym, 'name': sym, 'asset_category': spec['asset_category'], 'priority': i})
        payload['lists'].append({'list_name': list_name, 'asset_category': spec['asset_category'], 'target_size': spec['target_size'], 'before_count': len(current_symbols), 'after_count': len(desired), 'symbols': desired, 'unresolved_count': max(0, spec['target_size'] - len(desired))})
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
print(OUT)
