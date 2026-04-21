from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .constants import (
    ASSET_CATEGORY_AGRI,
    ASSET_CATEGORY_BASE_METAL,
    ASSET_CATEGORY_BLACK_CHAIN,
    ASSET_CATEGORY_CHEMICALS,
    ASSET_CATEGORY_ENERGY,
    ASSET_CATEGORY_MACRO,
    ASSET_CATEGORY_PRECIOUS_METAL,
    ASSET_CATEGORY_STOCK,
    ASSET_CATEGORY_TECH,
    FREQ_15MIN,
    FREQ_DAILY,
    FREQ_MINUTE,
    FREQ_NONE,
    LIST_TYPE_ARCHIVE_TARGETS,
    LIST_TYPE_FOCUS,
    LIST_TYPE_KEY_FOCUS,
    OWNER_ID_DEFAULT,
    OWNER_TYPE_DEFAULT,
)


@dataclass(frozen=True)
class ListSpec:
    name: str
    list_type: str
    asset_type: str
    frequency_type: str
    description: str
    items: list[dict]
    rules: dict[str, str]


def _macro_items() -> list[tuple[str, str, str]]:
    return [
        ("CN_CPI", "中国CPI", ASSET_CATEGORY_MACRO),
        ("CN_PPI", "中国PPI", ASSET_CATEGORY_MACRO),
        ("CN_PMI", "中国制造业PMI", ASSET_CATEGORY_MACRO),
        ("CN_M2", "中国M2", ASSET_CATEGORY_MACRO),
        ("CN_SOCIAL_FINANCING", "中国社融", ASSET_CATEGORY_MACRO),
        ("CN_EXPORT", "中国出口", ASSET_CATEGORY_MACRO),
        ("CN_IMPORT", "中国进口", ASSET_CATEGORY_MACRO),
        ("US_CPI", "美国CPI", ASSET_CATEGORY_MACRO),
        ("US_NFP", "美国非农", ASSET_CATEGORY_MACRO),
        ("US_FED_FUNDS", "美联储利率", ASSET_CATEGORY_MACRO),
    ]


def _preferred_stock_symbols() -> list[tuple[str, str, str]]:
    return [
        ("000001.SZ", "平安银行", ASSET_CATEGORY_STOCK),
        ("000333.SZ", "美的集团", ASSET_CATEGORY_STOCK),
        ("000651.SZ", "格力电器", ASSET_CATEGORY_STOCK),
        ("000977.SZ", "浪潮信息", ASSET_CATEGORY_STOCK),
        ("002230.SZ", "科大讯飞", ASSET_CATEGORY_STOCK),
        ("002415.SZ", "海康威视", ASSET_CATEGORY_STOCK),
        ("002594.SZ", "比亚迪", ASSET_CATEGORY_STOCK),
        ("002714.SZ", "牧原股份", ASSET_CATEGORY_STOCK),
        ("300033.SZ", "同花顺", ASSET_CATEGORY_STOCK),
        ("300308.SZ", "中际旭创", ASSET_CATEGORY_STOCK),
        ("300502.SZ", "新易盛", ASSET_CATEGORY_STOCK),
        ("300750.SZ", "宁德时代", ASSET_CATEGORY_STOCK),
        ("600036.SH", "招商银行", ASSET_CATEGORY_STOCK),
        ("600150.SH", "中国船舶", ASSET_CATEGORY_STOCK),
        ("600276.SH", "恒瑞医药", ASSET_CATEGORY_STOCK),
        ("600519.SH", "贵州茅台", ASSET_CATEGORY_STOCK),
        ("600570.SH", "恒生电子", ASSET_CATEGORY_STOCK),
        ("600809.SH", "山西汾酒", ASSET_CATEGORY_STOCK),
        ("600900.SH", "长江电力", ASSET_CATEGORY_STOCK),
        ("601012.SH", "隆基绿能", ASSET_CATEGORY_STOCK),
        ("601318.SH", "中国平安", ASSET_CATEGORY_STOCK),
        ("601398.SH", "工商银行", ASSET_CATEGORY_STOCK),
        ("601668.SH", "中国建筑", ASSET_CATEGORY_STOCK),
        ("601899.SH", "紫金矿业", ASSET_CATEGORY_STOCK),
        ("601888.SH", "中国中免", ASSET_CATEGORY_STOCK),
        ("603019.SH", "中科曙光", ASSET_CATEGORY_STOCK),
        ("603259.SH", "药明康德", ASSET_CATEGORY_STOCK),
        ("603501.SH", "韦尔股份", ASSET_CATEGORY_STOCK),
        ("603986.SH", "兆易创新", ASSET_CATEGORY_STOCK),
        ("688041.SH", "海光信息", ASSET_CATEGORY_STOCK),
        ("688111.SH", "金山办公", ASSET_CATEGORY_STOCK),
        ("688256.SH", "寒武纪", ASSET_CATEGORY_STOCK),
        ("688981.SH", "中芯国际", ASSET_CATEGORY_STOCK),
    ]


def _tech_stock_symbols() -> list[tuple[str, str, str]]:
    return [
        ("000063.SZ", "中兴通讯", ASSET_CATEGORY_TECH),
        ("000725.SZ", "京东方A", ASSET_CATEGORY_TECH),
        ("000938.SZ", "紫光股份", ASSET_CATEGORY_TECH),
        ("000977.SZ", "浪潮信息", ASSET_CATEGORY_TECH),
        ("002049.SZ", "紫光国微", ASSET_CATEGORY_TECH),
        ("002156.SZ", "通富微电", ASSET_CATEGORY_TECH),
        ("002230.SZ", "科大讯飞", ASSET_CATEGORY_TECH),
        ("002371.SZ", "北方华创", ASSET_CATEGORY_TECH),
        ("002415.SZ", "海康威视", ASSET_CATEGORY_TECH),
        ("002463.SZ", "沪电股份", ASSET_CATEGORY_TECH),
        ("002475.SZ", "立讯精密", ASSET_CATEGORY_TECH),
        ("002594.SZ", "比亚迪", ASSET_CATEGORY_TECH),
        ("300033.SZ", "同花顺", ASSET_CATEGORY_TECH),
        ("300059.SZ", "东方财富", ASSET_CATEGORY_TECH),
        ("300223.SZ", "北京君正", ASSET_CATEGORY_TECH),
        ("300308.SZ", "中际旭创", ASSET_CATEGORY_TECH),
        ("300394.SZ", "天孚通信", ASSET_CATEGORY_TECH),
        ("300418.SZ", "昆仑万维", ASSET_CATEGORY_TECH),
        ("300442.SZ", "润泽科技", ASSET_CATEGORY_TECH),
        ("300454.SZ", "深信服", ASSET_CATEGORY_TECH),
        ("300496.SZ", "中科创达", ASSET_CATEGORY_TECH),
        ("300502.SZ", "新易盛", ASSET_CATEGORY_TECH),
        ("300604.SZ", "长川科技", ASSET_CATEGORY_TECH),
        ("300750.SZ", "宁德时代", ASSET_CATEGORY_TECH),
        ("301236.SZ", "软通动力", ASSET_CATEGORY_TECH),
        ("301269.SZ", "华大九天", ASSET_CATEGORY_TECH),
        ("600460.SH", "士兰微", ASSET_CATEGORY_TECH),
        ("600570.SH", "恒生电子", ASSET_CATEGORY_TECH),
        ("600584.SH", "长电科技", ASSET_CATEGORY_TECH),
        ("600745.SH", "闻泰科技", ASSET_CATEGORY_TECH),
        ("600845.SH", "宝信软件", ASSET_CATEGORY_TECH),
        ("603019.SH", "中科曙光", ASSET_CATEGORY_TECH),
        ("603160.SH", "汇顶科技", ASSET_CATEGORY_TECH),
        ("603501.SH", "韦尔股份", ASSET_CATEGORY_TECH),
        ("603893.SH", "瑞芯微", ASSET_CATEGORY_TECH),
        ("603986.SH", "兆易创新", ASSET_CATEGORY_TECH),
        ("688008.SH", "澜起科技", ASSET_CATEGORY_TECH),
        ("688012.SH", "中微公司", ASSET_CATEGORY_TECH),
        ("688041.SH", "海光信息", ASSET_CATEGORY_TECH),
        ("688072.SH", "拓荆科技", ASSET_CATEGORY_TECH),
        ("688099.SH", "晶晨股份", ASSET_CATEGORY_TECH),
        ("688111.SH", "金山办公", ASSET_CATEGORY_TECH),
        ("688169.SH", "石头科技", ASSET_CATEGORY_TECH),
        ("688220.SH", "翱捷科技", ASSET_CATEGORY_TECH),
        ("688256.SH", "寒武纪", ASSET_CATEGORY_TECH),
        ("688396.SH", "华润微", ASSET_CATEGORY_TECH),
        ("688521.SH", "芯原股份", ASSET_CATEGORY_TECH),
        ("688608.SH", "恒玄科技", ASSET_CATEGORY_TECH),
        ("688777.SH", "中控技术", ASSET_CATEGORY_TECH),
        ("688981.SH", "中芯国际", ASSET_CATEGORY_TECH),
    ]


def _asset_items() -> list[tuple[str, str, str]]:
    return [
        ("AU0", "沪金主连", ASSET_CATEGORY_PRECIOUS_METAL),
        ("AG0", "沪银主连", ASSET_CATEGORY_PRECIOUS_METAL),
        ("CU0", "沪铜主连", ASSET_CATEGORY_BASE_METAL),
        ("AL0", "沪铝主连", ASSET_CATEGORY_BASE_METAL),
        ("ZN0", "沪锌主连", ASSET_CATEGORY_BASE_METAL),
        ("SC0", "原油主连", ASSET_CATEGORY_ENERGY),
        ("FU0", "燃油主连", ASSET_CATEGORY_ENERGY),
        ("RB0", "螺纹钢主连", ASSET_CATEGORY_BLACK_CHAIN),
        ("HC0", "热卷主连", ASSET_CATEGORY_BLACK_CHAIN),
        ("I0", "铁矿石主连", ASSET_CATEGORY_BLACK_CHAIN),
        ("JM0", "焦煤主连", ASSET_CATEGORY_BLACK_CHAIN),
        ("M0", "豆粕主连", ASSET_CATEGORY_AGRI),
        ("Y0", "豆油主连", ASSET_CATEGORY_AGRI),
        ("C0", "玉米主连", ASSET_CATEGORY_AGRI),
        ("CF0", "棉花主连", ASSET_CATEGORY_AGRI),
        ("TA0", "PTA主连", ASSET_CATEGORY_CHEMICALS),
        ("MA0", "甲醇主连", ASSET_CATEGORY_CHEMICALS),
        ("PP0", "聚丙烯主连", ASSET_CATEGORY_CHEMICALS),
        ("RU0", "橡胶主连", ASSET_CATEGORY_CHEMICALS),
        ("SA0", "纯碱主连", ASSET_CATEGORY_CHEMICALS),
    ]


def build_stock_pool(db_stock_candidates: Iterable[dict]) -> list[tuple[str, str, str]]:
    seen = set()
    result: list[tuple[str, str, str]] = []
    for symbol, name, category in _preferred_stock_symbols():
        if symbol not in seen:
            result.append((symbol, name, category))
            seen.add(symbol)
    for row in db_stock_candidates:
        symbol = row["symbol"]
        name = row["name"]
        if symbol.endswith((".SH", ".SZ", ".BJ")) and symbol not in seen:
            result.append((symbol, name, ASSET_CATEGORY_STOCK))
            seen.add(symbol)
    return result


def _dedupe_items(items: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    seen: set[str] = set()
    out: list[tuple[str, str, str]] = []
    for symbol, name, category in items:
        if symbol in seen:
            continue
        seen.add(symbol)
        out.append((symbol, name, category))
    return out


def _items_with_priority(items: list[tuple[str, str, str]], start: int = 1) -> list[dict]:
    return [
        {
            "symbol": symbol,
            "name": name,
            "asset_category": category,
            "priority": i,
            "source": "default_seed_v2",
            "notes": "",
        }
        for i, (symbol, name, category) in enumerate(_dedupe_items(items), start=start)
    ]


def build_default_specs(db_stock_candidates: Iterable[dict]) -> list[ListSpec]:
    stocks = build_stock_pool(db_stock_candidates)
    macros = _macro_items()
    tech_stocks = _tech_stock_symbols()
    assets = _asset_items()

    stock_key_focus_items = _items_with_priority(stocks[:20])
    stock_focus_items = _items_with_priority(stocks[:80])
    macro_key_focus_items = _items_with_priority(macros[:5])
    macro_focus_items = _items_with_priority(macros[:10])
    tech_key_focus_items = _items_with_priority(tech_stocks[:20])
    tech_focus_items = _items_with_priority(tech_stocks[:50])
    asset_key_focus_items = _items_with_priority(assets[:12])
    asset_focus_items = _items_with_priority(assets)

    minute_items = _items_with_priority(stocks[:8] + tech_stocks[:6] + assets[:6])
    m15_items = _items_with_priority(stocks[:16] + tech_stocks[:12] + assets[:12])
    daily_items = _items_with_priority(stocks[:120] + tech_stocks[:30] + macros[:10] + assets)

    return [
        ListSpec(
            name="default_stock_key_focus",
            list_type=LIST_TYPE_KEY_FOCUS,
            asset_type="stock",
            frequency_type=FREQ_NONE,
            description="Default owner stock key focus list",
            items=stock_key_focus_items,
            rules={"target_size": "20", "owner_scope": OWNER_ID_DEFAULT, "seed_origin": "a_share_only_tushare_supported"},
        ),
        ListSpec(
            name="default_stock_focus",
            list_type=LIST_TYPE_FOCUS,
            asset_type="stock",
            frequency_type=FREQ_NONE,
            description="Default owner stock focus list",
            items=stock_focus_items,
            rules={"target_size": "80", "owner_scope": OWNER_ID_DEFAULT, "seed_origin": "a_share_only_tushare_supported"},
        ),
        ListSpec(
            name="default_macro_key_focus",
            list_type=LIST_TYPE_KEY_FOCUS,
            asset_type="macro",
            frequency_type=FREQ_NONE,
            description="Default owner macro key focus list",
            items=macro_key_focus_items,
            rules={"target_size": "5", "owner_scope": OWNER_ID_DEFAULT},
        ),
        ListSpec(
            name="default_macro_focus",
            list_type=LIST_TYPE_FOCUS,
            asset_type="macro",
            frequency_type=FREQ_NONE,
            description="Default owner macro focus list",
            items=macro_focus_items,
            rules={"target_size": "10", "owner_scope": OWNER_ID_DEFAULT},
        ),
        ListSpec(
            name="default_tech_key_focus",
            list_type=LIST_TYPE_KEY_FOCUS,
            asset_type="tech",
            frequency_type=FREQ_NONE,
            description="Default owner technology key focus list",
            items=tech_key_focus_items,
            rules={"target_size": "20", "owner_scope": OWNER_ID_DEFAULT, "theme": "technology", "underlying_asset": "stock"},
        ),
        ListSpec(
            name="default_tech_focus",
            list_type=LIST_TYPE_FOCUS,
            asset_type="tech",
            frequency_type=FREQ_NONE,
            description="Default owner technology focus list",
            items=tech_focus_items,
            rules={"target_size": "50", "owner_scope": OWNER_ID_DEFAULT, "theme": "technology", "underlying_asset": "stock"},
        ),
        ListSpec(
            name="default_asset_key_focus",
            list_type=LIST_TYPE_KEY_FOCUS,
            asset_type="asset",
            frequency_type=FREQ_NONE,
            description="Default owner asset key focus list using rolling canonical contracts",
            items=asset_key_focus_items,
            rules={
                "target_size": "12",
                "owner_scope": OWNER_ID_DEFAULT,
                "identity_strategy": "rolling_canonical_contract",
                "sub_buckets": "precious_metal,base_metal,energy,black_chain,agri,chemicals",
            },
        ),
        ListSpec(
            name="default_asset_focus",
            list_type=LIST_TYPE_FOCUS,
            asset_type="asset",
            frequency_type=FREQ_NONE,
            description="Default owner asset focus list using rolling canonical contracts",
            items=asset_focus_items,
            rules={
                "target_size": str(len(asset_focus_items)),
                "owner_scope": OWNER_ID_DEFAULT,
                "identity_strategy": "rolling_canonical_contract",
                "sub_buckets": "precious_metal,base_metal,energy,black_chain,agri,chemicals",
            },
        ),
        ListSpec(
            name="default_archive_targets_minute",
            list_type=LIST_TYPE_ARCHIVE_TARGETS,
            asset_type="multi_asset",
            frequency_type=FREQ_MINUTE,
            description="Default minute archive targets",
            items=minute_items,
            rules={"target_size": str(len(minute_items)), "granularity": "minute"},
        ),
        ListSpec(
            name="default_archive_targets_15min",
            list_type=LIST_TYPE_ARCHIVE_TARGETS,
            asset_type="multi_asset",
            frequency_type=FREQ_15MIN,
            description="Default 15min archive targets",
            items=m15_items,
            rules={"target_size": str(len(m15_items)), "granularity": "15min"},
        ),
        ListSpec(
            name="default_archive_targets_daily",
            list_type=LIST_TYPE_ARCHIVE_TARGETS,
            asset_type="multi_asset",
            frequency_type=FREQ_DAILY,
            description="Default daily archive targets",
            items=daily_items,
            rules={"target_size": str(len(daily_items)), "granularity": "daily"},
        ),
    ]


def expected_default_list_names() -> set[str]:
    return {spec.name for spec in build_default_specs([])}
