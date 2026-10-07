"""src/manifest/models.py — Data models for Document Manifest schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ScopeConfigModel(BaseModel):
    mode: str = "ALL"  # "ALL" | "SELECTED"
    selected_articles: list[str] = Field(default_factory=list)


class OmnibusTargetModel(BaseModel):
    document: str
    keywords: list[str] = Field(default_factory=list)


class OmnibusConfigModel(BaseModel):
    targets: list[OmnibusTargetModel] = Field(default_factory=list)


class DocumentItemModel(BaseModel):
    id: str
    number: str
    raw_file: str
    name: str
    type: str  # "LUAT" | "NGHI_DINH" | "THONG_TU"
    role: str = "NORMAL"  # "NORMAL" | "AMENDMENT" | "OMNIBUS"
    need_review: bool = False
    aliases: list[str] = Field(default_factory=list)
    scope: ScopeConfigModel = Field(default_factory=ScopeConfigModel)
    omnibus: OmnibusConfigModel | None = None
    amendment_target_fallback: str | None = None
    amendment_article_targets: dict[str, str] = Field(default_factory=dict)


class DocumentManifest(BaseModel):
    documents: list[DocumentItemModel] = Field(default_factory=list)
