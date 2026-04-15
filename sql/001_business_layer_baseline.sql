CREATE SCHEMA IF NOT EXISTS ifa2;

CREATE TABLE IF NOT EXISTS ifa2.focus_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_type TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    list_type TEXT NOT NULL,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    frequency_type TEXT NOT NULL DEFAULT 'none',
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(owner_type, owner_id, list_type, name, asset_type, frequency_type)
);

CREATE TABLE IF NOT EXISTS ifa2.focus_list_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    list_id UUID NOT NULL REFERENCES ifa2.focus_lists(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    asset_category TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    source TEXT NOT NULL DEFAULT 'default',
    notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(list_id, symbol)
);

CREATE TABLE IF NOT EXISTS ifa2.focus_list_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    list_id UUID NOT NULL REFERENCES ifa2.focus_lists(id) ON DELETE CASCADE,
    rule_key TEXT NOT NULL,
    rule_value TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(list_id, rule_key)
);

CREATE INDEX IF NOT EXISTS idx_focus_lists_owner ON ifa2.focus_lists(owner_type, owner_id, list_type);
CREATE INDEX IF NOT EXISTS idx_focus_list_items_list ON ifa2.focus_list_items(list_id, priority, symbol);
CREATE INDEX IF NOT EXISTS idx_focus_list_items_category ON ifa2.focus_list_items(asset_category, symbol);
