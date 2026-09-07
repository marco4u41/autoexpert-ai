from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.domain.agent.capabilities.comparison import ComparisonCapability
from app.domain.agent.capabilities.diagnosis import DiagnosisCapability
from app.domain.agent.capabilities.recommendation import RecommendationCapability
from app.domain.agent.capability import CapabilityContext
from app.domain.agent.followup import FollowupField
from app.domain.agent.intent import Intent
from app.domain.agent.orchestrator import AgentOrchestrator
from app.domain.agent.registry import CapabilityRegistry

# ---------------------------------------------------------------------------
# FollowupField
# ---------------------------------------------------------------------------

class TestFollowupField:
    def test_frozen(self) -> None:
        f = FollowupField(name="budget", question="¿Presupuesto?", priority=1)
        with pytest.raises(AttributeError):
            f.name = "changed"  # type: ignore[misc]

    def test_slots(self) -> None:
        f = FollowupField(name="budget", question="¿Presupuesto?", priority=1)
        with pytest.raises((AttributeError, TypeError)):
            f.extra = True  # type: ignore[attr-defined]

    def test_priority_ordering(self) -> None:
        a = FollowupField(name="a", question="a", priority=3)
        b = FollowupField(name="b", question="b", priority=1)
        assert b.priority < a.priority


# ---------------------------------------------------------------------------
# Capability.get_required_fields — per capability
# ---------------------------------------------------------------------------

class TestRecommendationRequiredFields:
    def test_returns_budget_when_missing(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(user_message="hola")
        fields = cap.get_required_fields(ctx)
        names = [f.name for f in fields]
        assert "budget" in names

    def test_returns_terrain_when_missing(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(user_message="hola", budget=25000.0)
        fields = cap.get_required_fields(ctx)
        names = [f.name for f in fields]
        assert "terrain" in names

    def test_returns_engine_type_when_missing(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(
            user_message="hola", budget=25000.0, terrain="city",
        )
        fields = cap.get_required_fields(ctx)
        names = [f.name for f in fields]
        assert "engine_type" in names

    def test_empty_when_all_present(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(
            user_message="hola",
            budget=25000.0,
            usage="urbano",
            terrain="city",
            engine_type="gasoline",
        )
        assert cap.get_required_fields(ctx) == []


class TestComparisonRequiredFields:
    def test_returns_vehicles_when_less_than_two(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(user_message="compara", vehicles_count=0)
        fields = cap.get_required_fields(ctx)
        assert len(fields) == 1
        assert fields[0].name == "vehicles"
        assert fields[0].priority == 1

    def test_returns_vehicles_when_one_vehicle(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(user_message="compara", vehicles_count=1)
        fields = cap.get_required_fields(ctx)
        assert len(fields) == 1

    def test_empty_when_two_vehicles(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(user_message="compara", vehicles_count=2)
        assert cap.get_required_fields(ctx) == []


class TestDiagnosisRequiredFields:
    def test_returns_vehicle_when_missing(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(user_message="hace ruido")
        fields = cap.get_required_fields(ctx)
        names = [f.name for f in fields]
        assert "vehicle" in names

    def test_returns_symptoms_when_missing(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="mi auto", vehicles_count=1,
        )
        fields = cap.get_required_fields(ctx)
        names = [f.name for f in fields]
        assert "symptoms" in names

    def test_empty_when_all_present(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="mi Corolla hace ruido",
            vehicles_count=1,
            has_symptoms=True,
        )
        assert cap.get_required_fields(ctx) == []


# ---------------------------------------------------------------------------
# CapabilityRegistry.detect_missing_info
# ---------------------------------------------------------------------------

class TestDetectMissingInfo:
    def test_aggregates_from_multiple_capabilities(self) -> None:
        registry = CapabilityRegistry()
        registry.register(RecommendationCapability())
        registry.register(ComparisonCapability())

        ctx = CapabilityContext(user_message="hola")
        fields = registry.detect_missing_info(Intent.RECOMMENDATION, ctx)
        names = [f.name for f in fields]
        assert "budget" in names
        assert "terrain" in names

    def test_sorted_by_priority(self) -> None:
        registry = CapabilityRegistry()
        registry.register(RecommendationCapability())

        ctx = CapabilityContext(user_message="hola")
        fields = registry.detect_missing_info(Intent.RECOMMENDATION, ctx)
        priorities = [f.priority for f in fields]
        assert priorities == sorted(priorities)

    def test_deduplicates_by_name(self) -> None:
        class DupCap(RecommendationCapability):
            @property
            def name(self) -> str:
                return "dup"

        registry = CapabilityRegistry()
        registry.register(RecommendationCapability())
        registry.register(DupCap())

        ctx = CapabilityContext(user_message="hola")
        fields = registry.detect_missing_info(Intent.RECOMMENDATION, ctx)
        names = [f.name for f in fields]
        assert len(names) == len(set(names))

    def test_empty_for_general_intent(self) -> None:
        registry = CapabilityRegistry()
        registry.register(RecommendationCapability())

        ctx = CapabilityContext(user_message="hola")
        fields = registry.detect_missing_info(Intent.GENERAL, ctx)
        assert fields == []

    def test_empty_when_context_complete(self) -> None:
        registry = CapabilityRegistry()
        registry.register(RecommendationCapability())

        ctx = CapabilityContext(
            user_message="hola",
            budget=25000.0,
            usage="urbano",
            terrain="city",
            engine_type="gasoline",
        )
        fields = registry.detect_missing_info(Intent.RECOMMENDATION, ctx)
        assert fields == []


# ---------------------------------------------------------------------------
# Orchestrator._format_followup_instructions
# ---------------------------------------------------------------------------

class TestFormatFollowupInstructions:
    def test_contains_priority_labels(self) -> None:
        fields = [
            FollowupField(name="budget", question="¿Presupuesto?", priority=1),
            FollowupField(name="terrain", question="¿Terreno?", priority=2),
            FollowupField(name="engine_type", question="¿Motor?", priority=3),
        ]
        result = AgentOrchestrator._format_followup_instructions(fields)
        assert "CRÍTICO" in result
        assert "IMPORTANTE" in result
        assert "COMPLEMENTARIO" in result

    def test_contains_all_questions(self) -> None:
        fields = [
            FollowupField(name="budget", question="¿Cuánto?", priority=1),
        ]
        result = AgentOrchestrator._format_followup_instructions(fields)
        assert "¿Cuánto?" in result

    def test_header_present(self) -> None:
        fields = [
            FollowupField(name="x", question="q", priority=1),
        ]
        result = AgentOrchestrator._format_followup_instructions(fields)
        assert "INSTRUCCIONES DE SEGUIMIENTO" in result
        assert "NO inventes" in result


# ---------------------------------------------------------------------------
# Orchestrator.orchestrate — follow-up injection
# ---------------------------------------------------------------------------

def _orchestrator_with_tool(
    automotive_tool: object | None = None,
) -> AgentOrchestrator:
    llm = MagicMock()
    registry = CapabilityRegistry()
    registry.register(RecommendationCapability())
    registry.register(ComparisonCapability())
    registry.register(DiagnosisCapability())
    return AgentOrchestrator(
        llm=llm,
        registry=registry,
        automotive_tool=automotive_tool,
    )


class TestOrchestratorFollowup:
    @pytest.mark.asyncio
    async def test_injects_followup_when_budget_missing(self) -> None:
        orch = _orchestrator_with_tool()
        from app.domain.models.message import Message, MessageRole

        msg = Message(
            content="necesito un auto",
            role=MessageRole.USER,
            conversation_id="test",
        )
        result = await orch.orchestrate(
            "necesito un auto", [msg],
        )

        assert "INSTRUCCIONES DE SEGUIMIENTO" in result.system_prompt
        assert "CRÍTICO" in result.system_prompt

    @pytest.mark.asyncio
    async def test_no_followup_when_context_complete(self) -> None:
        orch = _orchestrator_with_tool()
        from app.domain.models.message import Message, MessageRole

        msg = Message(
            content="necesito un auto",
            role=MessageRole.USER,
            conversation_id="test",
        )
        result = await orch.orchestrate(
            "necesito un auto", [msg],
            budget=25000.0,
            terrain="city",
            engine_type="gasoline",
            usage="urbano",
        )

        assert "INSTRUCCIONES DE SEGUIMIENTO" not in result.system_prompt

    @pytest.mark.asyncio
    async def test_no_followup_for_general_intent(self) -> None:
        orch = _orchestrator_with_tool()
        from app.domain.models.message import Message, MessageRole

        msg = Message(
            content="hola",
            role=MessageRole.USER,
            conversation_id="test",
        )
        result = await orch.orchestrate(
            "hola", [msg],
        )

        assert "INSTRUCCIONES DE SEGUIMIENTO" not in result.system_prompt
