from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.domain.agent.capabilities.comparison import ComparisonCapability
from app.domain.agent.capabilities.recommendation import RecommendationCapability
from app.domain.agent.capability import CapabilityContext
from app.domain.agent.intent import Intent
from app.domain.agent.orchestrator import AgentOrchestrator
from app.domain.agent.registry import CapabilityRegistry
from app.domain.models.message import Message, MessageRole

# ---------------------------------------------------------------------------
# RecommendationCapability: usage-aware prompts
# ---------------------------------------------------------------------------

class TestRecommendationUsageGuidance:
    def test_includes_usage_guidance_when_urbano(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(
            user_message="necesito un auto",
            automotive_data="[VEHICLE_SEARCH]\nToyota Corolla",
            usage="urbano",
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "ORIENTACIÓN DE USO" in result
        assert "urbano" in result.lower()
        assert "sedan" in result.lower() or "hatchback" in result.lower()

    def test_includes_usage_guidance_when_familiar(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(
            user_message="auto familiar",
            usage="familiar",
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "ORIENTACIÓN DE USO" in result
        assert "SUV" in result

    def test_no_usage_guidance_when_empty(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(user_message="hola")
        result = cap.get_system_prompt_enhancement(ctx)
        assert "ORIENTACIÓN DE USO" not in result

    def test_automotive_data_emphasized_as_primary_source(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(
            user_message="necesito un auto",
            automotive_data="[VEHICLE_SEARCH]\n3 vehículos",
            budget=25000.0,
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "fuente principal" in result
        assert "[VEHICLE_SEARCH]" in result

    def test_no_automotive_data_returns_base_only(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(user_message="hola")
        result = cap.get_system_prompt_enhancement(ctx)
        assert "DATOS AUTOMOTRICES" not in result


class TestRecommendationContextEnrichment:
    def test_includes_usage_label(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(
            user_message="hola",
            usage="familiar",
        )
        result = cap.get_context_enrichment(ctx)
        assert "familiar" in result.lower()

    def test_includes_automotive_data_instruction(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(
            user_message="hola",
            automotive_data="[VEHICLE_SEARCH]\nResults",
        )
        result = cap.get_context_enrichment(ctx)
        assert "datos reales" in result.lower()

    def test_budget_and_usage_together(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(
            user_message="hola",
            budget=30000.0,
            usage="trabajo",
        )
        result = cap.get_context_enrichment(ctx)
        assert "$30,000" in result
        assert "trabajo" in result.lower()


class TestRecommendationFollowupWithUsage:
    def test_returns_usage_when_missing(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(user_message="hola", budget=25000.0)
        fields = cap.get_required_fields(ctx)
        names = [f.name for f in fields]
        assert "usage" in names

    def test_usage_priority_between_budget_and_terrain(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(user_message="hola")
        fields = cap.get_required_fields(ctx)
        names = [f.name for f in fields]
        assert names.index("budget") < names.index("usage")
        assert names.index("usage") < names.index("terrain")

    def test_no_usage_followup_when_present(self) -> None:
        cap = RecommendationCapability()
        ctx = CapabilityContext(
            user_message="hola",
            budget=25000.0,
            usage="urbano",
            terrain="city",
            engine_type="gasoline",
        )
        assert cap.get_required_fields(ctx) == []


# ---------------------------------------------------------------------------
# ComparisonCapability: focus-aware prompts
# ---------------------------------------------------------------------------

class TestComparisonFocusGuidance:
    def test_includes_focus_guidance_when_performance(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara Honda y Toyota",
            automotive_data="[VEHICLE_DETAILS]\nHonda Civic\nToyota Corolla",
            vehicles_count=2,
            focus="performance",
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "ENFOQUE EN RENDIMIENTO" in result
        assert "caballos" in result.lower() or "torque" in result.lower()

    def test_includes_focus_guidance_when_economy(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            vehicles_count=2,
            focus="economy",
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "ENFOQUE EN ECONOMÍA" in result
        assert "consumo" in result.lower()

    def test_includes_focus_guidance_when_safety(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            vehicles_count=2,
            focus="safety",
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "ENFOQUE EN SEGURIDAD" in result

    def test_includes_focus_guidance_when_value(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            vehicles_count=2,
            focus="value",
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "ENFOQUE EN RELACIÓN PRECIO-VALOR" in result

    def test_no_focus_guidance_when_all(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            vehicles_count=2,
            focus="all",
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "ENFOQUE EN" not in result

    def test_automotive_data_primary_source(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            automotive_data="[VEHICLE_DETAILS]\nHonda Civic\nToyota Corolla",
            vehicles_count=2,
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "datos reales del mercado" in result.lower()
        assert "[VEHICLE_DETAILS]" in result


class TestComparisonContextEnrichment:
    def test_focus_performance_enrichment(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            vehicles_count=2,
            focus="performance",
        )
        result = cap.get_context_enrichment(ctx)
        assert "rendimiento" in result.lower()
        assert "priorizar" in result.lower()

    def test_focus_economy_enrichment(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            vehicles_count=2,
            focus="economy",
        )
        result = cap.get_context_enrichment(ctx)
        assert "economía" in result.lower()

    def test_no_focus_enrichment_when_all(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            vehicles_count=2,
            focus="all",
        )
        result = cap.get_context_enrichment(ctx)
        assert "priorizar" not in result.lower()

    def test_automotive_data_enrichment(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            automotive_data="[VEHICLE_DETAILS]\nData",
            vehicles_count=2,
        )
        result = cap.get_context_enrichment(ctx)
        assert "datos reales" in result.lower()

    def test_vehicle_count_in_enrichment(self) -> None:
        cap = ComparisonCapability()
        ctx = CapabilityContext(
            user_message="compara",
            vehicles_count=3,
        )
        result = cap.get_context_enrichment(ctx)
        assert "3 vehículos" in result


# ---------------------------------------------------------------------------
# Orchestrator: usage and focus propagation
# ---------------------------------------------------------------------------

def _orchestrator_with_tool(
    automotive_tool: object | None = None,
) -> AgentOrchestrator:
    llm = MagicMock()
    registry = CapabilityRegistry()
    registry.register(RecommendationCapability())
    registry.register(ComparisonCapability())
    return AgentOrchestrator(
        llm=llm,
        registry=registry,
        automotive_tool=automotive_tool,
    )


class TestOrchestratorUsagePropagation:
    @pytest.mark.asyncio
    async def test_usage_reaches_capability_context(self) -> None:
        orch = _orchestrator_with_tool()
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
    async def test_focus_reaches_comparison_prompt(self) -> None:
        orch = _orchestrator_with_tool()
        msg = Message(
            content="compara Honda Civic con Toyota Corolla",
            role=MessageRole.USER,
            conversation_id="test",
        )
        result = await orch.orchestrate(
            "compara Honda Civic con Toyota Corolla",
            [msg],
            focus="economy",
        )
        assert result.intent == Intent.COMPARISON
        assert "economía" in result.system_prompt.lower()


class TestOrchestratorCapabilityContextFields:
    @pytest.mark.asyncio
    async def test_usage_appears_in_context_enrichment(self) -> None:
        orch = _orchestrator_with_tool()
        msg = Message(
            content="necesito un auto",
            role=MessageRole.USER,
            conversation_id="test",
        )
        result = await orch.orchestrate(
            "necesito un auto", [msg],
            budget=25000.0,
            usage="familiar",
        )
        assert "familiar" in result.context_enrichment.lower()

    @pytest.mark.asyncio
    async def test_focus_default_is_all(self) -> None:
        orch = _orchestrator_with_tool()
        msg = Message(
            content="compara Honda y Toyota",
            role=MessageRole.USER,
            conversation_id="test",
        )
        result = await orch.orchestrate(
            "compara Honda y Toyota", [msg],
        )
        assert result.intent == Intent.COMPARISON
        assert "ENFOQUE EN" not in result.system_prompt

