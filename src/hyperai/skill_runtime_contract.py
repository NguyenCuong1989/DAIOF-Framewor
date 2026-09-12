"""Stable contract vocabulary for the APΩ skill runtime."""

SKILL_CONTRACT_FIELDS = (
    "id",
    "name",
    "type",
    "source",
    "path",
    "trigger",
    "availability",
    "side_effect_class",
    "permission_class",
    "version",
    "provenance",
    "status",
    "contract_hash",
    "last_verified_at",
)

RESULT_STATUS = (
    "invoked",
    "returned",
    "observed",
    "failed",
    "partial",
    "verified",
)

FAILURE_CLASSES = (
    "MISSING",
    "UNAVAILABLE",
    "PERMISSION_DENIED",
    "WRONG_SCOPE",
    "WRONG_TARGET",
    "TIMEOUT",
    "INVALID_INPUT",
    "DEPENDENCY_FAILURE",
    "PARTIAL_RESULT",
    "STALE_STATE",
    "AMBIGUOUS",
)
