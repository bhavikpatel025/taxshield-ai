import json
import re
from pathlib import Path
from typing import Any

from app.models.audit import RiskLevel

RULES_PATH = Path(__file__).resolve().parent.parent / "rules" / "audit_rules.json"


class AuditRuleEngine:
    def __init__(self, rules_path: Path = RULES_PATH):
        self.rules = json.loads(rules_path.read_text(encoding="utf-8"))

    def evaluate(self, text: str) -> tuple[RiskLevel, list[dict[str, str]]]:
        normalized_text = text.lower()
        score = 0
        flags: list[dict[str, str]] = []

        for rule in self.rules:
            if self._matches(rule, normalized_text):
                score += int(rule.get("score", 1))
                flags.append(
                    {
                        "code": rule["code"],
                        "description": rule["description"],
                        "severity": rule["severity"],
                        "supporting_tax_authority": rule["supporting_tax_authority"],
                    }
                )

        return self._risk_level(score), flags

    def _matches(self, rule: dict[str, Any], text: str) -> bool:
        rule_type = rule.get("type")
        if rule_type == "keyword":
            return any(term in text for term in rule["terms"])
        if rule_type == "missing_context":
            has_required = any(term in text for term in rule["required_terms"])
            missing_context = not any(term in text for term in rule["missing_any_terms"])
            return has_required and missing_context
        if rule_type == "ratio":
            numerator = self._largest_amount_near_terms(text, rule["numerator_terms"])
            denominator = self._largest_amount_near_terms(text, rule["denominator_terms"])
            return denominator > 0 and numerator / denominator >= float(rule["threshold"])
        return False

    @staticmethod
    def _largest_amount_near_terms(text: str, terms: list[str]) -> float:
        amounts: list[float] = []
        amount_pattern = r"\$?\s?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|[0-9]+(?:\.[0-9]{2})?)"
        for term in terms:
            for match in re.finditer(term, text):
                window = text[max(match.start() - 80, 0) : match.end() + 80]
                for amount in re.findall(amount_pattern, window):
                    amounts.append(float(amount.replace(",", "")))
        return max(amounts) if amounts else 0.0

    @staticmethod
    def _risk_level(score: int) -> RiskLevel:
        if score >= 6:
            return RiskLevel.HIGH
        if score >= 3:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
