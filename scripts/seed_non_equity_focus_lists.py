#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text

DB_URL = 'postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp'
engine = create_engine(DB_URL)
OUT = Path('artifacts/non_equity_focus_seed_2026-04-16_1005.json')

LIST_SPECS = [
    ('default_futures_key_focus', 'futures_key_focus', 'futures', 20, ['IF', 'IH', 'IC', 'IM', 'TS', 'TF', 'T', 'TL']),
    ('default_futures_focus', 'futures_focus', 'futures', 40, ['IF', 'IH', 'IC', 'IM', 'TS', 'TF', 'T', 'TL']),
    ('default_commodity_key_focus', 'commodity_key_focus', 'commodity', 20, ['SC', 'LU', 'FU', 'BU', 'CU', 'AL', 'ZN', 'NI', 'SN', 'AO', 'RB', 'HC', 'I', 'J', 'JM', 'TA', 'MA', 'SA', 'FG', 'RU', 'BR', 'NR', 'M', 'Y', 'P', 'OI', 'RM', 'C', 'CS', 'CF', 'SR', 'UR', 'PX', 'PF', 'SH']),
    ('default_commodity_focus', 'commodity_focus', 'commodity', 40, ['SC', 'LU', 'FU', 'BU', 'CU', 'AL', 'ZN', 'NI', 'SN', 'AO', 'RB', 'HC', 'I', 'J', 'JM', 'TA', 'MA', 'SA', 'FG', 'RU', 'BR', 'NR', 'M', 'Y', 'P', 'OI', 'RM', 'C', 'CS', 'CF', 'SR', 'UR', 'PX', 'PF', 'SH']),
    ('default_precious_metal_key_focus', 'precious_metal_key_focus', 'precious_metal', 20, ['AU', 'AG']),
    ('default_precious_metal_focus', 'precious_metal_focus', 'precious_metal', 40, ['AU', 'AG']),
]

CATEGORY_MAP = {
    'futures': 'futures',
    'commodity': 'commodity',
    'precious_metal': 'precious_metal',
}

def fetch_candidates(conn, roots, asset_category):
    rows = conn.execute(text(
        "select symbol, name, asset_category from ifa2.focus_list_items "
        "where asset_category in ('futures','commodity','precious_metal') order by priority, symbol"
    )).mappings().all()
    out = []
    seen = set()
    for r in rows:
        sym = r['symbol']
        if r['asset_category'] != asset_category:
            continue
        for root in roots:
            if sym.startswith(root) and sym not in seen:
                out.append({'symbol': sym, 'name': r['name'], 'asset_category': r['asset_category']})
                seen.add(sym)
                break
    return out

with engine.begin() as conn:
    payload = {'lists': []}
    for list_name, list_type, asset_type, target_size, roots in LIST_SPECS:
        rows = fetch_candidates(conn, roots, CATEGORY_MAP[asset_type])
        inserted_rows = rows[:target_size]
        unresolved_count = max(0, target_size - len(inserted_rows))
        existing = conn.execute(text("select id from ifa2.focus_lists where name=:name"), {'name': list_name}).scalar_one_or_none()
        if existing:
            list_id = str(existing)
            conn.execute(text("delete from ifa2.focus_list_rules where list_id = cast(:id as uuid)"), {'id': list_id})
            conn.execute(text("delete from ifa2.focus_list_items where list_id = cast(:id as uuid)"), {'id': list_id})
            conn.execute(text("update ifa2.focus_lists set list_type=:lt, asset_type=:asset_type, frequency_type='none', description=:desc, is_active=true, updated_at=now() where id=cast(:id as uuid)"), {'id': list_id, 'lt': list_type, 'asset_type': asset_type, 'desc': f'{list_name} seeded 2026-04-16'})
        else:
            list_id = str(uuid4())
            conn.execute(text(
                "insert into ifa2.focus_lists (id, owner_type, owner_id, list_type, name, asset_type, frequency_type, description, is_active, created_at, updated_at) "
                "values (cast(:id as uuid), 'default', 'default', :lt, :name, :asset_type, 'none', :desc, true, now(), now())"
            ), {'id': list_id, 'lt': list_type, 'name': list_name, 'asset_type': asset_type, 'desc': f'{list_name} seeded 2026-04-16'})
        conn.execute(text(
            "insert into ifa2.focus_list_rules (id, list_id, rule_key, rule_value, created_at, updated_at) values "
            "(cast(:id1 as uuid), cast(:list_id as uuid), 'target_size', :target_size, now(), now()), "
            "(cast(:id2 as uuid), cast(:list_id as uuid), 'root_universe', :roots, now(), now())"
        ), {'id1': str(uuid4()), 'id2': str(uuid4()), 'list_id': list_id, 'target_size': str(target_size), 'roots': ','.join(roots)})
        inserted = []
        for i, r in enumerate(inserted_rows, start=1):
            conn.execute(text(
                "insert into ifa2.focus_list_items (id, list_id, symbol, name, asset_category, priority, source, notes, is_active, created_at, updated_at) "
                "values (cast(:id as uuid), cast(:list_id as uuid), :symbol, :name, :asset_category, :priority, 'seed_non_equity_2026-04-16', '', true, now(), now())"
            ), {'id': str(uuid4()), 'list_id': list_id, 'symbol': r['symbol'], 'name': r['name'], 'asset_category': r['asset_category'], 'priority': i})
            inserted.append({'symbol': r['symbol'], 'name': r['name'], 'priority': i})
        payload['lists'].append({'list_name': list_name, 'list_type': list_type, 'asset_type': asset_type, 'roots': roots, 'inserted_count': len(inserted), 'target_size': target_size, 'unresolved_count': unresolved_count, 'inserted': inserted})
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
print(OUT)
