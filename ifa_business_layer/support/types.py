from __future__ import annotations

from dataclasses import asdict, dataclass, field


VALID_AGENT_DOMAINS = {"macro", "commodities", "ai_tech"}
VALID_SLOTS = {"early", "late"}
VALID_SECTION_KEYS = {
    "macro": "support_macro",
    "commodities": "support_commodities",
    "ai_tech": "support_ai_tech",
}
VALID_SECTION_TYPE = "support"
VALID_ASSEMBLY_MODES = {"rule_assembled", "hybrid"}
VALID_RELATIONS = {"support", "adjust", "counter"}
VALID_FACT_TYPES = {"market", "event", "flow", "breadth", "theme", "news", "announcement", "macro", "commodity"}
VALID_SOURCE_LAYERS = {"business_seed", "lowfreq", "midfreq", "highfreq", "archive_v2", "slot_replay"}
VALID_FRESHNESS = {"fresh", "same_slot", "t_minus_1", "stale", "unknown"}
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_SIGNAL_TYPES = {"strengthening", "weakening", "rotation", "divergence", "confirmation", "risk"}
VALID_HORIZONS = {"intraday", "same_day", "t_plus_1"}
VALID_JUDGMENT_TYPES = {"support", "risk", "watch_item", "next_step"}
VALID_JUDGMENT_ACTIONS = {"support", "adjust", "confirm", "downgrade", "observe", "prepare"}
VALID_DIRECTIONS = {"bullish", "bearish", "mixed", "neutral", "conditional"}
VALID_PRIORITIES = {"p0", "p1", "p2"}


class SupportValidationError(ValueError):
    pass


@dataclass(slots=True)
class SupportBundle:
    bundle_id: str
    market: str
    business_date: str
    slot: str
    agent_domain: str
    section_key: str
    section_type: str
    producer: str
    producer_version: str
    assembly_mode: str
    summary: str
    primary_relation: str
    secondary_relations: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.market != "a_share":
            raise SupportValidationError("bundle.market must be 'a_share'")
        if self.slot not in VALID_SLOTS:
            raise SupportValidationError(f"invalid slot: {self.slot}")
        if self.agent_domain not in VALID_AGENT_DOMAINS:
            raise SupportValidationError(f"invalid agent_domain: {self.agent_domain}")
        expected_section_key = VALID_SECTION_KEYS[self.agent_domain]
        if self.section_key != expected_section_key:
            raise SupportValidationError(
                f"section_key '{self.section_key}' does not match agent_domain '{self.agent_domain}'"
            )
        if self.section_type != VALID_SECTION_TYPE:
            raise SupportValidationError("section_type must be 'support'")
        if self.producer != "business-layer":
            raise SupportValidationError("producer must be 'business-layer'")
        if self.assembly_mode not in VALID_ASSEMBLY_MODES:
            raise SupportValidationError(f"invalid assembly_mode: {self.assembly_mode}")
        if not self.summary or "\n" in self.summary.strip():
            raise SupportValidationError("summary must be a non-empty single sentence")
        if self.primary_relation not in VALID_RELATIONS:
            raise SupportValidationError(f"invalid primary_relation: {self.primary_relation}")
        for relation in self.secondary_relations:
            if relation not in VALID_RELATIONS:
                raise SupportValidationError(f"invalid secondary relation: {relation}")
        if self.primary_relation in self.secondary_relations:
            raise SupportValidationError("primary_relation must not be repeated in secondary_relations")


@dataclass(slots=True)
class SupportFact:
    fact_id: str
    object_key: str
    fsj_kind: str
    fact_type: str
    statement: str
    entity_refs: list[str]
    metric_refs: list[str]
    source_layer: str
    freshness_label: str
    confidence: str

    def validate(self, *, domain: str) -> None:
        if self.fsj_kind != "fact":
            raise SupportValidationError("fact.fsj_kind must be 'fact'")
        if self.fact_type not in VALID_FACT_TYPES:
            raise SupportValidationError(f"invalid fact_type: {self.fact_type}")
        if not self.statement:
            raise SupportValidationError("fact.statement is required")
        if self.source_layer not in VALID_SOURCE_LAYERS:
            raise SupportValidationError(f"invalid source_layer: {self.source_layer}")
        if self.freshness_label not in VALID_FRESHNESS:
            raise SupportValidationError(f"invalid freshness_label: {self.freshness_label}")
        if self.confidence not in VALID_CONFIDENCE:
            raise SupportValidationError(f"invalid fact confidence: {self.confidence}")
        _validate_object_key(domain, self.object_key)


@dataclass(slots=True)
class SupportSignal:
    signal_id: str
    object_key: str
    fsj_kind: str
    signal_type: str
    statement: str
    based_on_fact_ids: list[str]
    signal_strength: str
    horizon: str
    confidence: str

    def validate(self, *, domain: str, fact_ids: set[str]) -> None:
        if self.fsj_kind != "signal":
            raise SupportValidationError("signal.fsj_kind must be 'signal'")
        if self.signal_type not in VALID_SIGNAL_TYPES:
            raise SupportValidationError(f"invalid signal_type: {self.signal_type}")
        if not self.statement:
            raise SupportValidationError("signal.statement is required")
        if not self.based_on_fact_ids:
            raise SupportValidationError("signal.based_on_fact_ids must not be empty")
        if not set(self.based_on_fact_ids).issubset(fact_ids):
            raise SupportValidationError("signal references unknown fact ids")
        if self.signal_strength not in VALID_CONFIDENCE:
            raise SupportValidationError(f"invalid signal_strength: {self.signal_strength}")
        if self.horizon not in VALID_HORIZONS:
            raise SupportValidationError(f"invalid signal horizon: {self.horizon}")
        if self.confidence not in VALID_CONFIDENCE:
            raise SupportValidationError(f"invalid signal confidence: {self.confidence}")
        _validate_object_key(domain, self.object_key)


@dataclass(slots=True)
class SupportJudgment:
    judgment_id: str
    object_key: str
    fsj_kind: str
    judgment_type: str
    statement: str
    judgment_action: str
    based_on_signal_ids: list[str]
    direction: str
    priority: str
    invalidators: list[str]
    confidence: str

    def validate(self, *, domain: str, signal_ids: set[str]) -> None:
        if self.fsj_kind != "judgment":
            raise SupportValidationError("judgment.fsj_kind must be 'judgment'")
        if self.judgment_type not in VALID_JUDGMENT_TYPES:
            raise SupportValidationError(f"invalid judgment_type: {self.judgment_type}")
        if not self.statement:
            raise SupportValidationError("judgment.statement is required")
        if self.judgment_action not in VALID_JUDGMENT_ACTIONS:
            raise SupportValidationError(f"invalid judgment_action: {self.judgment_action}")
        if not self.based_on_signal_ids:
            raise SupportValidationError("judgment.based_on_signal_ids must not be empty")
        if not set(self.based_on_signal_ids).issubset(signal_ids):
            raise SupportValidationError("judgment references unknown signal ids")
        if self.direction not in VALID_DIRECTIONS:
            raise SupportValidationError(f"invalid judgment.direction: {self.direction}")
        if self.priority not in VALID_PRIORITIES:
            raise SupportValidationError(f"invalid judgment.priority: {self.priority}")
        if self.invalidators is None:
            raise SupportValidationError("judgment.invalidators must exist")
        if self.confidence not in VALID_CONFIDENCE:
            raise SupportValidationError(f"invalid judgment confidence: {self.confidence}")
        _validate_object_key(domain, self.object_key)


@dataclass(slots=True)
class SupportPayload:
    bundle: SupportBundle
    facts: list[SupportFact]
    signals: list[SupportSignal]
    judgments: list[SupportJudgment]

    def validate(self) -> None:
        self.bundle.validate()
        if not self.facts:
            raise SupportValidationError("at least one fact is required")
        if not self.signals:
            raise SupportValidationError("at least one signal is required")
        if not self.judgments:
            raise SupportValidationError("at least one judgment is required")
        fact_ids = {fact.fact_id for fact in self.facts}
        signal_ids = {signal.signal_id for signal in self.signals}
        for fact in self.facts:
            fact.validate(domain=self.bundle.agent_domain)
        for signal in self.signals:
            signal.validate(domain=self.bundle.agent_domain, fact_ids=fact_ids)
        for judgment in self.judgments:
            judgment.validate(domain=self.bundle.agent_domain, signal_ids=signal_ids)

    def to_dict(self) -> dict:
        self.validate()
        return {
            "bundle": asdict(self.bundle),
            "facts": [asdict(item) for item in self.facts],
            "signals": [asdict(item) for item in self.signals],
            "judgments": [asdict(item) for item in self.judgments],
        }


ALLOWED_OBJECT_KEYS = {
    "macro": {
        "macro:liquidity",
        "macro:rates",
        "macro:fx",
        "macro:policy_expectation",
        "macro:risk_appetite",
    },
    "commodities": {
        "commodity:oil_chain",
        "commodity:industrial_metals",
        "commodity:gold",
        "commodity:black_chain",
        "commodity:chemicals",
        "commodity:agri_chain",
    },
    "ai_tech": {
        "ai_tech:mainline_status",
        "ai_tech:compute_chain",
        "ai_tech:model_chain",
        "ai_tech:application_chain",
        "ai_tech:leader_diffusion",
        "ai_tech:theme_exhaustion",
    },
}


def _validate_object_key(domain: str, object_key: str) -> None:
    allowed = ALLOWED_OBJECT_KEYS.get(domain, set())
    if object_key not in allowed:
        raise SupportValidationError(f"invalid object_key for domain {domain}: {object_key}")
