"""
config.py

Chỉ chứa:
- System Configuration
- Parser Constants
- Document Registry
- Parser Patterns
- Parser State

Không chứa:
- Tri thức pháp lý (quan hệ sửa đổi A->B, thứ tự áp dụng...)
- Workflow / logic parser
"""

# ==========================================================
# PATH
# ==========================================================

RAW_DIR = "data/raw"
PARSED_DIR = "data/parsed"

# ==========================================================
# DOCUMENT TYPE / ROLE / TARGET LEVEL / PARSER STATE
# ==========================================================

DOCUMENT_TYPES = {"LUAT": "LUAT", "NGHI_DINH": "NGHI_DINH", "THONG_TU": "THONG_TU"}
DOCUMENT_ROLES = {"NORMAL": "NORMAL", "AMENDMENT": "AMENDMENT", "OMNIBUS": "OMNIBUS"}
TARGET_LEVEL = {"ARTICLE": "ARTICLE", "CLAUSE": "CLAUSE", "POINT": "POINT"}
PARSER_STATE = {
    "NORMAL": "NORMAL",
    "AMENDMENT_HEADER": "AMENDMENT_HEADER",
    "AMENDMENT_BLOCK": "AMENDMENT_BLOCK",
    "REPLACEMENT_TREE": "REPLACEMENT_TREE",
}

# ==========================================================
# LEGAL RELATIONS
# ==========================================================

REFERENCE_RELATIONS = ["THAM_CHIEU", "CAN_CU_VAO", "NGOAI_LE", "DAN_CHIEU"]
AMENDMENT_RELATIONS = ["SUA_DOI", "BO_SUNG", "THAY_THE", "BAI_BO", "THEM_MOI"]

# ==========================================================
# PARSER KEYWORDS / QUOTE / PATTERNS
# ==========================================================

AMENDMENT_KEYWORDS = ["Sửa đổi", "Bổ sung", "Thay thế", "Bãi bỏ", "Thêm mới"]
QUOTE_CHARS = ['"', "“", "”"]

TARGET_PATTERNS = {
    "ARTICLE": [r"Điều\s+\d+[a-zđ]?"],
    "CLAUSE": [r"khoản\s+\d+[a-zđ]?"],
    "POINT": [r"điểm\s+[a-zđ]"],
}

REFERENCE_PATTERNS = [
    "Điều này",
    "Khoản này",
    "Điểm này",
    "Luật này",
    "Nghị định này",
    "Thông tư này",
]

OPERATION_PRIORITY = ["BAI_BO", "THAY_THE", "SUA_DOI", "BO_SUNG", "THEM_MOI"]

# ==========================================================
# DOCUMENT REGISTRY & MANIFEST ADAPTER
# Nạp tự động từ config/documents.yaml để bảo toàn nguồn sự thật duy nhất
# và hỗ trợ cơ chế bán tự động (semi-automated) khi thêm văn bản mới.
# ==========================================================

from src.manifest.loader import load_manifest, manifest_to_legacy_config

_manifest = load_manifest()
_legacy = manifest_to_legacy_config(_manifest)

DOCUMENT_REGISTRY = _legacy["DOCUMENT_REGISTRY"]
FILE_SO_HIEU_MAP = _legacy["FILE_SO_HIEU_MAP"]
OMNIBUS_CONFIG = _legacy["OMNIBUS_CONFIG"]
SCOPE_CONFIG = _legacy["SCOPE_CONFIG"]
AMENDMENT_TARGET_FALLBACK = _legacy["AMENDMENT_TARGET_FALLBACK"]
AMENDMENT_ARTICLE_TARGETS = _legacy["AMENDMENT_ARTICLE_TARGETS"]
VAN_BAN_SCOPE = _legacy["VAN_BAN_SCOPE"]
