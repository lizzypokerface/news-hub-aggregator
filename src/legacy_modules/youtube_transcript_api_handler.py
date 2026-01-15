# Legacy module: retained for compatibility and slated for migration or deprecation.

import requests
import time
import logging

logger = logging.getLogger(__name__)


class YoutubeTranscriptApiHandler:
    """
    Handles fetching and parsing YouTube transcript data from the API.
    Documentation: https://www.youtube-transcript.io/api
    """

    API_URL = "https://www.youtube-transcript.io/api/transcripts"

    def __init__(self, video_id, api_token=None, mock_data=None):
        """
        Initializes the handler.

        Args:
            video_id (str): The YouTube video ID.
            api_token (str, optional): The API key. Required if mock_data is None.
            mock_data (list, optional): Pre-fetched JSON data (useful for testing without making API calls).
        """
        self.video_id = video_id

        if mock_data:
            logger.info("Using mock data for video_id: %s", video_id)
            self.data = mock_data
        elif api_token:
            logger.info("Fetching data from API for video_id: %s", video_id)
            self.data = self._fetch_data(api_token)
        else:
            logger.error("No api_token or mock_data provided.")
            raise ValueError(
                "You must provide either an api_token to fetch data or mock_data for testing."
            )

    def _fetch_data(self, api_token):
        """Internal method to perform the API request, with rate limit handling."""
        headers = {
            "Authorization": f"Basic {api_token}",
            "Content-Type": "application/json",
        }
        payload = {"ids": [self.video_id]}

        try:
            logger.debug(
                "Sending POST request to %s with payload: %s", self.API_URL, payload
            )
            response = requests.post(self.API_URL, headers=headers, json=payload)
            logger.info("Received response with status code: %s", response.status_code)
            if response.status_code == 429:
                logger.warning("Rate limit exceeded for video_id: %s", self.video_id)
                raise RuntimeError(
                    "Rate limit exceeded: received HTTP 429 Too Many Requests. Please wait before retrying."
                )
            response.raise_for_status()  # Raise error for bad HTTP status (4xx, 5xx)
            logger.debug("API response JSON: %s", response.text)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Failed to connect to Transcript API: %s", e)
            raise ConnectionError(f"Failed to connect to Transcript API: {e}")
        finally:
            # Always wait 2 econds after each fetch to avoid exceeding the rate limit
            logger.debug("Sleeping for 2seconds to respect API rate limits.")
            time.sleep(2)

    # --- Helper Methods ---

    def _get_first_item(self):
        """Validates that data is a list and returns the first item."""
        if not isinstance(self.data, list) or not self.data:
            logger.error("The API response is empty or not a valid list.")
            raise ValueError("The API response is empty or not a valid list.")
        return self.data[0]

    # --- Public Getters ---

    def _get_microformat_renderer(self):
        """Helper to safely access nested microformat data."""
        item = self._get_first_item()

        if "microformat" not in item:
            logger.error("'microformat' key missing from response.")
            raise KeyError("'microformat' key missing from response.")

        # Note: The API usually nests it under playerMicroformatRenderer
        if "playerMicroformatRenderer" not in item["microformat"]:
            logger.error("'playerMicroformatRenderer' key missing from microformat.")
            raise KeyError("'playerMicroformatRenderer' key missing from microformat.")

        return item["microformat"]["playerMicroformatRenderer"]

    def get_video_id_from_response(self):
        """Verifies and returns the ID found in the response body."""
        item = self._get_first_item()
        if "id" not in item:
            logger.error("The key 'id' was not found in the API response.")
            raise KeyError("The key 'id' was not found in the API response.")
        logger.info("Extracted video id: %s", item["id"])
        return item["id"]

    def get_transcript_text(self):
        """Extracts the main transcript text."""
        item = self._get_first_item()
        if "text" not in item:
            logger.error("The key 'text' was not found in the API response.")
            raise KeyError("The key 'text' was not found in the API response.")
        logger.info("Extracted transcript text for video_id: %s", self.video_id)
        return item["text"]

    def get_video_title(self):
        """Extracts the video title."""
        item = self._get_first_item()
        if "title" not in item:
            logger.error("The key 'title' was not found in the API response.")
            raise KeyError("The key 'title' was not found in the API response.")
        logger.info("Extracted video title for video_id: %s", self.video_id)
        return item["title"]

    def get_video_description(self):
        """Extracts the video description."""
        renderer = self._get_microformat_renderer()

        if "description" not in renderer or "simpleText" not in renderer["description"]:
            logger.error("Description 'simpleText' not found in microformat.")
            raise KeyError("Description 'simpleText' not found in microformat.")

        logger.info("Extracted video description for video_id: %s", self.video_id)
        return renderer["description"]["simpleText"]

    def get_channel_name(self):
        """Extracts the channel owner name."""
        renderer = self._get_microformat_renderer()
        if "ownerChannelName" not in renderer:
            logger.error("'ownerChannelName' not found in microformat.")
            raise KeyError("'ownerChannelName' not found in microformat.")
        logger.info("Extracted channel name: %s", renderer["ownerChannelName"])
        return renderer["ownerChannelName"]

    def get_publish_date(self):
        """Extracts the publish date."""
        renderer = self._get_microformat_renderer()
        if "publishDate" not in renderer:
            logger.error("'publishDate' not found in microformat.")
            raise KeyError("'publishDate' not found in microformat.")
        logger.info("Extracted publish date: %s", renderer["publishDate"])
        return renderer["publishDate"]
