"""
Tests for the Input Processor module.
"""

import pytest
from autoops_aws.input_processor import InputProcessor

@pytest.fixture
def input_processor():
    """Create an InputProcessor instance for testing."""
    return InputProcessor()

def test_input_processor_initialization(input_processor):
    """Test that InputProcessor initializes correctly."""
    assert isinstance(input_processor, InputProcessor)
    assert hasattr(input_processor, "supported_commands")
    assert isinstance(input_processor.supported_commands, set)

@pytest.mark.asyncio
async def test_process_input_not_implemented(input_processor):
    """Test that process_input raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        await input_processor.process_input("test command") 