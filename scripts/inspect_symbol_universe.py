from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp')
with engine.begin() as conn:
    cols = conn.execute(text(
        "select column_name, data_type from information_schema.columns where table_schema='ifa2' and table_name='symbol_universe' order by ordinal_position"
    )).fetchall()
    print(cols)
    rows = conn.execute(text("select * from ifa2.symbol_universe limit 5")).mappings().all()
    for r in rows:
        print(dict(r))
