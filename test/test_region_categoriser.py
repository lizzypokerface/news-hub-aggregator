import pytest
from unittest.mock import patch
from modules.region_categoriser import RegionCategoriser

# --- Fixtures ---


@pytest.fixture
def mock_config():
    """Provides a minimal mock configuration."""
    return {
        "api_keys": {"poe_api": "mock_key"},
    }


@pytest.fixture
def mock_llm_client():
    """Mocks the LLMClient to avoid actual network calls."""
    with patch("modules.region_categoriser.LLMClient") as MockClient:
        client_instance = MockClient.return_value
        yield client_instance


@pytest.fixture
# This fixture is needed to ensure LLMClient is patched for all tests using categoriser.  # noqa: F841
def categoriser(mock_config, mock_llm_client):
    """Initializes the RegionCategorizer with mocked dependencies."""
    return RegionCategoriser(mock_config, model="qwen2.5:14b")


# --- Tests ---


def test_initialization(categoriser):
    """Test that the categorizer initializes correctly."""
    assert categoriser.model == "qwen2.5:14b"
    assert categoriser.llm_client is not None


def test_get_region_normalization_west_asia(categoriser, mock_llm_client):
    """
    Test that the alias 'West Asia' is correctly normalized to 'West Asia (Middle East)'.
    """
    # Simulate LLM returning the shorthand "West Asia"
    mock_llm_client.query.return_value = "West Asia"

    title = "Why Did Hamas & Israel Agree To A Ceasefire?"
    result = categoriser.get_region(title)

    assert result == "West Asia (Middle East)"


def test_get_region_normalization_case_insensitive(categoriser, mock_llm_client):
    """Test that normalization works even if LLM returns lowercase."""
    mock_llm_client.query.return_value = "united states"

    result = categoriser.get_region("Some US news")
    assert result == "North America"


def test_get_region_handles_unknown(categoriser, mock_llm_client):
    """Test fallback for truly unknown regions."""
    mock_llm_client.query.return_value = "Atlantis"
    result = categoriser.get_region("Some random text")
    assert result == "Unknown"
