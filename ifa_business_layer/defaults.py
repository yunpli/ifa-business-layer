from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .constants import (
    ASSET_CATEGORY_COMMODITY,
    ASSET_CATEGORY_FUTURES,
    ASSET_CATEGORY_MACRO,
    ASSET_CATEGORY_PRECIOUS_METAL,
    ASSET_CATEGORY_STOCK,
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


def _futures_items() -> list[tuple[str, str, str]]:
    return [
        ("AU0", "沪金主连", ASSET_CATEGORY_PRECIOUS_METAL),
        ("AG0", "沪银主连", ASSET_CATEGORY_PRECIOUS_METAL),
        ("CU0", "沪铜主连", ASSET_CATEGORY_COMMODITY),
        ("AL0", "沪铝主连", ASSET_CATEGORY_COMMODITY),
        ("ZN0", "沪锌主连", ASSET_CATEGORY_COMMODITY),
        ("RB0", "螺纹钢主连", ASSET_CATEGORY_COMMODITY),
        ("HC0", "热卷主连", ASSET_CATEGORY_COMMODITY),
        ("SC0", "原油主连", ASSET_CATEGORY_COMMODITY),
        ("JM0", "焦煤主连", ASSET_CATEGORY_FUTURES),
        ("I0", "铁矿主连", ASSET_CATEGORY_FUTURES),
    ]


def _preferred_stock_symbols() -> list[tuple[str, str, str]]:
    return [
        ("000001.SZ", "平安银行", ASSET_CATEGORY_STOCK),
        ("000002.SZ", "万科A", ASSET_CATEGORY_STOCK),
        ("000063.SZ", "中兴通讯", ASSET_CATEGORY_STOCK),
        ("000333.SZ", "美的集团", ASSET_CATEGORY_STOCK),
        ("000651.SZ", "格力电器", ASSET_CATEGORY_STOCK),
        ("000725.SZ", "京东方A", ASSET_CATEGORY_STOCK),
        ("000977.SZ", "浪潮信息", ASSET_CATEGORY_STOCK),
        ("002230.SZ", "科大讯飞", ASSET_CATEGORY_STOCK),
        ("002415.SZ", "海康威视", ASSET_CATEGORY_STOCK),
        ("002594.SZ", "比亚迪", ASSET_CATEGORY_STOCK),
        ("002714.SZ", "牧原股份", ASSET_CATEGORY_STOCK),
        ("300033.SZ", "同花顺", ASSET_CATEGORY_STOCK),
        ("300308.SZ", "中际旭创", ASSET_CATEGORY_STOCK),
        ("300502.SZ", "新易盛", ASSET_CATEGORY_STOCK),
        ("300750.SZ", "宁德时代", ASSET_CATEGORY_STOCK),
        ("301236.SZ", "软通动力", ASSET_CATEGORY_STOCK),
        ("600036.SH", "招商银行", ASSET_CATEGORY_STOCK),
        ("600150.SH", "中国船舶", ASSET_CATEGORY_STOCK),
        ("600519.SH", "贵州茅台", ASSET_CATEGORY_STOCK),
        ("600570.SH", "恒生电子", ASSET_CATEGORY_STOCK),
        ("600809.SH", "山西汾酒", ASSET_CATEGORY_STOCK),
        ("600900.SH", "长江电力", ASSET_CATEGORY_STOCK),
        ("601012.SH", "隆基绿能", ASSET_CATEGORY_STOCK),
        ("601318.SH", "中国平安", ASSET_CATEGORY_STOCK),
        ("601398.SH", "工商银行", ASSET_CATEGORY_STOCK),
        ("601668.SH", "中国建筑", ASSET_CATEGORY_STOCK),
        ("601899.SH", "紫金矿业", ASSET_CATEGORY_STOCK),
        ("603019.SH", "中科曙光", ASSET_CATEGORY_STOCK),
        ("603259.SH", "药明康德", ASSET_CATEGORY_STOCK),
        ("603986.SH", "兆易创新", ASSET_CATEGORY_STOCK),
        ("688041.SH", "海光信息", ASSET_CATEGORY_STOCK),
        ("688111.SH", "金山办公", ASSET_CATEGORY_STOCK),
        ("688256.SH", "寒武纪", ASSET_CATEGORY_STOCK),
        ("688981.SH", "中芯国际", ASSET_CATEGORY_STOCK),
        ("601888.SH", "中国中免", ASSET_CATEGORY_STOCK),
        ("600276.SH", "恒瑞医药", ASSET_CATEGORY_STOCK),
        ("000858.SZ", "五粮液", ASSET_CATEGORY_STOCK),
        ("002475.SZ", "立讯精密", ASSET_CATEGORY_STOCK),
        ("300274.SZ", "阳光电源", ASSET_CATEGORY_STOCK),
        ("603501.SH", "韦尔股份", ASSET_CATEGORY_STOCK),
    ]


def _tech_stock_symbols() -> list[tuple[str, str, str]]:
    return [
        ("000063.SZ", "中兴通讯", ASSET_CATEGORY_STOCK),
        ("000066.SZ", "中国长城", ASSET_CATEGORY_STOCK),
        ("000725.SZ", "京东方A", ASSET_CATEGORY_STOCK),
        ("000938.SZ", "紫光股份", ASSET_CATEGORY_STOCK),
        ("000977.SZ", "浪潮信息", ASSET_CATEGORY_STOCK),
        ("002049.SZ", "紫光国微", ASSET_CATEGORY_STOCK),
        ("002130.SZ", "沃尔核材", ASSET_CATEGORY_STOCK),
        ("002156.SZ", "通富微电", ASSET_CATEGORY_STOCK),
        ("002230.SZ", "科大讯飞", ASSET_CATEGORY_STOCK),
        ("002236.SZ", "大华股份", ASSET_CATEGORY_STOCK),
        ("002371.SZ", "北方华创", ASSET_CATEGORY_STOCK),
        ("002410.SZ", "广联达", ASSET_CATEGORY_STOCK),
        ("002415.SZ", "海康威视", ASSET_CATEGORY_STOCK),
        ("002436.SZ", "兴森科技", ASSET_CATEGORY_STOCK),
        ("002463.SZ", "沪电股份", ASSET_CATEGORY_STOCK),
        ("002475.SZ", "立讯精密", ASSET_CATEGORY_STOCK),
        ("002527.SZ", "新时达", ASSET_CATEGORY_STOCK),
        ("002555.SZ", "三七互娱", ASSET_CATEGORY_STOCK),
        ("002594.SZ", "比亚迪", ASSET_CATEGORY_STOCK),
        ("002938.SZ", "鹏鼎控股", ASSET_CATEGORY_STOCK),
        ("300002.SZ", "神州泰岳", ASSET_CATEGORY_STOCK),
        ("300017.SZ", "网宿科技", ASSET_CATEGORY_STOCK),
        ("300033.SZ", "同花顺", ASSET_CATEGORY_STOCK),
        ("300059.SZ", "东方财富", ASSET_CATEGORY_STOCK),
        ("300124.SZ", "汇川技术", ASSET_CATEGORY_STOCK),
        ("300223.SZ", "北京君正", ASSET_CATEGORY_STOCK),
        ("300308.SZ", "中际旭创", ASSET_CATEGORY_STOCK),
        ("300316.SZ", "晶盛机电", ASSET_CATEGORY_STOCK),
        ("300339.SZ", "润和软件", ASSET_CATEGORY_STOCK),
        ("300347.SZ", "泰格医药", ASSET_CATEGORY_STOCK),
        ("300394.SZ", "天孚通信", ASSET_CATEGORY_STOCK),
        ("300413.SZ", "芒果超媒", ASSET_CATEGORY_STOCK),
        ("300418.SZ", "昆仑万维", ASSET_CATEGORY_STOCK),
        ("300433.SZ", "蓝思科技", ASSET_CATEGORY_STOCK),
        ("300442.SZ", "润泽科技", ASSET_CATEGORY_STOCK),
        ("300450.SZ", "先导智能", ASSET_CATEGORY_STOCK),
        ("300454.SZ", "深信服", ASSET_CATEGORY_STOCK),
        ("300474.SZ", "景嘉微", ASSET_CATEGORY_STOCK),
        ("300496.SZ", "中科创达", ASSET_CATEGORY_STOCK),
        ("300502.SZ", "新易盛", ASSET_CATEGORY_STOCK),
        ("300567.SZ", "精测电子", ASSET_CATEGORY_STOCK),
        ("300604.SZ", "长川科技", ASSET_CATEGORY_STOCK),
        ("300661.SZ", "圣邦股份", ASSET_CATEGORY_STOCK),
        ("300666.SZ", "江丰电子", ASSET_CATEGORY_STOCK),
        ("300672.SZ", "国科微", ASSET_CATEGORY_STOCK),
        ("300679.SZ", "电连技术", ASSET_CATEGORY_STOCK),
        ("300735.SZ", "光弘科技", ASSET_CATEGORY_STOCK),
        ("300750.SZ", "宁德时代", ASSET_CATEGORY_STOCK),
        ("300757.SZ", "罗博特科", ASSET_CATEGORY_STOCK),
        ("300782.SZ", "卓胜微", ASSET_CATEGORY_STOCK),
        ("300857.SZ", "协创数据", ASSET_CATEGORY_STOCK),
        ("300870.SZ", "欧陆通", ASSET_CATEGORY_STOCK),
        ("300972.SZ", "万辰集团", ASSET_CATEGORY_STOCK),
        ("301236.SZ", "软通动力", ASSET_CATEGORY_STOCK),
        ("301269.SZ", "华大九天", ASSET_CATEGORY_STOCK),
        ("301308.SZ", "江波龙", ASSET_CATEGORY_STOCK),
        ("600183.SH", "生益科技", ASSET_CATEGORY_STOCK),
        ("600460.SH", "士兰微", ASSET_CATEGORY_STOCK),
        ("600570.SH", "恒生电子", ASSET_CATEGORY_STOCK),
        ("600584.SH", "长电科技", ASSET_CATEGORY_STOCK),
        ("600588.SH", "用友网络", ASSET_CATEGORY_STOCK),
        ("600667.SH", "太极实业", ASSET_CATEGORY_STOCK),
        ("600745.SH", "闻泰科技", ASSET_CATEGORY_STOCK),
        ("600845.SH", "宝信软件", ASSET_CATEGORY_STOCK),
        ("601012.SH", "隆基绿能", ASSET_CATEGORY_STOCK),
        ("603005.SH", "晶方科技", ASSET_CATEGORY_STOCK),
        ("603019.SH", "中科曙光", ASSET_CATEGORY_STOCK),
        ("603160.SH", "汇顶科技", ASSET_CATEGORY_STOCK),
        ("603228.SH", "景旺电子", ASSET_CATEGORY_STOCK),
        ("603236.SH", "移远通信", ASSET_CATEGORY_STOCK),
        ("603290.SH", "斯达半导", ASSET_CATEGORY_STOCK),
        ("603338.SH", "浙江鼎力", ASSET_CATEGORY_STOCK),
        ("603501.SH", "韦尔股份", ASSET_CATEGORY_STOCK),
        ("603893.SH", "瑞芯微", ASSET_CATEGORY_STOCK),
        ("603986.SH", "兆易创新", ASSET_CATEGORY_STOCK),
        ("605111.SH", "新洁能", ASSET_CATEGORY_STOCK),
        ("688008.SH", "澜起科技", ASSET_CATEGORY_STOCK),
        ("688012.SH", "中微公司", ASSET_CATEGORY_STOCK),
        ("688018.SH", "乐鑫科技", ASSET_CATEGORY_STOCK),
        ("688036.SH", "传音控股", ASSET_CATEGORY_STOCK),
        ("688041.SH", "海光信息", ASSET_CATEGORY_STOCK),
        ("688047.SH", "龙芯中科", ASSET_CATEGORY_STOCK),
        ("688072.SH", "拓荆科技", ASSET_CATEGORY_STOCK),
        ("688082.SH", "盛美上海", ASSET_CATEGORY_STOCK),
        ("688099.SH", "晶晨股份", ASSET_CATEGORY_STOCK),
        ("688111.SH", "金山办公", ASSET_CATEGORY_STOCK),
        ("688126.SH", "沪硅产业", ASSET_CATEGORY_STOCK),
        ("688169.SH", "石头科技", ASSET_CATEGORY_STOCK),
        ("688187.SH", "时代电气", ASSET_CATEGORY_STOCK),
        ("688200.SH", "华峰测控", ASSET_CATEGORY_STOCK),
        ("688220.SH", "翱捷科技", ASSET_CATEGORY_STOCK),
        ("688256.SH", "寒武纪", ASSET_CATEGORY_STOCK),
        ("688270.SH", "臻镭科技", ASSET_CATEGORY_STOCK),
        ("688396.SH", "华润微", ASSET_CATEGORY_STOCK),
        ("688521.SH", "芯原股份", ASSET_CATEGORY_STOCK),
        ("688608.SH", "恒玄科技", ASSET_CATEGORY_STOCK),
        ("688728.SH", "格科微", ASSET_CATEGORY_STOCK),
        ("688777.SH", "中控技术", ASSET_CATEGORY_STOCK),
        ("688981.SH", "中芯国际", ASSET_CATEGORY_STOCK),
        ("689009.SH", "九号公司", ASSET_CATEGORY_STOCK),
        ("689256.SH", "寒武纪-U", ASSET_CATEGORY_STOCK),
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
        if symbol not in seen:
            result.append((symbol, name, ASSET_CATEGORY_STOCK))
            seen.add(symbol)
    return result


def _items_with_priority(items: list[tuple[str, str, str]], start: int = 1) -> list[dict]:
    return [
        {
            "symbol": symbol,
            "name": name,
            "asset_category": category,
            "priority": i,
            "source": "default",
        }
        for i, (symbol, name, category) in enumerate(items, start=start)
    ]


def build_default_specs(db_stock_candidates: Iterable[dict]) -> list[ListSpec]:
    stocks = build_stock_pool(db_stock_candidates)
    macros = _macro_items()
    futs = _futures_items()
    tech_stocks = _tech_stock_symbols()

    key_focus_items = _items_with_priority(stocks[:10] + macros[:5] + futs[:5])
    focus_items = _items_with_priority(stocks[:80] + macros[:10] + futs[:10])
    minute_items = _items_with_priority(stocks[:10] + futs[:6] + macros[:4])
    m15_items = _items_with_priority(stocks[:22] + futs[:10] + macros[:8])
    daily_items = _items_with_priority(stocks[:180] + futs[:10] + macros[:10])
    tech_key_focus_items = _items_with_priority(tech_stocks[:20])
    tech_focus_items = _items_with_priority(tech_stocks[:100])

    return [
        ListSpec(
            name="default_key_focus",
            list_type=LIST_TYPE_KEY_FOCUS,
            asset_type="multi_asset",
            frequency_type=FREQ_NONE,
            description="Default owner-scoped key focus list (20 objects)",
            items=key_focus_items,
            rules={"target_size": "20", "owner_scope": OWNER_ID_DEFAULT},
        ),
        ListSpec(
            name="default_focus",
            list_type=LIST_TYPE_FOCUS,
            asset_type="multi_asset",
            frequency_type=FREQ_NONE,
            description="Default owner-scoped focus list (100 objects)",
            items=focus_items,
            rules={"target_size": "100", "owner_scope": OWNER_ID_DEFAULT},
        ),
        ListSpec(
            name="tech_key_focus",
            list_type=LIST_TYPE_KEY_FOCUS,
            asset_type="stock",
            frequency_type=FREQ_NONE,
            description="Technology-only key focus list (20 stock objects)",
            items=tech_key_focus_items,
            rules={"target_size": "20", "owner_scope": OWNER_ID_DEFAULT, "theme": "technology"},
        ),
        ListSpec(
            name="tech_focus",
            list_type=LIST_TYPE_FOCUS,
            asset_type="stock",
            frequency_type=FREQ_NONE,
            description="Technology-only focus list (100 stock objects)",
            items=tech_focus_items,
            rules={"target_size": "100", "owner_scope": OWNER_ID_DEFAULT, "theme": "technology"},
        ),
        ListSpec(
            name="default_archive_targets_minute",
            list_type=LIST_TYPE_ARCHIVE_TARGETS,
            asset_type="multi_asset",
            frequency_type=FREQ_MINUTE,
            description="Default minute archive targets (20 objects)",
            items=minute_items,
            rules={"target_size": "20", "granularity": "minute"},
        ),
        ListSpec(
            name="default_archive_targets_15min",
            list_type=LIST_TYPE_ARCHIVE_TARGETS,
            asset_type="multi_asset",
            frequency_type=FREQ_15MIN,
            description="Default 15min archive targets (40 objects)",
            items=m15_items,
            rules={"target_size": "40", "granularity": "15min"},
        ),
        ListSpec(
            name="default_archive_targets_daily",
            list_type=LIST_TYPE_ARCHIVE_TARGETS,
            asset_type="multi_asset",
            frequency_type=FREQ_DAILY,
            description="Default daily archive targets (200 objects)",
            items=daily_items,
            rules={"target_size": "200", "granularity": "daily"},
        ),
    ]
