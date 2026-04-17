from __future__ import annotations

import json
from pathlib import Path
from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp')
OUT = Path('artifacts/contract_identity_roll_2026-04-16_1828.json')
ROOTS = ['AU', 'AG', 'HC', 'NI', 'CU', 'AL', 'ZN', 'RB', 'I', 'J', 'JM', 'MA', 'TA', 'RU']

payload = {'roots': {}}
with engine.begin() as conn:
    for root in ROOTS:
        payload['roots'][root] = {}
        for table in ['futures_history', 'commodity_15min_history', 'commodity_minute_history', 'commodity_60min_history', 'precious_metal_15min_history', 'precious_metal_minute_history', 'precious_metal_60min_history']:
            try:
                rows = conn.execute(text(f"select distinct ts_code from ifa2.\"{table}\" where ts_code like :pat order by ts_code"), {'pat': f'{root}%'}).fetchall()
                payload['roots'][root][table] = [r[0] for r in rows]
            except Exception:
                payload['roots'][root][table] = []
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
print(OUT)
