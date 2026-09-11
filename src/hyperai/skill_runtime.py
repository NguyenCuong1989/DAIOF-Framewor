from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional
from uuid import uuid4


class SkillStatus(str, Enum):
    DISCOVERED = "discovered"
    SELECTED = "selected"
    INVOKED = "invoked"
    RETURNED = "returned"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass
class Skill:
    id: str
    name: str
    trigger: str
    handler: Callable[[Any], Any]
    availability: str = "available"
    side_effect_class: str = "none"
    status: SkillStatus = SkillStatus.DISCOVERED


@dataclass
class SkillResult:
    skill_id: str
    run_id: str
    status: SkillStatus
    input: Any
    output: Any = None
    input_refs: List[str] = field(default_factory=list)
    output_refs: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    error_class: Optional[str] = None
    next_eligible: bool = False


class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill):
        if skill.id in self._skills:
            raise ValueError(f"skill already registered: {skill.id}")
        self._skills[skill.id] = skill
        return skill

    def get(self, skill_id: str):
        return self._skills[skill_id]

    def discover(self, task: str):
        terms = set(task.lower().split())
        return [s for s in self._skills.values() if terms & set(s.trigger.lower().split())]

    def promote(self, skill_id: str, status: SkillStatus, evidence: Iterable[str]):
        evidence = list(evidence)
        if status == SkillStatus.VERIFIED and not evidence:
            raise ValueError("verified status requires evidence")
        self._skills[skill_id].status = status
        return self._skills[skill_id]


class CapabilityRouter:
    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def select(self, task: str):
        candidates = [s for s in self.registry.discover(task) if s.availability == "available"]
        if not candidates:
            raise LookupError(f"no available capability for task: {task}")
        candidates.sort(key=lambda s: (s.side_effect_class != "none", len(s.trigger)))
        selected = candidates[:1]
        for skill in selected:
            skill.status = SkillStatus.SELECTED
        return selected


class ChainExecutor:
    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def invoke(self, skill_id: str, value: Any, verify: bool = True, input_refs=None):
        skill = self.registry.get(skill_id)
        run_id = str(uuid4())
        try:
            skill.status = SkillStatus.INVOKED
            output = skill.handler(value)
        except Exception as exc:
            skill.status = SkillStatus.FAILED
            return SkillResult(skill_id, run_id, SkillStatus.FAILED, value, input_refs=list(input_refs or []), error_class=type(exc).__name__)
        skill.status = SkillStatus.RETURNED
        if not verify:
            return SkillResult(skill_id, run_id, SkillStatus.RETURNED, value, output, list(input_refs or []))
        skill.status = SkillStatus.VERIFIED
        return SkillResult(skill_id, run_id, SkillStatus.VERIFIED, value, output, list(input_refs or []), [run_id], [run_id], next_eligible=True)

    def run(self, skill_ids, value):
        results = []
        current = value
        previous = None
        for skill_id in skill_ids:
            result = self.invoke(skill_id, current, True, [previous] if previous else [])
            results.append(result)
            if not result.next_eligible:
                break
            current = result.output
            previous = result.run_id
        return results
