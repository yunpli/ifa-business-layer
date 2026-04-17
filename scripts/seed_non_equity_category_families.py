#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4
from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp')
OUT = Path('artifacts/non_equity_category_families_2026-04-16_1830.json')

FAMILIES = {
    'commodity': {
        'key': ('default_commodity_key_focus', 'commodity_key_focus', ['SC0', 'TA2506.ZCE', 'MA2506.ZCE', 'RU2506.SHF']),
        'focus': ('default_commodity_focus', 'commodity_focus', ['SC0', 'TA2506.ZCE', 'MA2506.ZCE', 'RU2506.SHF']),
    },
    'metal': {
        'key': ('default_metal_key_focus', 'metal_key_focus', ['CU0', 'CU2506.SHF', 'AL0', 'AL2506.SHF', 'ZN0', 'ZN2506.SHF', 'NI2506.SHF', 'PB2506.SHF']),
        'focus': ('default_metal_focus', 'metal_focus', ['CU0', 'CU2506.SHF', 'AL0', 'AL2506.SHF', 'ZN0', 'ZN2506.SHF', 'NI2506.SHF', 'PB2506.SHF']),
    },
    'precious_metal': {
        'key': ('default_precious_metal_key_focus', 'precious_metal_key_focus', ['AU0', 'AU2506.SHF', 'AG0', 'AG2506.SHF']),
        'focus': ('default_precious_metal_focus', 'precious_metal_focus', ['AU0', 'AU2506.SHF', 'AG0', 'AG2506.SHF']),
    },
    'black_chain': {
        'key': ('default_black_chain_key_focus', 'black_chain_key_focus', ['RB0', 'RB2506.SHF', 'HC0', 'HC2506.SHF', 'I0', 'I2506.DCE', 'J2506.DCE', 'J2509.DCE', 'JM0', 'JM2506.DCE']),
        'focus': ('default_black_chain_focus', 'black_chain_focus', ['RB0', 'RB2506.SHF', 'HC0', 'HC2506.SHF', 'I0', 'I2506.DCE', 'J2506.DCE', 'J2509.DCE', 'JM0', 'JM2506.DCE']),
    },
}

def upsert_list(conn, list_name, list_type, asset_type, symbols):
    existing = conn.execute(text('select id from ifa2.focus_lists where name=:name'), {'name': list_name}).scalar_one_or_none()
    if existing:
        list_id = str(existing)
        conn.execute(text('delete from ifa2.focus_list_rules where list_id = cast(:id as uuid)'), {'id': list_id})
        conn.execute(text('delete from ifa2.focus_list_items where list_id = cast(:id as uuid)'), {'id': list_id})
        conn.execute(text("update ifa2.focus_lists set list_type=:lt, asset_type=:asset_type, description=:desc, is_active=true, updated_at=now() where id=cast(:id as uuid)"), {'id': list_id, 'lt': list_type, 'asset_type': asset_type, 'desc': f'{list_name} corrected 2026-04-16'})
    else:
        list_id = str(uuid4())
        conn.execute(text("insert into ifa2.focus_lists (id, owner_type, owner_id, list_type, name, asset_type, frequency_type, description, is_active, created_at, updated_at) values (cast(:id as uuid), 'default', 'default', :lt, :name, :asset_type, 'none', :desc, true, now(), now())"), {'id': list_id, 'lt': list_type, 'name': list_name, 'asset_type': asset_type, 'desc': f'{list_name} corrected 2026-04-16'})
    conn.execute(text("insert into ifa2.focus_list_rules (id, list_id, rule_key, rule_value, created_at, updated_at) values (cast(:id1 as uuid), cast(:list_id as uuid), 'identity_strategy', 'root_or_rolling_contract', now(), now()), (cast(:id2 as uuid), cast(:list_id as uuid), 'target_size', :sz, now(), now())"), {'id1': str(uuid4()), 'id2': str(uuid4()), 'list_id': list_id, 'sz': str(len(symbols))})
    for i, sym in enumerate(symbols, start=1):
        conn.execute(text("insert into ifa2.focus_list_items (id, list_id, symbol, name, asset_category, priority, source, notes, is_active, created_at, updated_at) values (cast(:id as uuid), cast(:list_id as uuid), :symbol, :name, :asset_category, :priority, 'bl_category_correction_2026-04-16', '', true, now(), now())"), {'id': str(uuid4()), 'list_id': list_id, 'symbol': sym, 'name': sym, 'asset_category': asset_type, 'priority': i})
    return list_id

payload = {'families': []}
with engine.begin() as conn:
    for category, spec in FAMILIES.items():
        for mode in ['key', 'focus']:
            list_name, list_type, symbols = spec[mode]
            upsert_list(conn, list_name, list_type, category, symbols)
            payload['families'].append({'category': category, 'mode': mode, 'list_name': list_name, 'count': len(symbols), 'symbols': symbols})
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
print(OUT)
