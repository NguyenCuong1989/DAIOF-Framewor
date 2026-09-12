import pytest

from hyperai.skill_runtime import (
    CapabilityRouter,
    ChainExecutor,
    Skill,
    SkillRegistry,
    SkillResult,
    SkillStatus,
)


def test_router_selects_minimum_sufficient_chain():
    registry = SkillRegistry()
    registry.register(Skill("discover", "discover", "find capability", handler=lambda x: x + "-d"))
    registry.register(Skill("specialist", "specialist", "analyze capability", handler=lambda x: x + "-s"))
    registry.register(Skill("unrelated", "unrelated", "weather", handler=lambda x: x + "-u"))

    plan = CapabilityRouter(registry).select("analyze capability")

    assert [skill.id for skill in plan] == ["specialist"]


def test_chain_passes_output_to_next_skill_and_records_provenance():
    registry = SkillRegistry()
    registry.register(Skill("a", "A", "first", handler=lambda x: x + "A"))
    registry.register(Skill("b", "B", "second", handler=lambda x: x + "B"))
    executor = ChainExecutor(registry)

    results = executor.run(["a", "b"], "start")

    assert [r.status for r in results] == [SkillStatus.VERIFIED, SkillStatus.VERIFIED]
    assert results[-1].output == "startAB"
    assert results[1].input_refs == [results[0].run_id]
    assert results[1].evidence_refs == [results[0].run_id]


def test_returned_result_cannot_be_verified_without_evidence():
    registry = SkillRegistry()
    registry.register(Skill("a", "A", "first", handler=lambda x: x))
    executor = ChainExecutor(registry)

    result = executor.invoke("a", "x", verify=False)

    assert result.status == SkillStatus.RETURNED
    assert result.next_eligible is False


def test_failed_skill_does_not_allow_downstream_execution():
    registry = SkillRegistry()
    registry.register(Skill("bad", "bad", "first", handler=lambda x: (_ for _ in ()).throw(RuntimeError("boom"))))
    registry.register(Skill("next", "next", "second", handler=lambda x: x + "next"))
    executor = ChainExecutor(registry)

    results = executor.run(["bad", "next"], "x")

    assert results[0].status == SkillStatus.FAILED
    assert len(results) == 1


def test_registry_rejects_verified_without_evidence():
    registry = SkillRegistry()
    skill = Skill("a", "A", "first", handler=lambda x: x)

    with pytest.raises(ValueError):
        registry.promote(skill.id, SkillStatus.VERIFIED, evidence=[])
