import pytest

from src.legacy_modules.youtube_transcript_api_handler import (
    YoutubeTranscriptApiHandler,
)

# --- Fixtures (Mock Data) ---


@pytest.fixture
def mock_valid_response():
    """Returns a valid JSON response structure matching the API."""
    return [
        {
            "text": "Hello everyone, welcome back...",
            "id": "rrqgBxw3fic",
            "title": "BRICS Is Taking Over AI — And the West Is Panicking",
            "microformat": {
                "playerMicroformatRenderer": {
                    "description": {"simpleText": "🔹 Subscribe to Lena's Substack..."},
                    "ownerChannelName": "World Affairs In Context",
                    "publishDate": "2025-12-29",
                }
            },
        }
    ]


@pytest.fixture
def mock_missing_keys_response():
    """Returns a malformed response missing critical keys."""
    return [
        {
            "text": "Just some text",
            # Missing 'title', 'id', 'microformat'
        }
    ]


# --- Tests ---


def test_initialization_success(mock_valid_response):
    """Test that the class initializes correctly with mock data."""
    handler = YoutubeTranscriptApiHandler("rrqgBxw3fic", mock_data=mock_valid_response)
    assert handler.video_id == "rrqgBxw3fic"


def test_initialization_failure():
    """Test that it raises ValueError if no token OR mock data is provided."""
    with pytest.raises(ValueError, match="You must provide either an api_token"):
        YoutubeTranscriptApiHandler("rrqgBxw3fic")


def test_get_video_id(mock_valid_response):
    handler = YoutubeTranscriptApiHandler("rrqgBxw3fic", mock_data=mock_valid_response)
    assert handler.get_video_id_from_response() == "rrqgBxw3fic"


def test_get_transcript_text(mock_valid_response):
    handler = YoutubeTranscriptApiHandler("rrqgBxw3fic", mock_data=mock_valid_response)
    text = handler.get_transcript_text()
    assert text.startswith("Hello everyone")


def test_get_video_details(mock_valid_response):
    """Test title, description, channel, and date extraction."""
    handler = YoutubeTranscriptApiHandler("rrqgBxw3fic", mock_data=mock_valid_response)

    assert (
        handler.get_video_title()
        == "BRICS Is Taking Over AI — And the West Is Panicking"
    )
    assert "Subscribe" in handler.get_video_description()
    assert handler.get_channel_name() == "World Affairs In Context"
    assert handler.get_publish_date() == "2025-12-29"


def test_missing_keys_raises_error(mock_missing_keys_response):
    """Test that strict error handling works when keys are missing."""
    handler = YoutubeTranscriptApiHandler(
        "rrqgBxw3fic", mock_data=mock_missing_keys_response
    )

    # Try to access a key that doesn't exist in the bad mock data
    with pytest.raises(KeyError, match="'title' was not found"):
        handler.get_video_title()

    with pytest.raises(KeyError, match="'microformat' key missing"):
        handler.get_channel_name()
