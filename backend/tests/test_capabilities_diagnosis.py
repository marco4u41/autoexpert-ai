from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.agent.capabilities.diagnosis import DiagnosisCapability
from app.domain.agent.capability import CapabilityContext
from app.domain.agent.intent import Intent
from app.domain.agent.orchestrator import AgentOrchestrator
from app.domain.agent.registry import CapabilityRegistry
from app.domain.models.message import Message, MessageRole

# ---------------------------------------------------------------------------
# DiagnosisCapability: automotive data in prompts
# ---------------------------------------------------------------------------

class TestDiagnosisAutomotiveDataPrompt:
    def test_includes_automotive_data_when_present(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="mi auto hace ruido",
            automotive_data="[VEHICLE_DETAILS]\nToyota Corolla 2020\nMotor 1.8L",
            vehicles_count=1,
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "DATOS AUTOMOTRICES REALES DEL VEHÍCULO" in result
        assert "[VEHICLE_DETAILS]" in result
        assert "Toyota Corolla 2020" in result

    def test_no_automotive_data_returns_base_only(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(user_message="mi auto hace ruido")
        result = cap.get_system_prompt_enhancement(ctx)
        assert "DATOS AUTOMOTRICES" not in result
        assert "Modo Diagnóstico" in result

    def test_anti_hallucination_rules_with_data(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="problema con motor",
            automotive_data="[VEHICLE_DETAILS]\nFord F-150 2021",
            vehicles_count=1,
        )
        result = cap.get_system_prompt_enhancement(ctx)
        assert "NO inventes" in result
        assert "especificaciones" in result.lower()

    def test_no_anti_hallucination_rules_without_data(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(user_message="problema con motor")
        result = cap.get_system_prompt_enhancement(ctx)
        assert "NO inventes" not in result


class TestDiagnosisContextEnrichment:
    def test_includes_automotive_data_instruction(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="mi auto falla",
            automotive_data="[VEHICLE_DETAILS]\nHonda Civic specs",
            vehicles_count=1,
        )
        result = cap.get_context_enrichment(ctx)
        assert "datos reales" in result.lower()
        assert "especificaciones del motor" in result.lower()

    def test_no_automotive_data_instruction_without_data(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(user_message="mi auto falla")
        result = cap.get_context_enrichment(ctx)
        assert "datos reales del vehículo" not in result.lower()

    def test_vehicle_info_already_provided(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="mi Toyota hace ruido",
            vehicles_count=1,
        )
        result = cap.get_context_enrichment(ctx)
        assert "ya proporcionó información del vehículo" in result

    def test_no_vehicle_info_prompt_when_count_zero(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="mi auto hace ruido",
            vehicles_count=0,
        )
        result = cap.get_context_enrichment(ctx)
        assert "ya proporcionó información" not in result

    def test_symptoms_already_described(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="mi auto hace ruido al frenar",
            vehicles_count=1,
            has_symptoms=True,
        )
        result = cap.get_context_enrichment(ctx)
        assert "ya describió síntomas" in result

    def test_no_symptoms_prompt_when_none(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="tengo un problema",
            vehicles_count=0,
            has_symptoms=False,
        )
        result = cap.get_context_enrichment(ctx)
        assert "ya describió síntomas" not in result

    def test_always_recommends_mechanic(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="problema",
            automotive_data="data",
            vehicles_count=1,
            has_symptoms=True,
        )
        result = cap.get_context_enrichment(ctx)
        assert "mecánico" in result.lower()

    def test_followup_when_no_vehicle(self) -> None:
        cap = DiagnosisCapability()
        ctx = CapabilityContext(
            user_message="mi auto falla",
            vehicles_count=0,
            has_symptoms=True,
        )
        result = cap.get_context_enrichment(ctx)
        assert "solicita esos detalles" in result


# ---------------------------------------------------------------------------
# Orchestrator: diagnosis with automotive data
# ---------------------------------------------------------------------------

def _orchestrator_with_tool(
    automotive_tool: object | None = None,
) -> AgentOrchestrator:
    llm = MagicMock()
    registry = CapabilityRegistry()
    registry.register(DiagnosisCapability())
    return AgentOrchestrator(
        llm=llm,
        registry=registry,
        automotive_tool=automotive_tool,
    )


class TestOrchestratorDiagnosisData:
    @pytest.mark.asyncio
    async def test_diagnosis_intent_fetches_data(self) -> None:
        detail_result = MagicMock()
        detail_result.content = "[VEHICLE_DETAILS]\nToyota Corolla"

        mock_tool = MagicMock()
        mock_tool.get_vehicle_details = AsyncMock(return_value=detail_result)
        mock_tool.get_model_info = AsyncMock(return_value=None)

        orch = _orchestrator_with_tool(automotive_tool=mock_tool)
        msg = Message(
            content="mi Toyota Corolla hace ruido al frenar",
            role=MessageRole.USER,
            conversation_id="test",
        )
        result = await orch.orchestrate(
            "mi Toyota Corolla hace ruido al frenar", [msg],
        )
        assert result.intent == Intent.DIAGNOSIS
        assert "DATOS AUTOMOTRICES" in result.system_prompt

    @pytest.mark.asyncio
    async def test_diagnosis_no_tool_returns_base_prompt(self) -> None:
        orch = _orchestrator_with_tool(automotive_tool=None)
        msg = Message(
            content="mi auto hace ruido",
            role=MessageRole.USER,
            conversation_id="test",
        )
        result = await orch.orchestrate(
            "mi auto hace ruido", [msg],
        )
        assert result.intent == Intent.DIAGNOSIS
        assert "DATOS AUTOMOTRICES" not in result.system_prompt
        assert "Modo Diagnóstico" in result.system_prompt

