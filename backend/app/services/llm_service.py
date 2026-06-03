from app.schemas.qa import CitationResponse
from app.services.rag_retriever import RetrievedChunk


class GroundedLLMResponse:
    def __init__(self, answer: str, confidence: float, citations: list[CitationResponse]):
        self.answer = answer
        self.confidence = confidence
        self.citations = citations


class MockGroundedLLMService:
    UNSUPPORTED_MESSAGE = "No supporting tax authority was found for this question."

    def answer(self, question: str, chunks: list[RetrievedChunk]) -> GroundedLLMResponse:
        if not chunks:
            return GroundedLLMResponse(self.UNSUPPORTED_MESSAGE, 0.0, [])

        top_chunks = chunks[:2]
        citations = [
            CitationResponse(
                source_id=chunk.source_id,
                source_title=chunk.source_title,
                section=chunk.section,
                source_url=chunk.source_url,
                validated=False,
            )
            for chunk in top_chunks
        ]
        answer = self._compose_answer(question, top_chunks)
        confidence = min(0.95, 0.55 + (sum(chunk.score for chunk in top_chunks) / 30))
        return GroundedLLMResponse(answer, round(confidence, 2), citations)

    @staticmethod
    def _compose_answer(question: str, chunks: list[RetrievedChunk]) -> str:
        source_sentences = " ".join(chunk.content for chunk in chunks)
        return (
            f"Based on the retrieved tax authority, {source_sentences} "
            "Review the specific facts before applying this guidance."
        )
