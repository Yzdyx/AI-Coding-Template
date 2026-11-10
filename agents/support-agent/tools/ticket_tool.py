"""Knowledge-base and draft tools for the support agent.

Layer: Service (tool implementation). Standard library only. Input is validated,
output is JSON-serialisable, and every tool declares a risk level.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

RISK_LOW = "low"
RISK_HIGH = "high"

MAX_QUESTION_LENGTH = 1024
MAX_DRAFT_LENGTH = 4000


class ToolInputError(ValueError):
    """Raised when a caller passes an argument the tool cannot accept."""


@dataclass(frozen=True)
class Article:
    """One knowledge-base article."""

    article_id: str
    title: str
    body: str

    def as_dict(self) -> dict[str, Any]:
        return {"article_id": self.article_id, "title": self.title, "body": self.body}


class KnowledgeBaseTool:
    """Looks up knowledge-base articles from an injected corpus.

    The corpus is passed in, so the tool performs no I/O and runs offline in tests.
    """

    name = "kb_lookup"
    risk = RISK_LOW

    def __init__(self, articles: Sequence[Article], limit: int = 3) -> None:
        self._articles = tuple(articles)
        self._limit = limit

    def validate(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        question = arguments.get("question")
        if not isinstance(question, str):
            raise ToolInputError("question is required and must be a string")
        question = question.strip()
        if question == "":
            raise ToolInputError("question must not be empty")
        if len(question) > MAX_QUESTION_LENGTH:
            raise ToolInputError(f"question must be at most {MAX_QUESTION_LENGTH} characters")
        return {"question": question}

    def call(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        clean = self.validate(arguments)
        terms = [term for term in clean["question"].lower().split() if term]

        matches: list[Article] = []
        for article in self._articles:
            haystack = f"{article.title} {article.body}".lower()
            if any(term in haystack for term in terms):
                matches.append(article)

        selected = matches[: self._limit]
        return {
            "question": clean["question"],
            "count": len(selected),
            "articles": [article.as_dict() for article in selected],
        }


class DraftReplyTool:
    """Creates a reply draft. Risk is `high`: a draft can reach a customer.

    The tool records the draft in an injected sink. It never transmits anything,
    and it requires an idempotency key so a retry cannot create a second draft.
    """

    name = "draft_reply"
    risk = RISK_HIGH

    def __init__(self, sink: list[dict[str, Any]] | None = None) -> None:
        self._sink = [] if sink is None else sink

    @property
    def drafts(self) -> Sequence[Mapping[str, Any]]:
        return tuple(self._sink)

    def validate(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        ticket_id = arguments.get("ticket_id")
        if not isinstance(ticket_id, str) or ticket_id.strip() == "":
            raise ToolInputError("ticket_id is required and must be a non-empty string")

        body = arguments.get("body")
        if not isinstance(body, str):
            raise ToolInputError("body is required and must be a string")
        body = body.strip()
        if body == "":
            raise ToolInputError("body must not be empty")
        if len(body) > MAX_DRAFT_LENGTH:
            raise ToolInputError(f"body must be at most {MAX_DRAFT_LENGTH} characters")

        idempotency_key = arguments.get("idempotency_key")
        if not isinstance(idempotency_key, str) or idempotency_key.strip() == "":
            raise ToolInputError("idempotency_key is required for a side-effecting tool")

        return {"ticket_id": ticket_id.strip(), "body": body, "idempotency_key": idempotency_key}

    def call(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        clean = self.validate(arguments)

        for draft in self._sink:
            if draft["idempotency_key"] == clean["idempotency_key"]:
                return {"draft_id": draft["draft_id"], "ticket_id": draft["ticket_id"], "replayed": True}

        draft_id = f"draft-{len(self._sink) + 1}"
        self._sink.append(
            {
                "draft_id": draft_id,
                "ticket_id": clean["ticket_id"],
                "body": clean["body"],
                "idempotency_key": clean["idempotency_key"],
            }
        )
        return {"draft_id": draft_id, "ticket_id": clean["ticket_id"], "replayed": False}
