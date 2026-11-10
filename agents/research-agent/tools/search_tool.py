"""Search tool for the research agent.

Layer: Service (tool implementation). Standard library only. The tool validates
its input, returns JSON-serialisable output and declares a risk level.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

RISK_LOW = "low"
MAX_QUERY_LENGTH = 512
DEFAULT_LIMIT = 5
MAX_LIMIT = 25


class ToolInputError(ValueError):
    """Raised when a caller passes an argument the tool cannot accept."""


@dataclass(frozen=True)
class Document:
    """One retrieved document."""

    document_id: str
    title: str
    snippet: str
    score: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "snippet": self.snippet,
            "score": self.score,
        }


class SearchTool:
    """Searches an injected corpus.

    The corpus is passed in, so the tool performs no I/O and runs offline in
    tests. In production the runtime injects a corpus reader backed by the
    internal index.
    """

    name = "search"
    risk = RISK_LOW

    def __init__(self, documents: Sequence[Document], default_limit: int = DEFAULT_LIMIT) -> None:
        self._documents = tuple(documents)
        self._default_limit = default_limit

    def validate(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        """Validate and normalise the arguments. Raises ToolInputError on bad input."""
        query = arguments.get("query")
        if not isinstance(query, str):
            raise ToolInputError("query is required and must be a string")
        query = query.strip()
        if query == "":
            raise ToolInputError("query must not be empty")
        if len(query) > MAX_QUERY_LENGTH:
            raise ToolInputError(f"query must be at most {MAX_QUERY_LENGTH} characters")

        raw_limit = arguments.get("limit", self._default_limit)
        if not isinstance(raw_limit, int) or isinstance(raw_limit, bool):
            raise ToolInputError("limit must be an integer")
        if raw_limit < 1 or raw_limit > MAX_LIMIT:
            raise ToolInputError(f"limit must be between 1 and {MAX_LIMIT}")

        return {"query": query, "limit": raw_limit}

    def call(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        """Return matching documents. The result is JSON-serialisable."""
        clean = self.validate(arguments)
        terms = [term for term in clean["query"].lower().split() if term]

        scored: list[Document] = []
        for document in self._documents:
            haystack = f"{document.title} {document.snippet}".lower()
            hits = sum(1 for term in terms if term in haystack)
            if hits:
                scored.append(
                    Document(
                        document_id=document.document_id,
                        title=document.title,
                        snippet=document.snippet,
                        score=round(hits / max(len(terms), 1), 4),
                    )
                )

        scored.sort(key=lambda item: (-item.score, item.document_id))
        matches = scored[: clean["limit"]]

        return {
            "query": clean["query"],
            "count": len(matches),
            "results": [document.as_dict() for document in matches],
            "degraded": False,
        }
