import pytest

from hyperai.skill_runtime import (CapabilityRouter, ChainExecutor, Skill,
                                   SkillRegistry, SkillResult, SkillStatus,
                                   VerificationEvidence)


def verified(value, output):
    return ["runtime-check"]


def test_router_selects_minimum_sufficient_chain():
    registry = SkillRegistry()
    registry.register(
        Skill("discover", "discover", "find capability", handler=lambda x: x + "-d")
    )
    registry.register(
        Skill(
            "specialist",
            "specialist",
            "analyze capability",
            handler=lambda x: x + "-s",
            verifier=verified,
        )
    )
    registry.register(
        Skill("unrelated", "unrelated", "weather", handler=lambda x: x + "-u")
    )

    plan = CapabilityRouter(registry).select("analyze capability")

    assert [skill.id for skill in plan] == ["specialist"]


def test_router_can_select_multiple_capabilities():
    registry = SkillRegistry()
    registry.register(Skill("first", "First", "first", handler=lambda x: x))
    registry.register(Skill("second", "Second", "second", handler=lambda x: x))

    plan = CapabilityRouter(registry).select("first second")

    assert [skill.id for skill in plan] == ["first", "second"]


def test_chain_passes_output_to_next_skill_and_records_provenance():
    registry = SkillRegistry()
    registry.register(
        Skill("a", "A", "first", handler=lambda x: x + "A", verifier=verified)
    )
    registry.register(
        Skill("b", "B", "second", handler=lambda x: x + "B", verifier=verified)
    )
    executor = ChainExecutor(registry)

    results = executor.run(["a", "b"], "start")

    assert [r.status for r in results] == [SkillStatus.VERIFIED, SkillStatus.VERIFIED]
    assert results[-1].output == "startAB"
    assert results[1].input_refs == [results[0].run_id]


def test_verified_result_requires_explicit_verifier():
    registry = SkillRegistry()
    registry.register(Skill("a", "A", "first", handler=lambda x: x))
    result = ChainExecutor(registry).invoke("a", "x", verify=True)

    assert result.status == SkillStatus.RETURNED
    assert result.next_eligible is False


def test_returned_result_cannot_be_verified_without_evidence():
    registry = SkillRegistry()
    registry.register(Skill("a", "A", "first", handler=lambda x: x))
    result = ChainExecutor(registry).invoke("a", "x", verify=False)

    assert result.status == SkillStatus.RETURNED
    assert result.next_eligible is False


def test_failed_skill_does_not_allow_downstream_execution():
    registry = SkillRegistry()
    registry.register(
        Skill(
            "bad",
            "bad",
            "first",
            handler=lambda x: (_ for _ in ()).throw(RuntimeError("boom")),
            verifier=verified,
        )
    )
    registry.register(
        Skill("next", "next", "second", handler=lambda x: x + "next", verifier=verified)
    )
    results = ChainExecutor(registry).run(["bad", "next"], "x")

    assert results[0].status == SkillStatus.FAILED
    assert len(results) == 1


def test_mutation_capability_requires_explicit_authorization():
    registry = SkillRegistry()
    registry.register(
        Skill(
            "mutate",
            "Mutate",
            "mutate",
            handler=lambda x: x,
            side_effect_class="mutation",
            permission_class="user-gated",
            verifier=verified,
        )
    )
    result = ChainExecutor(registry).invoke("mutate", "x")

    assert result.status == SkillStatus.FAILED
    assert result.error_class == "PERMISSION_DENIED"


def test_registry_rejects_verified_without_evidence():
    registry = SkillRegistry()
    skill = registry.register(Skill("a", "A", "first", handler=lambda x: x))

    with pytest.raises(ValueError):
        registry.promote(skill.id, SkillStatus.VERIFIED, evidence=[])


def test_registry_rejects_unbound_verified_evidence():
    registry = SkillRegistry()
    skill = registry.register(Skill("a", "A", "first", handler=lambda x: x))
    evidence = VerificationEvidence(
        skill_id="other",
        version=skill.version,
        run_id="run",
        evidence_id="evidence",
        output_digest="digest",
    )

    with pytest.raises(ValueError):
        registry.promote(skill.id, SkillStatus.VERIFIED, evidence=[evidence])
