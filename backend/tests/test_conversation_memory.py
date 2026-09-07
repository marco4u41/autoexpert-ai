from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.agent.memory import ConversationMemoryService
from app.domain.models.conversation import Conversation
from app.domain.models.message import Message, MessageRole

# ---------------------------------------------------------------------------
# Subfase 5.7 â€” ConversationMemoryService
# ---------------------------------------------------------------------------

class TestConversationMemoryService:
    def test_empty_messages_returns_empty(self) -> None:
        svc = ConversationMemoryService()
        assert svc.generate_summary([]) == ""

    def test_extracts_vehicle_info(self) -> None:
        svc = ConversationMemoryService()
        messages = [
            Message(
                content="tengo un Toyota Corolla 2020",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = svc.generate_summary(messages)
        assert "Toyota" in summary
        assert "Corolla" in summary

    def test_extracts_budget(self) -> None:
        svc = ConversationMemoryService()
        messages = [
            Message(
                content="mi presupuesto es $25000",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = svc.generate_summary(messages)
        assert "$25,000" in summary

    def test_extracts_usage(self) -> None:
        svc = ConversationMemoryService()
        messages = [
            Message(
                content="necesito un auto familiar para la ciudad",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = svc.generate_summary(messages)
        assert "Uso:" in summary

    def test_extracts_diagnosis_symptoms(self) -> None:
        svc = ConversationMemoryService()
        messages = [
            Message(
                content="mi auto hace ruido al frenar y humea",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = svc.generate_summary(messages)
        assert "Problema:" in summary

    def test_extracts_brands(self) -> None:
        svc = ConversationMemoryService()
        messages = [
            Message(
                content="me gustan Honda y Toyota",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = svc.generate_summary(messages)
        assert "Marcas:" in summary

    def test_multiple_fields_combined(self) -> None:
        svc = ConversationMemoryService()
        messages = [
            Message(
                content="tengo un Honda Civic y mi presupuesto es $20000",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = svc.generate_summary(messages)
        assert "Honda" in summary
        assert "$20,000" in summary
        assert ";" in summary

    def test_ignores_assistant_messages(self) -> None:
        svc = ConversationMemoryService()
        messages = [
            Message(
                content="asistente: hola",
                role=MessageRole.ASSISTANT,
                conversation_id="c1",
            ),
            Message(
                content="tengo un Toyota",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = svc.generate_summary(messages)
        assert "toyota" in summary.lower()

    def test_custom_extractor(self) -> None:
        extractor = MagicMock()
        extractor.extract.return_value = MagicMock(
            vehicles=[],
            budget=None,
            usage="",
            terrain=None,
            mentioned_brands=[],
            has_diagnosed_issue=False,
            diagnosis_symptoms=[],
            preferences=[],
        )
        svc = ConversationMemoryService(extractor=extractor)
        messages = [
            Message(
                content="hola",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = svc.generate_summary(messages)
        assert summary == ""
        extractor.extract.assert_called_once_with(messages)


# ---------------------------------------------------------------------------
# Subfase 5.7 â€” Conversation domain model
# ---------------------------------------------------------------------------

class TestConversationSummaryField:
    def test_default_summary_empty(self) -> None:
        conv = Conversation(title="test")
        assert conv.summary == ""

    def test_summary_settable(self) -> None:
        conv = Conversation(title="test", summary="VehÃ­culos: Toyota Corolla")
        assert conv.summary == "VehÃ­culos: Toyota Corolla"

    def test_summary_persists_through_touch(self) -> None:
        conv = Conversation(title="test", summary="data")
        conv.touch()
        assert conv.summary == "data"


# ---------------------------------------------------------------------------
# Subfase 5.7 â€” ContextManager integration with summaries
# ---------------------------------------------------------------------------

class TestContextManagerSummaries:
    @pytest.mark.asyncio
    async def test_build_context_loads_recent_summaries(self) -> None:
        from app.domain.agent.context.manager import ContextManager

        conv1 = Conversation(title="conv1", summary="VehÃ­culos: Honda Civic")
        conv2 = Conversation(title="conv2", summary="Presupuesto: $20,000")

        mock_repo = AsyncMock()
        mock_repo.get_recent.return_value = [conv1, conv2]

        mgr = ContextManager(conversation_repo=mock_repo)
        messages = [
            Message(
                content="hola",
                role=MessageRole.USER,
                conversation_id="current",
            ),
        ]
        _, context_block = await mgr.build_context(
            messages,
            exclude_conversation_id="current",
        )
        assert "Honda Civic" in context_block
        assert "$20,000" in context_block

    @pytest.mark.asyncio
    async def test_build_context_excludes_current_conversation(self) -> None:
        from app.domain.agent.context.manager import ContextManager

        conv_current = Conversation(
            title="current",
            summary="Problema: ruido",
            id="conv-current-123",
        )
        conv_other = Conversation(
            title="other",
            summary="VehÃ­culos: Toyota",
            id="conv-other-456",
        )

        mock_repo = AsyncMock()
        mock_repo.get_recent.return_value = [conv_current, conv_other]

        mgr = ContextManager(conversation_repo=mock_repo)
        messages = [
            Message(
                content="hola",
                role=MessageRole.USER,
                conversation_id="current",
            ),
        ]
        _, context_block = await mgr.build_context(
            messages,
            exclude_conversation_id="conv-current-123",
        )
        assert "ruido" not in context_block
        assert "Toyota" in context_block

    @pytest.mark.asyncio
    async def test_build_context_no_repo_still_works(self) -> None:
        from app.domain.agent.context.manager import ContextManager

        mgr = ContextManager(conversation_repo=None)
        messages = [
            Message(
                content="hola",
                role=MessageRole.USER,
                conversation_id="test",
            ),
        ]
        _, context_block = await mgr.build_context(messages)
        assert "Conversaciones anteriores" not in context_block

    @pytest.mark.asyncio
    async def test_build_context_repo_error_still_works(self) -> None:
        from app.domain.agent.context.manager import ContextManager

        mock_repo = AsyncMock()
        mock_repo.get_recent.side_effect = Exception("DB error")

        mgr = ContextManager(conversation_repo=mock_repo)
        messages = [
            Message(
                content="hola",
                role=MessageRole.USER,
                conversation_id="test",
            ),
        ]
        _, context_block = await mgr.build_context(messages)
        assert "Conversaciones anteriores" not in context_block

    @pytest.mark.asyncio
    async def test_update_conversation_summary(self) -> None:
        from app.domain.agent.context.manager import ContextManager

        conv = Conversation(title="test", id="c1")
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = conv
        mock_repo.update.return_value = conv

        mgr = ContextManager(conversation_repo=mock_repo)
        messages = [
            Message(
                content="tengo un Toyota Corolla y presupuesto $25000",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = await mgr.update_conversation_summary(messages, "c1")
        assert "Toyota" in summary
        assert "$25,000" in summary
        assert conv.summary == summary
        mock_repo.update.assert_called_once_with(conv)

    @pytest.mark.asyncio
    async def test_update_conversation_summary_no_repo(self) -> None:
        from app.domain.agent.context.manager import ContextManager

        mgr = ContextManager(conversation_repo=None)
        messages = [
            Message(
                content="hola",
                role=MessageRole.USER,
                conversation_id="c1",
            ),
        ]
        summary = await mgr.update_conversation_summary(messages, "c1")
        assert summary == ""

    @pytest.mark.asyncio
    async def test_empty_messages_no_summaries_no_context(self) -> None:
        from app.domain.agent.context.manager import ContextManager

        mock_repo = AsyncMock()
        mock_repo.get_recent.return_value = []

        mgr = ContextManager(conversation_repo=mock_repo)
        messages = [
            Message(
                content="hola",
                role=MessageRole.USER,
                conversation_id="test",
            ),
        ]
        _ctx, context_block = await mgr.build_context(messages)
        assert "Conversaciones anteriores" not in context_block

