#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text

DB_URL = 'postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp'
engine = create_engine(DB_URL)
OUT = Path('artifacts/non_equity_focus_seed_2026-04-16_1035.json')

LIST_SPECS = [
    ('default_futures_key_focus', 'futures_key_focus', 'futures', 20, ['IF', 'IH', 'IC', 'IM', 'TS', 'TF', 'T', 'TL']),
    ('default_futures_focus', 'futures_focus', 'futures', 40, ['IF', 'IH', 'IC', 'IM', 'TS', 'TF', 'T', 'TL']),
    ('default_commodity_key_focus', 'commodity_key_focus', 'commodity', 20, ['SC', 'LU', 'FU', 'BU', 'TA', 'MA', 'PX', 'PF', 'CU', 'AL', 'ZN', 'NI', 'SN', 'AO', 'RB', 'HC', 'I', 'J', 'JM', 'FG', 'SA', 'SH', 'BR', 'NR', 'RU', 'M', 'Y', 'P', 'OI', 'RM', 'C', 'CS', 'CF', 'SR', 'UR']),
    ('default_commodity_focus', 'commodity_focus', 'commodity', 40, ['SC', 'LU', 'FU', 'BU', 'TA', 'MA', 'PX', 'PF', 'CU', 'AL', 'ZN', 'NI', 'SN', 'AO', 'RB', 'HC', 'I', 'J', 'JM', 'FG', 'SA', 'SH', 'BR', 'NR', 'RU', 'M', 'Y', 'P', 'OI', 'RM', 'C', 'CS', 'CF', 'SR', 'UR']),
    ('default_precious_metal_key_focus', 'precious_metal_key_focus', 'precious_metal', 20, ['AU', 'AG']),
    ('default_precious_metal_focus', 'precious_metal_focus', 'precious_metal', 40, ['AU', 'AG']),
]

SOURCE_QUERIES = [
    ("futures_history", "select distinct ts_code as symbol from ifa2.futures_history"),
    ("futures_15min_history", "select distinct ts_code as symbol from ifa2.futures_15min_history"),
    ("futures_minute_history", "select distinct ts_code as symbol from ifa2.futures_minute_history"),
    ("futures_60min_history", "select distinct ts_code as symbol from ifa2.futures_60min_history"),
    ("commodity_15min_history", "select distinct ts_code as symbol from ifa2.commodity_15min_history"),
    ("commodity_minute_history", "select distinct ts_code as symbol from ifa2.commodity_minute_history"),
    ("commodity_60min_history", "select distinct ts_code as symbol from ifa2.commodity_60min_history"),
    ("precious_metal_15min_history", "select distinct ts_code as symbol from ifa2.precious_metal_15min_history"),
    ("precious_metal_minute_history", "select distinct ts_code as symbol from ifa2.precious_metal_minute_history"),
    ("precious_metal_60min_history", "select distinct ts_code as symbol from ifa2.precious_metal_60min_history"),
    ("archive_targets", "select distinct symbol from ifa2.focus_list_items where asset_category in ('futures','commodity','precious_metal')"),
]

def root_of(symbol: str) -> str:
    out = []
    for ch in symbol:
        if ch.isalpha():
            out.append(ch)
        else:
            break
    return ''.join(out)


def fetch_candidates(conn):
    universe = defaultdict(set)
    for _, sql in SOURCE_QUERIES:
        rows = conn.execute(text(sql)).fetchall()
        for (symbol,) in rows:
            if not symbol:
                continue
            universe[root_of(symbol)].add(symbol)
    return {k: sorted(v) for k, v in universe.items()}

with engine.begin() as conn:
    universe = fetch_candidates(conn)
    payload = {'lists': []}
    for list_name, list_type, asset_type, target_size, roots in LIST_SPECS:
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

        selected = []
        unresolved = []
        for root in roots:
            available = universe.get(root, [])
            if not available:
                unresolved.append({'root': root, 'reason': 'no current DB/runtime contract truth found'})
                continue
            for symbol in available:
                if symbol not in selected:
                    selected.append(symbol)
        selected = selected[:target_size]
        for i, symbol in enumerate(selected, start=1):
            conn.execute(text(
                "insert into ifa2.focus_list_items (id, list_id, symbol, name, asset_category, priority, source, notes, is_active, created_at, updated_at) "
                "values (cast(:id as uuid), cast(:list_id as uuid), :symbol, :name, :asset_category, :priority, 'seed_non_equity_2026-04-16', '', true, now(), now())"
            ), {'id': str(uuid4()), 'list_id': list_id, 'symbol': symbol, 'name': symbol, 'asset_category': asset_type, 'priority': i})
        missing_slots = max(0, target_size - len(selected))
        if missing_slots:
            unresolved.append({'reason': f'only {len(selected)} resolvable symbols available from current DB/runtime truth', 'missing_slots': missing_slots})
        payload['lists'].append({'list_name': list_name, 'list_type': list_type, 'asset_type': asset_type, 'target_size': target_size, 'inserted_count': len(selected), 'unresolved_count': len(unresolved), 'inserted': selected, 'unresolved': unresolved})
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
print(OUT)
