"""src/manifest/loader.py — Load, validate and transform Document Manifest."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from src.manifest.models import DocumentManifest
from src.parser.canonical_id_resolver import normalize_so_hieu

logger = logging.getLogger(__name__)

DEFAULT_MANIFEST_PATH = Path("config/documents.yaml")


def load_manifest(path: str | Path | None = None) -> DocumentManifest:
    """Loads and validates the document manifest YAML file.
    
    If the file does not exist, returns an empty DocumentManifest.
    """
    manifest_path = Path(path) if path else DEFAULT_MANIFEST_PATH
    if not manifest_path.exists():
        logger.warning("Manifest file %s not found, returning empty manifest.", manifest_path)
        return DocumentManifest()

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}
        return DocumentManifest.model_validate(raw_data)
    except Exception as e:
        logger.error("Failed to load or parse manifest from %s: %s", manifest_path, e)
        raise


def manifest_to_legacy_config(manifest: DocumentManifest) -> dict[str, Any]:
    """Transforms a DocumentManifest instance into legacy configuration dictionaries.
    
    Ensures 100% backward compatibility with existing code expecting:
    - DOCUMENT_REGISTRY
    - FILE_SO_HIEU_MAP
    - OMNIBUS_CONFIG
    - SCOPE_CONFIG
    - AMENDMENT_TARGET_FALLBACK
    - AMENDMENT_ARTICLE_TARGETS
    - VAN_BAN_SCOPE
    """
    file_so_hieu_map: dict[str, str] = {}
    document_registry: dict[str, dict[str, Any]] = {}
    omnibus_config: list[dict[str, Any]] = []
    scope_config: dict[str, Any] = {}
    amendment_target_fallback: dict[str, str] = {}
    amendment_article_targets: dict[str, dict[str, str]] = {}

    for doc in manifest.documents:
        key = normalize_so_hieu(doc.number) or doc.id
        
        # 1. FILE_SO_HIEU_MAP
        if doc.raw_file:
            file_so_hieu_map[doc.raw_file] = key

        # 2. DOCUMENT_REGISTRY
        document_registry[key] = {
            "id": doc.id,
            "number": doc.number,
            "name": doc.name,
            "aliases": list(doc.aliases),
            "type": doc.type,
            "role": doc.role,
        }

        # 3. OMNIBUS_CONFIG
        if doc.omnibus and doc.omnibus.targets:
            omnibus_config.append({
                "source": key,
                "targets": [
                    {
                        "document": t.document,
                        "keywords": list(t.keywords),
                    }
                    for t in doc.omnibus.targets
                ],
            })

        # 4. SCOPE_CONFIG
        if doc.scope.mode == "SELECTED":
            scope_config[key] = {
                "scope_mode": "SELECTED",
                "selected_articles": list(doc.scope.selected_articles),
            }

        # 5. AMENDMENT_TARGET_FALLBACK
        if doc.amendment_target_fallback:
            amendment_target_fallback[key] = doc.amendment_target_fallback

        # 6. AMENDMENT_ARTICLE_TARGETS
        if doc.amendment_article_targets:
            amendment_article_targets[key] = dict(doc.amendment_article_targets)

    # Default scope for unconfigured documents
    scope_config["default"] = {"scope_mode": "ALL"}

    # 7. VAN_BAN_SCOPE (derived from DOCUMENT_REGISTRY)
    van_ban_scope = {
        number: {
            "ten": meta["name"],
            "loai": (
                "NghiDinh_suaDoi"
                if meta["role"] == "AMENDMENT"
                else "Luat_gop"
                if meta["role"] == "OMNIBUS" and meta["type"] == "LUAT"
                else "NghiDinh_phanDinhThamQuyen"
                if meta["role"] == "OMNIBUS"
                else "Luat"
                if meta["type"] == "LUAT"
                else "ThongTu"
                if meta.get("type") == "THONG_TU"
                else "NghiDinh"
            ),
            "pham_vi_ngoai_scope": meta["role"] == "OMNIBUS",
        }
        for number, meta in document_registry.items()
    }

    return {
        "FILE_SO_HIEU_MAP": file_so_hieu_map,
        "DOCUMENT_REGISTRY": document_registry,
        "OMNIBUS_CONFIG": omnibus_config,
        "SCOPE_CONFIG": scope_config,
        "AMENDMENT_TARGET_FALLBACK": amendment_target_fallback,
        "AMENDMENT_ARTICLE_TARGETS": amendment_article_targets,
        "VAN_BAN_SCOPE": van_ban_scope,
    }
