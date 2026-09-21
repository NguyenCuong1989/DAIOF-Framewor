from hyperai.skill_runtime_contract import FAILURE_CLASSES, RESULT_STATUS, SKILL_CONTRACT_FIELDS


def test_contract_vocabulary_is_complete():
    assert {"id", "trigger", "availability", "side_effect_class", "permission_class", "provenance", "status"}.issubset(SKILL_CONTRACT_FIELDS)
    assert {"returned", "failed", "verified"}.issubset(RESULT_STATUS)
    assert {"MISSING", "PERMISSION_DENIED", "STALE_STATE", "AMBIGUOUS"}.issubset(FAILURE_CLASSES)
