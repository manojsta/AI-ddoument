from pydantic import BaseModel, Field
from uuid import UUID
from typing import Any

class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    top_k: int = Field(default=8, ge=1, le=30)
    document_type: str | None = None
    vendor: str | None = None
    asset: str | None = None

class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    document_ids: list[UUID] = Field(default_factory=list)
    top_k: int = Field(default=6, ge=1, le=20)

class MetadataUpdate(BaseModel):
    metadata: dict[str, Any] = Field(default_factory=dict)

class Source(BaseModel):
    document_id: str
    filename: str
    page_number: int | None
    excerpt: str
