"""tests/unit/manifest/test_manifest_loader.py — Tests for manifest loading and legacy mapping."""

from pathlib import Path

import yaml

from src.manifest.loader import load_manifest, manifest_to_legacy_config
from src.manifest.models import DocumentItemModel, DocumentManifest, ScopeConfigModel


def test_load_manifest_non_existent(tmp_path: Path):
    non_existent = tmp_path / "does_not_exist.yaml"
    manifest = load_manifest(non_existent)
    assert isinstance(manifest, DocumentManifest)
    assert len(manifest.documents) == 0


def test_load_manifest_valid(tmp_path: Path):
    manifest_file = tmp_path / "documents.yaml"
    content = {
        "documents": [
            {
                "id": "168_2024_ND_CP",
                "number": "168/2024/NĐ-CP",
                "raw_file": "168_2024.docx",
                "name": "Nghị định 168",
                "type": "NGHI_DINH",
                "role": "NORMAL",
                "need_review": False,
                "aliases": ["168"],
                "scope": {"mode": "ALL", "selected_articles": []},
            }
        ]
    }
    manifest_file.write_text(yaml.dump(content), encoding="utf-8")
    
    manifest = load_manifest(manifest_file)
    assert len(manifest.documents) == 1
    doc = manifest.documents[0]
    assert doc.id == "168_2024_ND_CP"
    assert doc.number == "168/2024/NĐ-CP"
    assert doc.role == "NORMAL"
    assert not doc.need_review


def test_manifest_to_legacy_config():
    manifest = DocumentManifest(
        documents=[
            DocumentItemModel(
                id="168_2024_ND_CP",
                number="168/2024/NĐ-CP",
                raw_file="168.docx",
                name="Nghị định 168",
                type="NGHI_DINH",
                role="NORMAL",
                aliases=["168"],
                scope=ScopeConfigModel(mode="ALL"),
            ),
            DocumentItemModel(
                id="118_2025_QH15",
                number="118/2025/QH15",
                raw_file="118.docx",
                name="Luật 118",
                type="LUAT",
                role="OMNIBUS",
                aliases=["118"],
                scope=ScopeConfigModel(mode="SELECTED", selected_articles=["7"]),
                amendment_article_targets={"7": "36/2024/QH15"},
            ),
        ]
    )

    legacy = manifest_to_legacy_config(manifest)

    # 1. FILE_SO_HIEU_MAP
    assert legacy["FILE_SO_HIEU_MAP"]["168.docx"] == "168/2024/ND-CP"
    assert legacy["FILE_SO_HIEU_MAP"]["118.docx"] == "118/2025/QH15"

    # 2. DOCUMENT_REGISTRY
    reg = legacy["DOCUMENT_REGISTRY"]
    assert "168/2024/ND-CP" in reg
    assert reg["168/2024/ND-CP"]["role"] == "NORMAL"
    assert "118/2025/QH15" in reg
    assert reg["118/2025/QH15"]["role"] == "OMNIBUS"

    # 3. SCOPE_CONFIG
    scope = legacy["SCOPE_CONFIG"]
    assert scope["118/2025/QH15"]["scope_mode"] == "SELECTED"
    assert scope["118/2025/QH15"]["selected_articles"] == ["7"]
    assert scope["default"]["scope_mode"] == "ALL"

    # 4. AMENDMENT_ARTICLE_TARGETS
    assert legacy["AMENDMENT_ARTICLE_TARGETS"]["118/2025/QH15"] == {"7": "36/2024/QH15"}

    # 5. VAN_BAN_SCOPE
    vb_scope = legacy["VAN_BAN_SCOPE"]
    assert vb_scope["168/2024/ND-CP"]["loai"] == "NghiDinh"
    assert vb_scope["118/2025/QH15"]["loai"] == "Luat_gop"
    assert vb_scope["118/2025/QH15"]["pham_vi_ngoai_scope"] is True
