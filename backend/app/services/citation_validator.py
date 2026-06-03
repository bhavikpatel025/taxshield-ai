from app.schemas.qa import CitationResponse
from app.services.rag_retriever import RetrievedChunk


class CitationValidator:
    def validate(self, citations: list[CitationResponse], chunks: list[RetrievedChunk]) -> list[CitationResponse]:
        allowed = {(chunk.source_id, chunk.section) for chunk in chunks}
        validated: list[CitationResponse] = []
        for citation in citations:
            validated.append(
                CitationResponse(
                    source_id=citation.source_id,
                    source_title=citation.source_title,
                    section=citation.section,
                    source_url=citation.source_url,
                    validated=(citation.source_id, citation.section) in allowed,
                )
            )
        return [citation for citation in validated if citation.validated]
