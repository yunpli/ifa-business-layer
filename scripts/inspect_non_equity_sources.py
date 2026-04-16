from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp')
with engine.begin() as conn:
    queries = [
        ("archive_target_symbols", "select distinct symbol from ifa2.focus_list_items where asset_category in ('futures','commodity','precious_metal') order by symbol limit 200"),
        ("futures_history_symbols", "select distinct ts_code from ifa2.futures_history order by ts_code limit 200"),
        ("futures_15min_symbols", "select distinct ts_code from ifa2.futures_15min_history order by ts_code limit 200"),
        ("futures_minute_symbols", "select distinct ts_code from ifa2.futures_minute_history order by ts_code limit 200"),
        ("commodity_15min_symbols", "select distinct ts_code from ifa2.commodity_15min_history order by ts_code limit 200"),
        ("commodity_minute_symbols", "select distinct ts_code from ifa2.commodity_minute_history order by ts_code limit 200"),
        ("pm_15min_symbols", "select distinct ts_code from ifa2.precious_metal_15min_history order by ts_code limit 200"),
        ("pm_minute_symbols", "select distinct ts_code from ifa2.precious_metal_minute_history order by ts_code limit 200"),
    ]
    for name, sql in queries:
        print('---', name, '---')
        rows = conn.execute(text(sql)).fetchall()
        for r in rows[:40]:
            print(r[0])
