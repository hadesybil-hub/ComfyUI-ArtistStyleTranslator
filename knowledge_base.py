"""Validated, backward-compatible records for the built-in artist knowledge base.

This module contains data-shape and loading concerns only.  It does not build
prompts, access networks, or add fields to the semantic engine's public types.
"""

from copy import deepcopy
from datetime import date, datetime, time, timezone
import math
import re
import unicodedata


STYLE_PROFILE_FIELDS = (
    "medium",
    "genre",
    "subject_focus",
    "linework",
    "shape_language",
    "facial_design",
    "anatomy",
    "rendering",
    "shading",
    "coloring",
    "palette",
    "lighting",
    "composition",
    "environment",
    "clothing",
    "mood",
    "detail_emphasis",
)

KNOWLEDGE_RECORD_FIELDS = (
    "artist_id",
    "canonical_name",
    "display_name",
    "aliases",
    "localized_names",
    "category",
    "metadata",
    "semantic",
)
KNOWLEDGE_METADATA_FIELDS = (
    "source",
    "version",
    "created_at",
    "updated_at",
    "profile_schema_version",
    "review_status",
)
KNOWLEDGE_SEMANTIC_FIELDS = (
    "style_profile",
    "profile_confidence",
    "category_confidence",
    "evidence",
)
EVIDENCE_FIELDS = (
    "evidence_id",
    "type",
    "scope",
    "summary",
    "reference",
)

SUPPORTED_PROFILE_SCHEMA_VERSIONS = ("1.0",)
SUPPORTED_REVIEW_STATUSES = ("draft", "reviewed", "published")
SUPPORTED_EVIDENCE_TYPES = (
    "direct_observation",
    "cross_work_synthesis",
    "uncertain_inference",
    "legacy_migration",
)

_ARTIST_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


class KnowledgeRecordValidationError(ValueError):
    """Raised when a knowledge record cannot safely enter the knowledge base."""


class KnowledgeBaseConflictError(KnowledgeRecordValidationError):
    """Raised when IDs or normalized artist names collide."""


def normalize_artist_name(name):
    """Normalize Unicode, case, whitespace, and common separators for lookup."""
    try:
        text = unicodedata.normalize("NFKC", str(name or "")).casefold().strip()
        return "".join(character for character in text if character.isalnum())
    except Exception:
        return ""


def _require_exact_fields(value, expected, field_name):
    if not isinstance(value, dict):
        raise KnowledgeRecordValidationError(f"{field_name} must be a dictionary")
    actual = set(value)
    required = set(expected)
    missing = sorted(required - actual)
    unknown = sorted(actual - required)
    if missing or unknown:
        raise KnowledgeRecordValidationError(
            f"{field_name} fields are invalid; missing={missing}, unknown={unknown}"
        )


def _require_text(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeRecordValidationError(
            f"{field_name} must be a non-empty string"
        )
    return value.strip()


def _require_text_tuple(value, field_name, *, allow_empty=False):
    if not isinstance(value, tuple):
        raise KnowledgeRecordValidationError(f"{field_name} must be a tuple")
    if not value and not allow_empty:
        raise KnowledgeRecordValidationError(f"{field_name} must not be empty")
    for index, item in enumerate(value):
        _require_text(item, f"{field_name}[{index}]")


def _require_confidence(value, field_name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise KnowledgeRecordValidationError(
            f"{field_name} must be a number between 0 and 1"
        )
    score = float(value)
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise KnowledgeRecordValidationError(
            f"{field_name} must be a number between 0 and 1"
        )


def _require_iso_date(value, field_name):
    text = _require_text(value, field_name)
    try:
        if "T" in text:
            datetime.fromisoformat(text.replace("Z", "+00:00"))
        else:
            date.fromisoformat(text)
    except ValueError as exc:
        raise KnowledgeRecordValidationError(
            f"{field_name} must use ISO 8601 format"
        ) from exc
    return text


def _date_sort_value(value):
    if "T" in value:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    return datetime.combine(date.fromisoformat(value), time.min)


def _validate_metadata(metadata):
    _require_exact_fields(metadata, KNOWLEDGE_METADATA_FIELDS, "metadata")
    _require_text(metadata["source"], "metadata.source")
    version = _require_text(metadata["version"], "metadata.version")
    if not _VERSION_PATTERN.fullmatch(version):
        raise KnowledgeRecordValidationError(
            "metadata.version must use MAJOR.MINOR.PATCH format"
        )
    created_at = _require_iso_date(metadata["created_at"], "metadata.created_at")
    updated_at = _require_iso_date(metadata["updated_at"], "metadata.updated_at")
    if _date_sort_value(updated_at) < _date_sort_value(created_at):
        raise KnowledgeRecordValidationError(
            "metadata.updated_at must not precede metadata.created_at"
        )
    schema_version = _require_text(
        metadata["profile_schema_version"],
        "metadata.profile_schema_version",
    )
    if schema_version not in SUPPORTED_PROFILE_SCHEMA_VERSIONS:
        raise KnowledgeRecordValidationError(
            "metadata.profile_schema_version is not supported"
        )
    review_status = _require_text(metadata["review_status"], "metadata.review_status")
    if review_status not in SUPPORTED_REVIEW_STATUSES:
        raise KnowledgeRecordValidationError("metadata.review_status is not supported")


def _validate_evidence(evidence):
    if not isinstance(evidence, tuple) or not evidence:
        raise KnowledgeRecordValidationError(
            "semantic.evidence must be a non-empty tuple"
        )
    evidence_ids = set()
    for index, item in enumerate(evidence):
        field_name = f"semantic.evidence[{index}]"
        _require_exact_fields(item, EVIDENCE_FIELDS, field_name)
        evidence_id = _require_text(item["evidence_id"], f"{field_name}.evidence_id")
        if evidence_id in evidence_ids:
            raise KnowledgeRecordValidationError(
                f"duplicate evidence_id: {evidence_id}"
            )
        evidence_ids.add(evidence_id)
        evidence_type = _require_text(item["type"], f"{field_name}.type")
        if evidence_type not in SUPPORTED_EVIDENCE_TYPES:
            raise KnowledgeRecordValidationError(
                f"{field_name}.type is not supported"
            )
        scope = _require_text(item["scope"], f"{field_name}.scope")
        if scope != "profile" and scope not in STYLE_PROFILE_FIELDS:
            raise KnowledgeRecordValidationError(
                f"{field_name}.scope must be profile or a style category"
            )
        _require_text(item["summary"], f"{field_name}.summary")
        _require_text(item["reference"], f"{field_name}.reference")


def _validate_semantic(semantic):
    _require_exact_fields(semantic, KNOWLEDGE_SEMANTIC_FIELDS, "semantic")
    style_profile = semantic["style_profile"]
    _require_exact_fields(style_profile, STYLE_PROFILE_FIELDS, "semantic.style_profile")
    for field_name in STYLE_PROFILE_FIELDS:
        _require_text_tuple(
            style_profile[field_name],
            f"semantic.style_profile.{field_name}",
        )

    _require_confidence(
        semantic["profile_confidence"],
        "semantic.profile_confidence",
    )
    category_confidence = semantic["category_confidence"]
    _require_exact_fields(
        category_confidence,
        STYLE_PROFILE_FIELDS,
        "semantic.category_confidence",
    )
    for field_name in STYLE_PROFILE_FIELDS:
        _require_confidence(
            category_confidence[field_name],
            f"semantic.category_confidence.{field_name}",
        )
    _validate_evidence(semantic["evidence"])


def validate_knowledge_record(record):
    """Strictly validate one knowledge record without mutating it."""
    _require_exact_fields(record, KNOWLEDGE_RECORD_FIELDS, "record")
    artist_id = _require_text(record["artist_id"], "artist_id")
    if not _ARTIST_ID_PATTERN.fullmatch(artist_id):
        raise KnowledgeRecordValidationError(
            "artist_id must be a lowercase ASCII slug"
        )
    canonical_name = _require_text(record["canonical_name"], "canonical_name")
    _require_text(record["display_name"], "display_name")
    if not normalize_artist_name(canonical_name):
        raise KnowledgeRecordValidationError(
            "canonical_name must produce a non-empty lookup key"
        )

    _require_text_tuple(record["aliases"], "aliases", allow_empty=True)
    localized_names = record["localized_names"]
    if not isinstance(localized_names, dict):
        raise KnowledgeRecordValidationError("localized_names must be a dictionary")
    for language, names in localized_names.items():
        _require_text(language, "localized_names language")
        _require_text_tuple(names, f"localized_names.{language}")
    _require_text_tuple(record["category"], "category")
    _validate_metadata(record["metadata"])
    _validate_semantic(record["semantic"])
    return record


def _record_names(record):
    names = [record["canonical_name"], record["display_name"], *record["aliases"]]
    for localized in record["localized_names"].values():
        names.extend(localized)
    return names


def legacy_artist_view(record):
    """Return the exact pre-V1.7 public artist record shape."""
    validate_knowledge_record(record)
    if record["metadata"]["review_status"] != "published":
        raise KnowledgeRecordValidationError(
            "only published knowledge records can enter runtime"
        )
    return {
        "canonical_name": record["canonical_name"],
        "aliases": tuple(record["aliases"]),
        "style_profile": deepcopy(record["semantic"]["style_profile"]),
    }


def project_semantic_style_profile(record):
    """Project a published record into existing semantic engine types.

    Structured research evidence remains in the knowledge record.  The runtime
    projection intentionally preserves the V1.6 built-in provenance contract.
    """
    validate_knowledge_record(record)
    if record["metadata"]["review_status"] != "published":
        raise KnowledgeRecordValidationError(
            "only published knowledge records can enter runtime"
        )
    try:
        from .style_engine import (
            SemanticStyleProfile,
            deduplicate_features,
            rank_features,
            semanticize_style_profile,
        )
    except ImportError:  # Supports the existing direct-file test loader.
        from style_engine import (
            SemanticStyleProfile,
            deduplicate_features,
            rank_features,
            semanticize_style_profile,
        )

    runtime_evidence = ("builtin structured style profile",)
    features = []
    for category in STYLE_PROFILE_FIELDS:
        category_profile = semanticize_style_profile(
            {
                category: record["semantic"]["style_profile"][category],
            },
            source="builtin",
            confidence=record["semantic"]["category_confidence"][category],
            evidence=runtime_evidence,
            generated_by="artist_database",
        )
        features.extend(category_profile.features)
    return SemanticStyleProfile(
        features=rank_features(deduplicate_features(features)),
        source="builtin",
        confidence=record["semantic"]["profile_confidence"],
        evidence=runtime_evidence,
        generated_by="artist_database",
    )


class KnowledgeBaseLoader:
    """Validate records and expose published entries through legacy APIs."""

    def __init__(self, records):
        self._records = deepcopy(tuple(records))
        self._record_by_id = {}
        self._published_name_index = {}
        self._validate_collection()

    def _validate_collection(self):
        canonical_names = {}
        normalized_names = {}
        for record in self._records:
            validate_knowledge_record(record)
            artist_id = record["artist_id"]
            if artist_id in self._record_by_id:
                raise KnowledgeBaseConflictError(f"duplicate artist_id: {artist_id}")
            self._record_by_id[artist_id] = record

            canonical_key = record["canonical_name"].casefold()
            existing = canonical_names.get(canonical_key)
            if existing is not None:
                raise KnowledgeBaseConflictError(
                    f"duplicate canonical_name: {record['canonical_name']}"
                )
            canonical_names[canonical_key] = artist_id

            for name in _record_names(record):
                key = normalize_artist_name(name)
                if not key:
                    raise KnowledgeRecordValidationError(
                        f"artist name produces an empty lookup key: {name!r}"
                    )
                owner = normalized_names.get(key)
                if owner is not None and owner != artist_id:
                    raise KnowledgeBaseConflictError(
                        f"normalized artist name collision: {name!r}"
                    )
                normalized_names[key] = artist_id

        for key, artist_id in normalized_names.items():
            record = self._record_by_id[artist_id]
            if record["metadata"]["review_status"] == "published":
                self._published_name_index[key] = record

    def get_artist(self, name):
        record = self._published_name_index.get(normalize_artist_name(name))
        return legacy_artist_view(record) if record is not None else None

    def get_knowledge_record(self, name):
        record = self._published_name_index.get(normalize_artist_name(name))
        return deepcopy(record) if record is not None else None

    def list_artists(self):
        records = {
            record["artist_id"]: record
            for record in self._published_name_index.values()
        }
        return sorted(
            (record["canonical_name"] for record in records.values()),
            key=str.casefold,
        )

    def published_records(self):
        return tuple(
            deepcopy(record)
            for record in self._records
            if record["metadata"]["review_status"] == "published"
        )


__all__ = [
    "STYLE_PROFILE_FIELDS",
    "KNOWLEDGE_RECORD_FIELDS",
    "KNOWLEDGE_METADATA_FIELDS",
    "KNOWLEDGE_SEMANTIC_FIELDS",
    "EVIDENCE_FIELDS",
    "SUPPORTED_PROFILE_SCHEMA_VERSIONS",
    "SUPPORTED_REVIEW_STATUSES",
    "SUPPORTED_EVIDENCE_TYPES",
    "KnowledgeRecordValidationError",
    "KnowledgeBaseConflictError",
    "KnowledgeBaseLoader",
    "normalize_artist_name",
    "validate_knowledge_record",
    "legacy_artist_view",
    "project_semantic_style_profile",
]
