import logging
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

from dateutil import parser as date_parser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from interfaces import BaseConsolidator
from interfaces.models import MainstreamSourceEntry, MainstreamHeadlines
from modules.content_extractor import ContentExtractor

logger = logging.getLogger(__name__)


class MainstreamHeadlineConsolidator(BaseConsolidator):
    """
    Consolidates mainstream news from sources defined in config.yaml where type='datapoint'.
    - YouTube: Uses API to fetch recent video titles.
    - Webpage: Uses ContentExtractor to scrape text.
    """

    def __init__(self, config: Dict):
        self.config = config
        self.api_key = self.config.get("api_keys", {}).get("youtube_api")

        # Initialize ContentExtractor
        self.content_extractor = ContentExtractor(self.config)

        # Initialize YouTube Service
        self.youtube_service = None
        if self.api_key:
            try:
                logger.debug("Initializing YouTube service with provided API key.")
                self.youtube_service = build("youtube", "v3", developerKey=self.api_key)
                logger.info("YouTube service initialized successfully.")
            except Exception as e:
                logger.error(
                    f"Failed to initialize YouTube service: {e}", exc_info=True
                )
        else:
            logger.warning("No YouTube API key found. YouTube sources will be skipped.")

    def consolidate(self) -> MainstreamHeadlines:
        """
        Iterates through sources, fetching content based on type.
        Returns a list containing a single MainstreamHeadlines object (to match BaseConsolidator interface).
        """
        sources = self.config.get("sources", [])
        logger.info(f"Loaded {len(sources)} sources from config.")
        # Filter for 'datapoint' type sources
        datapoint_sources = [s for s in sources if s.get("type") == "datapoint"]

        if not datapoint_sources:
            logger.warning("No sources with type='datapoint' found in config.")
            return []

        consolidated_entries: List[MainstreamSourceEntry] = []

        for source in datapoint_sources:
            name = source.get("name")
            url = source.get("url")
            fmt = source.get("format")  # 'youtube' or 'webpage'

            if not name or not url:
                logger.warning(f"Skipping source with missing name or url: {source}")
                continue

            logger.info(
                f"Processing Mainstream source: {name} (format: {fmt}, url: {url})"
            )

            content_data: List[str] = []

            # Strategy Pattern based on format
            if fmt == "youtube":
                logger.info(f"Fetching YouTube titles for channel: {name} ({url})")
                content_data = self._fetch_youtube_titles(name, url)
            elif fmt == "webpage":
                logger.info(f"Extracting webpage content from: {url}")
                text = self._fetch_webpage_content(url)
                if text:
                    content_data = [text]  # Wrap single text in list
                    logger.info(
                        f"Webpage content extracted for {name} (length: {len(text)})"
                    )
                else:
                    logger.warning(f"No content extracted from webpage: {url}")
            else:
                logger.warning(f"Unknown format '{fmt}' for source '{name}'. Skipping.")

            if content_data:
                logger.info(f"Adding {len(content_data)} entries for source: {name}")
                entry = MainstreamSourceEntry(
                    source_name=name, content=content_data, source_type=fmt
                )
                consolidated_entries.append(entry)
            else:
                logger.warning(f"No content data found for source: {name}")

        logger.info(
            f"Consolidation complete. Total entries: {len(consolidated_entries)}"
        )
        # Return the single object directly (NO LIST WRAPPER)
        return MainstreamHeadlines(entries=consolidated_entries)

    def _fetch_webpage_content(self, url: str) -> Optional[str]:
        """Delegates to the existing ContentExtractor class."""
        try:
            logger.info(f"Attempting to extract text from webpage: {url}")
            text = self.content_extractor.get_text(url)
            logger.info(
                f"Successfully extracted text from {url} (length: {len(text) if text else 0})"
            )
            return text
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}", exc_info=True)
            return None

    def _fetch_youtube_titles(self, channel_name: str, channel_url: str) -> List[str]:
        """
        Fetches video titles published in the last 7 days.
        """
        if not self.youtube_service:
            logger.warning(
                f"YouTube service not initialized. Skipping channel: {channel_name}"
            )
            return []

        handle_match = re.search(r"youtube\.com/(@[A-Za-z0-9_.-]+)", channel_url)
        if not handle_match:
            logger.error(f"Could not extract handle from URL: {channel_url}")
            return []
        handle = handle_match.group(1)
        logger.info(f"Extracted YouTube handle '{handle}' from URL: {channel_url}")

        try:
            # 1. Get Channel ID
            logger.info(f"Searching for channel ID using handle: {handle}")
            search_res = (
                self.youtube_service.search()
                .list(q=handle, part="id", type="channel", maxResults=1)
                .execute()
            )

            if not search_res.get("items"):
                logger.error(f"Channel ID not found for handle '{handle}'")
                return []

            channel_id = search_res["items"][0]["id"]["channelId"]
            logger.info(f"Found channel ID '{channel_id}' for handle '{handle}'")

            # 2. Get Uploads Playlist ID
            logger.info(f"Fetching uploads playlist ID for channel ID: {channel_id}")
            channel_res = (
                self.youtube_service.channels()
                .list(id=channel_id, part="contentDetails")
                .execute()
            )

            uploads_id = channel_res["items"][0]["contentDetails"]["relatedPlaylists"][
                "uploads"
            ]
            logger.info(
                f"Uploads playlist ID for channel '{channel_name}': {uploads_id}"
            )

            # 3. Fetch Videos (Last 7 Days)
            one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            logger.info(
                f"Fetching videos from uploads playlist '{uploads_id}' published after {one_week_ago.isoformat()}"
            )
            playlist_res = (
                self.youtube_service.playlistItems()
                .list(playlistId=uploads_id, part="snippet", maxResults=60)
                .execute()
            )

            titles = []
            for item in playlist_res.get("items", []):
                snippet = item["snippet"]
                published = date_parser.isoparse(snippet["publishedAt"])

                if published >= one_week_ago:
                    titles.append(snippet["title"])
                    logger.info(
                        f"Added video '{snippet['title']}' published at {published}"
                    )

            logger.info(f"Fetched {len(titles)} titles from {channel_name}")
            return titles

        except HttpError as e:
            logger.error(f"YouTube API Error for {channel_name}: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error for {channel_name}: {e}", exc_info=True)
            return []
