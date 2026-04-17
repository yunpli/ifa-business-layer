from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp')
queries = [
    ("history_tables", "select table_name from information_schema.tables where table_schema='ifa2' and (table_name ilike '%futures%' or table_name ilike '%commodity%' or table_name ilike '%precious%') order by table_name"),
    ("all_focus_non_equity", "select distinct symbol from ifa2.focus_list_items where asset_category in ('futures','commodity','precious_metal') order by symbol"),
    ("archive_runs_recent", "select distinct dataset_name from ifa2.archive_runs order by dataset_name"),
]
with engine.begin() as conn:
    for name, sql in queries:
        print('---', name, '---')
        for row in conn.execute(text(sql)).fetchall():
            print(row[0])
    for table in ['futures_history','futures_15min_history','futures_minute_history','futures_60min_history','commodity_15min_history','commodity_minute_history','commodity_60min_history','precious_metal_15min_history','precious_metal_minute_history','precious_metal_60min_history']:
        print('--- sample', table, '---')
        try:
            rows = conn.execute(text(f'select distinct ts_code from ifa2."{table}" order by ts_code limit 80')).fetchall()
            for r in rows:
                print(r[0])
        except Exception as e:
            print('ERR', e)
