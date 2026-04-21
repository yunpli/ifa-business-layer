from __future__ import annotations

import json
import subprocess
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy import text

REPO = Path('/Users/neoclaw/repos/ifa-business-layer')
PYTHON = Path('/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python')
DB_URL = 'postgresql+psycopg2://neoclaw@/ifa_db?host=/tmp'


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {
        'PYTHONPATH': str(REPO),
        'DATABASE_URL': DB_URL,
        'IFA_DB_SCHEMA': 'ifa2',
    }
    return subprocess.run(
        [str(PYTHON), str(REPO / 'scripts' / 'focus_cli.py'), *args],
        cwd=str(REPO),
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def engine():
    return sa.create_engine(DB_URL, future=True)


def test_phase1_schema_default_seed_and_cli_crud():
    run_cli('init-schema')
    run_cli('seed-default')

    with engine().begin() as conn:
        conn.execute(text("delete from ifa2.focus_list_items where list_id in (select id from ifa2.focus_lists where owner_type='test' and owner_id='phase1')"))
        conn.execute(text("delete from ifa2.focus_list_rules where list_id in (select id from ifa2.focus_lists where owner_type='test' and owner_id='phase1')"))
        conn.execute(text("delete from ifa2.focus_lists where owner_type='test' and owner_id='phase1'"))
        conn.execute(text("delete from ifa2.focus_list_items where list_id in (select id from ifa2.focus_lists where owner_type='default' and owner_id='default')"))
        conn.execute(text("delete from ifa2.focus_list_rules where list_id in (select id from ifa2.focus_lists where owner_type='default' and owner_id='default')"))
        conn.execute(text("delete from ifa2.focus_lists where owner_type='default' and owner_id='default'"))

    run_cli('seed-default')

    with engine().connect() as conn:
        rows = conn.execute(text("""
            select owner_type, owner_id, list_type, name, frequency_type, asset_type
            from ifa2.focus_lists
            where owner_type='default' and owner_id='default'
            order by list_type, frequency_type, name
        """)).fetchall()
        assert len(rows) == 11

        counts = dict(conn.execute(text("""
            select fl.name, count(*)
            from ifa2.focus_lists fl
            join ifa2.focus_list_items fli on fli.list_id = fl.id
            where fl.owner_type='default' and fl.owner_id='default'
            group by fl.name
        """)).fetchall())
        assert counts['default_stock_key_focus'] == 20
        assert counts['default_stock_focus'] == 80
        assert counts['default_macro_key_focus'] == 5
        assert counts['default_macro_focus'] == 10
        assert counts['default_tech_key_focus'] == 20
        assert counts['default_tech_focus'] == 50
        assert counts['default_asset_key_focus'] == 12
        assert counts['default_asset_focus'] == 20
        assert counts['default_archive_targets_minute'] == 19
        assert counts['default_archive_targets_15min'] == 36
        assert counts['default_archive_targets_daily'] == 170

        categories = dict(conn.execute(text("""
            select fl.name, string_agg(distinct fli.asset_category, ',' order by fli.asset_category)
            from ifa2.focus_lists fl
            join ifa2.focus_list_items fli on fli.list_id = fl.id
            where fl.owner_type='default' and fl.owner_id='default'
            group by fl.name
        """)).fetchall())
        assert categories['default_stock_key_focus'] == 'stock'
        assert categories['default_stock_focus'] == 'stock'
        assert categories['default_macro_key_focus'] == 'macro'
        assert categories['default_macro_focus'] == 'macro'
        assert categories['default_tech_key_focus'] == 'tech'
        assert categories['default_tech_focus'] == 'tech'
        assert 'agri' in categories['default_asset_focus']
        assert 'chemicals' in categories['default_asset_focus']

        stock_rules = dict(conn.execute(text("""
            select r.rule_key, r.rule_value
            from ifa2.focus_lists fl
            join ifa2.focus_list_rules r on r.list_id = fl.id
            where fl.owner_type='default' and fl.owner_id='default' and fl.name='default_stock_focus'
        """)).fetchall())
        asset_rules = dict(conn.execute(text("""
            select r.rule_key, r.rule_value
            from ifa2.focus_lists fl
            join ifa2.focus_list_rules r on r.list_id = fl.id
            where fl.owner_type='default' and fl.owner_id='default' and fl.name='default_asset_focus'
        """)).fetchall())
        assert stock_rules['seed_origin'] == 'a_share_only_tushare_supported'
        assert asset_rules['identity_strategy'] == 'rolling_canonical_contract'
        assert 'agri' in asset_rules['sub_buckets']
        assert 'chemicals' in asset_rules['sub_buckets']

        legacy = conn.execute(text("""
            select count(*) from ifa2.focus_lists
            where owner_type='default' and owner_id='default'
              and name in ('default_key_focus', 'default_focus', 'tech_key_focus', 'tech_focus')
        """)).scalar_one()
        assert legacy == 0

    run_cli('add-list', '--owner-type', 'test', '--owner-id', 'phase1', '--list-type', 'focus', '--name', 'test_focus', '--asset-type', 'multi_asset', '--frequency-type', 'none', '--description', 'test list')
    run_cli('add-item', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus', '--symbol', 'US_CPI', '--item-name', '美国CPI', '--asset-category', 'macro', '--priority', '1')
    run_cli('add-item', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus', '--symbol', 'AU0', '--item-name', '沪金主连', '--asset-category', 'precious_metal', '--priority', '2')

    payload = json.loads(run_cli('list-items', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus').stdout)
    assert payload['list']['owner_type'] == 'test'
    assert payload['list']['owner_id'] == 'phase1'
    assert len(payload['items']) == 2

    bulk_path = REPO / 'tmp_bulk_items.json'
    bulk_path.write_text(json.dumps([
        {'symbol': '000001.SZ', 'name': '平安银行', 'asset_category': 'stock', 'priority': 3, 'source': 'manual'},
        {'symbol': 'TA0', 'name': 'PTA主连', 'asset_category': 'chemicals', 'priority': 4, 'source': 'manual'},
    ], ensure_ascii=False), encoding='utf-8')
    run_cli('bulk-upsert', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus', '--file', str(bulk_path))

    payload = json.loads(run_cli('list-items', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus').stdout)
    assert len(payload['items']) == 4

    delete_path = REPO / 'tmp_bulk_delete.json'
    delete_path.write_text(json.dumps({'symbols': ['AU0', 'TA0']}, ensure_ascii=False), encoding='utf-8')
    run_cli('bulk-delete', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus', '--file', str(delete_path))
    payload = json.loads(run_cli('list-items', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus').stdout)
    assert len(payload['items']) == 2

    run_cli('delete-item', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus', '--symbol', 'US_CPI')
    payload = json.loads(run_cli('list-items', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus').stdout)
    assert len(payload['items']) == 1

    run_cli('delete-list', '--owner-type', 'test', '--owner-id', 'phase1', '--name', 'test_focus')
    listed = json.loads(run_cli('list-lists', '--owner-type', 'test', '--owner-id', 'phase1').stdout)
    assert listed == []
