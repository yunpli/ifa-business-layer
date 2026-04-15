#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ifa_business_layer.constants import OWNER_ID_DEFAULT, OWNER_TYPE_DEFAULT
from ifa_business_layer.defaults import build_default_specs
from ifa_business_layer.repository import BusinessLayerRepository
from ifa_business_layer.schema import create_schema


def _repo() -> BusinessLayerRepository:
    return BusinessLayerRepository()


def cmd_init_schema(args):
    create_schema()
    print("schema_initialized")


def cmd_seed_default(args):
    repo = _repo()
    create_schema()
    stock_candidates = repo.fetch_stock_candidates(limit=400)
    for spec in build_default_specs(stock_candidates):
        list_id = repo.upsert_list(
            owner_type=OWNER_TYPE_DEFAULT,
            owner_id=OWNER_ID_DEFAULT,
            list_type=spec.list_type,
            name=spec.name,
            asset_type=spec.asset_type,
            frequency_type=spec.frequency_type,
            description=spec.description,
        )
        for k, v in spec.rules.items():
            repo.upsert_rule(list_id=list_id, rule_key=k, rule_value=v)
        repo.bulk_upsert_items(list_id, spec.items)
        print(json.dumps({"name": spec.name, "list_id": list_id, "items": len(spec.items)}, ensure_ascii=False))


def cmd_list_lists(args):
    rows = _repo().list_lists(owner_type=args.owner_type, owner_id=args.owner_id)
    print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))


def cmd_list_items(args):
    target = _repo().get_list(owner_type=args.owner_type, owner_id=args.owner_id, name=args.name)
    if not target:
        raise SystemExit("list_not_found")
    payload = {
        "list": target,
        "rules": _repo().list_rules(target["id"]),
        "items": _repo().list_items(target["id"]),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def cmd_add_list(args):
    list_id = _repo().upsert_list(
        owner_type=args.owner_type,
        owner_id=args.owner_id,
        list_type=args.list_type,
        name=args.name,
        asset_type=args.asset_type,
        frequency_type=args.frequency_type,
        description=args.description,
        is_active=not args.inactive,
    )
    print(list_id)


def cmd_delete_list(args):
    print(_repo().delete_list(owner_type=args.owner_type, owner_id=args.owner_id, name=args.name))


def cmd_add_item(args):
    target = _repo().get_list(owner_type=args.owner_type, owner_id=args.owner_id, name=args.name)
    if not target:
        raise SystemExit("list_not_found")
    row_id = _repo().upsert_item(
        list_id=target["id"],
        symbol=args.symbol,
        name=args.item_name,
        asset_category=args.asset_category,
        priority=args.priority,
        source=args.source,
        notes=args.notes,
        is_active=not args.inactive,
    )
    print(row_id)


def cmd_delete_item(args):
    target = _repo().get_list(owner_type=args.owner_type, owner_id=args.owner_id, name=args.name)
    if not target:
        raise SystemExit("list_not_found")
    print(_repo().delete_item(list_id=target["id"], symbol=args.symbol))


def cmd_bulk_upsert(args):
    target = _repo().get_list(owner_type=args.owner_type, owner_id=args.owner_id, name=args.name)
    if not target:
        raise SystemExit("list_not_found")
    items = json.loads(Path(args.file).read_text())
    ids = _repo().bulk_upsert_items(target["id"], items)
    print(json.dumps({"count": len(ids)}, ensure_ascii=False))


def cmd_bulk_delete(args):
    target = _repo().get_list(owner_type=args.owner_type, owner_id=args.owner_id, name=args.name)
    if not target:
        raise SystemExit("list_not_found")
    payload = json.loads(Path(args.file).read_text())
    deleted = _repo().bulk_delete_items(list_id=target["id"], symbols=payload["symbols"])
    print(json.dumps({"deleted": deleted}, ensure_ascii=False))


def build_parser():
    p = argparse.ArgumentParser(description="Business-layer focus list maintenance CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init-schema"); s.set_defaults(func=cmd_init_schema)
    s = sub.add_parser("seed-default"); s.set_defaults(func=cmd_seed_default)

    s = sub.add_parser("list-lists")
    s.add_argument("--owner-type", default=None)
    s.add_argument("--owner-id", default=None)
    s.set_defaults(func=cmd_list_lists)

    s = sub.add_parser("list-items")
    s.add_argument("--owner-type", default=OWNER_TYPE_DEFAULT)
    s.add_argument("--owner-id", default=OWNER_ID_DEFAULT)
    s.add_argument("--name", required=True)
    s.set_defaults(func=cmd_list_items)

    s = sub.add_parser("add-list")
    s.add_argument("--owner-type", default=OWNER_TYPE_DEFAULT)
    s.add_argument("--owner-id", default=OWNER_ID_DEFAULT)
    s.add_argument("--list-type", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--asset-type", default="multi_asset")
    s.add_argument("--frequency-type", default="none")
    s.add_argument("--description", default="")
    s.add_argument("--inactive", action="store_true")
    s.set_defaults(func=cmd_add_list)

    s = sub.add_parser("delete-list")
    s.add_argument("--owner-type", default=OWNER_TYPE_DEFAULT)
    s.add_argument("--owner-id", default=OWNER_ID_DEFAULT)
    s.add_argument("--name", required=True)
    s.set_defaults(func=cmd_delete_list)

    s = sub.add_parser("add-item")
    s.add_argument("--owner-type", default=OWNER_TYPE_DEFAULT)
    s.add_argument("--owner-id", default=OWNER_ID_DEFAULT)
    s.add_argument("--name", required=True)
    s.add_argument("--symbol", required=True)
    s.add_argument("--item-name", required=True)
    s.add_argument("--asset-category", required=True)
    s.add_argument("--priority", type=int, default=100)
    s.add_argument("--source", default="manual")
    s.add_argument("--notes", default="")
    s.add_argument("--inactive", action="store_true")
    s.set_defaults(func=cmd_add_item)

    s = sub.add_parser("delete-item")
    s.add_argument("--owner-type", default=OWNER_TYPE_DEFAULT)
    s.add_argument("--owner-id", default=OWNER_ID_DEFAULT)
    s.add_argument("--name", required=True)
    s.add_argument("--symbol", required=True)
    s.set_defaults(func=cmd_delete_item)

    s = sub.add_parser("bulk-upsert")
    s.add_argument("--owner-type", default=OWNER_TYPE_DEFAULT)
    s.add_argument("--owner-id", default=OWNER_ID_DEFAULT)
    s.add_argument("--name", required=True)
    s.add_argument("--file", required=True)
    s.set_defaults(func=cmd_bulk_upsert)

    s = sub.add_parser("bulk-delete")
    s.add_argument("--owner-type", default=OWNER_TYPE_DEFAULT)
    s.add_argument("--owner-id", default=OWNER_ID_DEFAULT)
    s.add_argument("--name", required=True)
    s.add_argument("--file", required=True)
    s.set_defaults(func=cmd_bulk_delete)

    return p


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)
