import json
import re
from dataclasses import dataclass
from pathlib import Path

SOURCES_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "mock_tax_sources.json"


@dataclass(frozen=True)
class RetrievedChunk:
    source_id: str
    source_title: str
    section: str
    source_url: str | None
    content: str
    score: float


class LocalTaxLawRetriever:
    def __init__(self, sources_path: Path = SOURCES_PATH):
        self.sources = json.loads(sources_path.read_text(encoding="utf-8"))

    def retrieve(self, question: str, top_k: int = 4) -> list[RetrievedChunk]:
        normalized_question = question.lower()
        query_terms = self._terms(normalized_question)
        scored: list[RetrievedChunk] = []
        for source in self.sources:
            keyword_hits = sum(1 for keyword in source["keywords"] if self._has_keyword(normalized_question, keyword))
            content_terms = self._terms(source["content"].lower())
            overlap = len(query_terms.intersection(content_terms))
            score = float(keyword_hits * 3 + overlap)
            if score <= 0:
                continue
            scored.append(
                RetrievedChunk(
                    source_id=source["source_id"],
                    source_title=source["source_title"],
                    section=source["section"],
                    source_url=source.get("source_url"),
                    content=source["content"],
                    score=score,
                )
            )
        return sorted(scored, key=lambda chunk: chunk.score, reverse=True)[:top_k]

    @staticmethod
    def _terms(text: str) -> set[str]:
        stop_words = {"a", "an", "and", "are", "can", "do", "for", "i", "is", "of", "on", "the", "to"}
        return {term for term in re.findall(r"[a-z0-9]+", text) if len(term) > 2 and term not in stop_words}

    @staticmethod
    def _has_keyword(text: str, keyword: str) -> bool:
        escaped = re.escape(keyword.lower())
        return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text) is not None
