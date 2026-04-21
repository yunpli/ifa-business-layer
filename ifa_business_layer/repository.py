from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from sqlalchemy import text

from .config import DEFAULT_SCHEMA
from .constants import (
    ALLOWED_ASSET_CATEGORIES,
    ALLOWED_FREQ,
    ALLOWED_LIST_TYPES,
)
from .db import make_engine


@dataclass
class FocusListRow:
    id: str
    owner_type: str
    owner_id: str
    list_type: str
    name: str
    asset_type: str
    frequency_type: str
    description: str | None
    is_active: bool


class BusinessLayerRepository:
    def __init__(self):
        self.engine = make_engine()
        self.schema = DEFAULT_SCHEMA

    def list_lists(self, owner_type: Optional[str] = None, owner_id: Optional[str] = None):
        sql = f"""
        SELECT id, owner_type, owner_id, list_type, name, asset_type, frequency_type, description, is_active
        FROM {self.schema}.focus_lists
        WHERE (:owner_type IS NULL OR owner_type = :owner_type)
          AND (:owner_id IS NULL OR owner_id = :owner_id)
        ORDER BY owner_type, owner_id, list_type, frequency_type, name
        """
        with self.engine.connect() as conn:
            rows = conn.execute(text(sql), {"owner_type": owner_type, "owner_id": owner_id}).mappings().all()
            return [dict(r) for r in rows]

    def get_list(self, *, owner_type: str, owner_id: str, name: str):
        sql = f"""
        SELECT id, owner_type, owner_id, list_type, name, asset_type, frequency_type, description, is_active
        FROM {self.schema}.focus_lists
        WHERE owner_type=:owner_type AND owner_id=:owner_id AND name=:name
        """
        with self.engine.connect() as conn:
            row = conn.execute(text(sql), {"owner_type": owner_type, "owner_id": owner_id, "name": name}).mappings().first()
            return dict(row) if row else None

    def upsert_list(self, *, owner_type: str, owner_id: str, list_type: str, name: str, asset_type: str, frequency_type: str, description: str = "", is_active: bool = True):
        if list_type not in ALLOWED_LIST_TYPES:
            raise ValueError(f"invalid list_type: {list_type}")
        if frequency_type not in ALLOWED_FREQ:
            raise ValueError(f"invalid frequency_type: {frequency_type}")
        sql = f"""
        INSERT INTO {self.schema}.focus_lists (
            owner_type, owner_id, list_type, name, asset_type, frequency_type, description, is_active
        ) VALUES (
            :owner_type, :owner_id, :list_type, :name, :asset_type, :frequency_type, :description, :is_active
        )
        ON CONFLICT (owner_type, owner_id, list_type, name, asset_type, frequency_type)
        DO UPDATE SET description=EXCLUDED.description, is_active=EXCLUDED.is_active, updated_at=now()
        RETURNING id
        """
        with self.engine.begin() as conn:
            list_id = conn.execute(text(sql), {
                "owner_type": owner_type, "owner_id": owner_id, "list_type": list_type,
                "name": name, "asset_type": asset_type, "frequency_type": frequency_type,
                "description": description, "is_active": is_active,
            }).scalar_one()
            return str(list_id)

    def delete_list(self, *, owner_type: str, owner_id: str, name: str):
        sql = f"DELETE FROM {self.schema}.focus_lists WHERE owner_type=:owner_type AND owner_id=:owner_id AND name=:name"
        with self.engine.begin() as conn:
            return conn.execute(text(sql), {"owner_type": owner_type, "owner_id": owner_id, "name": name}).rowcount

    def delete_lists_not_in(self, *, owner_type: str, owner_id: str, allowed_names: Iterable[str], list_types: Iterable[str]):
        sql = f"""
        DELETE FROM {self.schema}.focus_lists
        WHERE owner_type=:owner_type
          AND owner_id=:owner_id
          AND list_type = ANY(:list_types)
          AND NOT (name = ANY(:allowed_names))
        """
        with self.engine.begin() as conn:
            return conn.execute(text(sql), {
                "owner_type": owner_type,
                "owner_id": owner_id,
                "allowed_names": list(allowed_names),
                "list_types": list(list_types),
            }).rowcount

    def list_items(self, list_id: str):
        sql = f"""
        SELECT id, list_id, symbol, name, asset_category, priority, source, notes, is_active
        FROM {self.schema}.focus_list_items
        WHERE list_id=:list_id
        ORDER BY priority, symbol
        """
        with self.engine.connect() as conn:
            return [dict(r) for r in conn.execute(text(sql), {"list_id": list_id}).mappings().all()]

    def upsert_item(self, *, list_id: str, symbol: str, name: str, asset_category: str, priority: int, source: str = "default", notes: str = "", is_active: bool = True):
        if asset_category not in ALLOWED_ASSET_CATEGORIES:
            raise ValueError(f"invalid asset_category: {asset_category}")
        sql = f"""
        INSERT INTO {self.schema}.focus_list_items (
            list_id, symbol, name, asset_category, priority, source, notes, is_active
        ) VALUES (
            :list_id, :symbol, :name, :asset_category, :priority, :source, :notes, :is_active
        )
        ON CONFLICT (list_id, symbol)
        DO UPDATE SET name=EXCLUDED.name, asset_category=EXCLUDED.asset_category,
                      priority=EXCLUDED.priority, source=EXCLUDED.source,
                      notes=EXCLUDED.notes, is_active=EXCLUDED.is_active, updated_at=now()
        RETURNING id
        """
        with self.engine.begin() as conn:
            return str(conn.execute(text(sql), {
                "list_id": list_id, "symbol": symbol, "name": name, "asset_category": asset_category,
                "priority": priority, "source": source, "notes": notes, "is_active": is_active,
            }).scalar_one())

    def replace_items(self, list_id: str, items: Iterable[dict]):
        with self.engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {self.schema}.focus_list_items WHERE list_id=:list_id"), {"list_id": list_id})
            for item in items:
                if item["asset_category"] not in ALLOWED_ASSET_CATEGORIES:
                    raise ValueError(f"invalid asset_category: {item['asset_category']}")
                conn.execute(text(f"""
                    INSERT INTO {self.schema}.focus_list_items (
                        list_id, symbol, name, asset_category, priority, source, notes, is_active
                    ) VALUES (
                        :list_id, :symbol, :name, :asset_category, :priority, :source, :notes, :is_active
                    )
                """), {
                    "list_id": list_id,
                    "symbol": item["symbol"],
                    "name": item["name"],
                    "asset_category": item["asset_category"],
                    "priority": item["priority"],
                    "source": item.get("source", "default"),
                    "notes": item.get("notes", ""),
                    "is_active": item.get("is_active", True),
                })

    def bulk_upsert_items(self, list_id: str, items: Iterable[dict]):
        ids = []
        for item in items:
            ids.append(self.upsert_item(list_id=list_id, **item))
        return ids

    def delete_item(self, *, list_id: str, symbol: str):
        sql = f"DELETE FROM {self.schema}.focus_list_items WHERE list_id=:list_id AND symbol=:symbol"
        with self.engine.begin() as conn:
            return conn.execute(text(sql), {"list_id": list_id, "symbol": symbol}).rowcount

    def bulk_delete_items(self, *, list_id: str, symbols: list[str]):
        if not symbols:
            return 0
        sql = f"DELETE FROM {self.schema}.focus_list_items WHERE list_id=:list_id AND symbol = ANY(:symbols)"
        with self.engine.begin() as conn:
            return conn.execute(text(sql), {"list_id": list_id, "symbols": symbols}).rowcount

    def upsert_rule(self, *, list_id: str, rule_key: str, rule_value: str):
        sql = f"""
        INSERT INTO {self.schema}.focus_list_rules (list_id, rule_key, rule_value)
        VALUES (:list_id, :rule_key, :rule_value)
        ON CONFLICT (list_id, rule_key)
        DO UPDATE SET rule_value=EXCLUDED.rule_value, updated_at=now()
        """
        with self.engine.begin() as conn:
            conn.execute(text(sql), {"list_id": list_id, "rule_key": rule_key, "rule_value": rule_value})

    def replace_rules(self, list_id: str, rules: dict[str, str]):
        with self.engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {self.schema}.focus_list_rules WHERE list_id=:list_id"), {"list_id": list_id})
            for rule_key, rule_value in rules.items():
                conn.execute(text(f"""
                    INSERT INTO {self.schema}.focus_list_rules (list_id, rule_key, rule_value)
                    VALUES (:list_id, :rule_key, :rule_value)
                """), {"list_id": list_id, "rule_key": rule_key, "rule_value": rule_value})

    def list_rules(self, list_id: str):
        sql = f"SELECT rule_key, rule_value FROM {self.schema}.focus_list_rules WHERE list_id=:list_id ORDER BY rule_key"
        with self.engine.connect() as conn:
            return [dict(r) for r in conn.execute(text(sql), {"list_id": list_id}).mappings().all()]

    def fetch_stock_candidates(self, limit: int):
        sql = f"""
        SELECT ts_code AS symbol, name
        FROM {self.schema}.stock_basic_current
        ORDER BY ts_code
        LIMIT :limit
        """
        with self.engine.connect() as conn:
            return [dict(r) for r in conn.execute(text(sql), {"limit": limit}).mappings().all()]
