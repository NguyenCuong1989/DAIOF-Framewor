"""Evidence-gated APΩ skill runtime primitives."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Callable, Dict, Iterable, List, Optional
from uuid import uuid4


class SkillStatus(str, Enum):
    DISCOVERED = "discovered"
    SELECTED = "selected"
    INVOKED = "invoked"
    RETURNED = "returned"
    OBSERVED = "observed"
    FAILED = "failed"
    PARTIAL = "partial"
    VERIFIED = "verified"
    STALE = "stale"


@dataclass(frozen=True)
class VerificationEvidence:
    skill_id: str
    version: str
    run_id: str
    evidence_id: str
    output_digest: str
    claim: str


@dataclass
class Skill:
    id: str
    name: str
    trigger: str
    handler: Callable[[Any], Any]
    type: str = "technique"
    source: str = "local"
    path: str = ""
    availability: str = "available"
    side_effect_class: str = "none"
    permission_class: str = "none"
    version: str = "1.0.0"
    provenance: str = "runtime"
    contract_hash: str = ""
    last_verified_at: Optional[str] = None
    verifier: Optional[Callable[[Any, Any], Iterable[str]]] = None
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
        self._verification_evidence: Dict[str, VerificationEvidence] = {}

    def register(self, skill: Skill):
        if skill.id in self._skills:
            raise ValueError(f"skill already registered: {skill.id}")
        self._skills[skill.id] = skill
        return skill

    def get(self, skill_id: str):
        if skill_id not in self._skills:
            raise KeyError(f"unknown skill: {skill_id}")
        return self._skills[skill_id]

    def discover(self, task: str):
        terms = set(task.lower().split())
        if not terms:
            return []
        return [
            skill
            for skill in self._skills.values()
            if terms & set(skill.trigger.lower().split())
        ]

    def _record_verification_evidence(
        self, evidence: Iterable[VerificationEvidence]
    ) -> None:
        for item in evidence:
            if not isinstance(item, VerificationEvidence):
                raise TypeError("verification evidence must use VerificationEvidence")
            if not all(
                (
                    item.skill_id,
                    item.version,
                    item.run_id,
                    item.evidence_id,
                    item.output_digest,
                    item.claim,
                )
            ):
                raise ValueError("verification evidence fields must be non-empty")
            if item.evidence_id in self._verification_evidence:
                raise ValueError(f"duplicate evidence id: {item.evidence_id}")
            self._verification_evidence[item.evidence_id] = item

    def promote(
        self,
        skill_id: str,
        status: SkillStatus,
        evidence: Iterable[VerificationEvidence],
    ):
        evidence = list(evidence)
        skill = self.get(skill_id)
        if status == SkillStatus.VERIFIED:
            if not evidence:
                raise ValueError("verified status requires evidence")
            for item in evidence:
                if not isinstance(item, VerificationEvidence):
                    raise TypeError("verified status requires VerificationEvidence")
                if self._verification_evidence.get(item.evidence_id) != item:
                    raise ValueError("verified status requires registry-issued evidence")
                if item.skill_id != skill.id or item.version != skill.version:
                    raise ValueError("verified status requires runtime-bound evidence")
            skill.last_verified_at = datetime.now(timezone.utc).isoformat()
        skill.status = status
        return skill


class CapabilityRouter:
    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def select(self, task: str):
        terms = set(task.lower().split())
        candidates = [
            skill
            for skill in self.registry.discover(task)
            if skill.availability == "available"
        ]
        if not candidates:
            raise LookupError(f"no available capability for task: {task}")

        remaining = set(terms)
        selected = []
        pool = list(candidates)
        while pool and remaining:
            pool.sort(
                key=lambda skill: (
                    -len(remaining & set(skill.trigger.lower().split())),
                    skill.side_effect_class != "none",
                    len(skill.trigger),
                    skill.id,
                )
            )
            best = pool.pop(0)
            covered = remaining & set(best.trigger.lower().split())
            if not covered:
                break
            selected.append(best)
            remaining -= covered

        if remaining:
            raise LookupError(
                f"no sufficient capability chain for task: {task}; "
                f"uncovered terms: {sorted(remaining)}"
            )

        for skill in selected:
            skill.status = SkillStatus.SELECTED
        return selected


class ChainExecutor:
    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    @staticmethod
    def _digest(value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, default=str).encode("utf-8")
        return sha256(payload).hexdigest()

    def invoke(
        self,
        skill_id: str,
        value: Any,
        verify: bool = True,
        input_refs: Optional[Iterable[str]] = None,
        authorized: bool = False,
    ):
        skill = self.registry.get(skill_id)
        run_id = str(uuid4())
        refs = list(input_refs or [])

        if skill.side_effect_class != "none" or skill.permission_class != "none":
            if not authorized:
                return SkillResult(
                    skill_id=skill_id,
                    run_id=run_id,
                    status=SkillStatus.FAILED,
                    input=value,
                    input_refs=refs,
                    error_class="PERMISSION_DENIED",
                )

        try:
            skill.status = SkillStatus.INVOKED
            output = skill.handler(value)
        except Exception as exc:
            skill.status = SkillStatus.FAILED
            return SkillResult(
                skill_id=skill_id,
                run_id=run_id,
                status=SkillStatus.FAILED,
                input=value,
                input_refs=refs,
                error_class=type(exc).__name__,
            )

        skill.status = SkillStatus.RETURNED
        if not verify or skill.verifier is None:
            return SkillResult(
                skill_id=skill_id,
                run_id=run_id,
                status=SkillStatus.RETURNED,
                input=value,
                output=output,
                input_refs=refs,
            )

        try:
            claims = [str(claim).strip() for claim in skill.verifier(value, output)]
        except Exception as exc:
            skill.status = SkillStatus.FAILED
            return SkillResult(
                skill_id=skill_id,
                run_id=run_id,
                status=SkillStatus.FAILED,
                input=value,
                output=output,
                input_refs=refs,
                error_class=f"VERIFICATION_{type(exc).__name__}",
            )

        if not claims or any(not claim for claim in claims):
            return SkillResult(
                skill_id=skill_id,
                run_id=run_id,
                status=SkillStatus.RETURNED,
                input=value,
                output=output,
                input_refs=refs,
            )

        output_digest = self._digest(output)
        evidence = [
            VerificationEvidence(
                skill_id=skill.id,
                version=skill.version,
                run_id=run_id,
                evidence_id=str(uuid4()),
                output_digest=output_digest,
                claim=claim,
            )
            for claim in claims
        ]
        self.registry._record_verification_evidence(evidence)
        self.registry.promote(skill.id, SkillStatus.VERIFIED, evidence)
        return SkillResult(
            skill_id=skill_id,
            run_id=run_id,
            status=SkillStatus.VERIFIED,
            input=value,
            output=output,
            input_refs=refs,
            output_refs=[run_id],
            evidence_refs=[item.evidence_id for item in evidence],
            next_eligible=True,
        )

    def run(self, skill_ids: Iterable[str], value: Any, authorized: bool = False):
        results = []
        current = value
        previous = None
        for skill_id in skill_ids:
            result = self.invoke(
                skill_id,
                current,
                verify=True,
                input_refs=[previous] if previous else [],
                authorized=authorized,
            )
            results.append(result)
            if not result.next_eligible:
                break
            current = result.output
            previous = result.run_id
        return results
