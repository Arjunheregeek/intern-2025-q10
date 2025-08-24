import pytest
from src.services.memory_manager import ConversationMemoryManager, MemoryManager


@pytest.fixture
def conversation_memory_manager():
    return ConversationMemoryManager(window_size=4)


@pytest.fixture
def memory_manager():
    return MemoryManager(threshold_mb=100.0)


def test_add_and_retrieve_messages(conversation_memory_manager):
    conversation_memory_manager.add_user_message("Hello")
    conversation_memory_manager.add_ai_message("Hi, how can I help you?")
    history = conversation_memory_manager.get_conversation_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_clear_memory(conversation_memory_manager):
    conversation_memory_manager.add_user_message("Hello")
    conversation_memory_manager.clear_memory()
    history = conversation_memory_manager.get_conversation_history()
    assert len(history) == 0


def test_memory_status(conversation_memory_manager):
    conversation_memory_manager.add_user_message("Hello")
    status = conversation_memory_manager.get_memory_status()
    assert status["total_messages"] == 1


def test_memory_usage(memory_manager):
    stats = memory_manager.get_memory_usage()
    assert "current_mb" in stats
    assert "peak_mb" in stats


def test_memory_optimization(memory_manager):
    optimized = memory_manager.check_and_optimize()
    assert not optimized  # No optimization needed initially
