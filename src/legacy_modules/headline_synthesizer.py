# Legacy module: retained for compatibility and slated for migration or deprecation.

import logging
import re
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict

from dateutil import parser as date_parser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# --- Future Work ---

# TODO: synthesize webpage articles

# --- Future Work ---

# --- Basic Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- LLM Prompt Template  ---
PROMPT_TEMPLATE = PromptTemplate.from_template(
    """
You are an expert information synthesizer. Your primary function is to analyze a list of headlines or video titles and distill them into a dense, compact summary of the distinct, ongoing events they describe.
Follow this exact methodology:
1.  **Scan and Group:** First, scan the entire list of titles to identify and group those covering the same core event. For example, group all titles about an election in one country or a natural disaster in a specific region. This prevents redundancy.
2.  **Synthesize Core Information:** For each group of related titles, extract the essential information: the main subject (who/what) and the primary action (the event itself). Merge details from multiple titles into a single concept (e.g., flooding in two different provinces becomes "flooding in Punjab and KP provinces").
3.  **Draft a Comprehensive Sentence:** Write a single, clear sentence that summarizes the entire event for each group.
4.  **Refine for Conciseness:** Aggressively edit each sentence down to a strict **10-15 word limit**. Achieve this by removing filler words (e.g., 'a', 'the', 'in'), using stronger verbs, and rephrasing for maximum information density.
Output Constraints:
- The final output must be a single, compact text block.
- All the refined sentences must be joined together by commas.
- Do not use bullet points, numbering, line breaks, or any introductory text in the final output.
---
**EXAMPLE 1: Grouping Related Titles**
*   **If Titles Are:** "Pakistan flooding: Nearly 4 million people affected by punjab flooding" and "Pakistan flooding: Thousands impacted in Khyber Pakhtunkhwa province"
*   **Your Thought Process:** Both are about Pakistan flooding. Group them. Synthesize the locations: Punjab and Khyber Pakhtunkhwa (KP). Draft and refine.
*   **Resulting Sentence:** `Pakistan flooding affects nearly four million in Punjab and KP provinces.`

**EXAMPLE 2: Synthesizing Different Actions for One Event**
*   **If Titles Are:** "US top diplomat in Latin America: Washington mulls military base in Ecuador" and "Rubio in Ecuador: Washington pledges $20m in security aid"
*   **Your Thought Process:** Both are about US-Ecuador relations. Group them. Synthesize the actions: pledging aid and mulling a base. Draft and refine.
*   **Resulting Sentence:** `The US pledged $20m in security aid to Ecuador, mulling a military base.`

**EXAMPLE 3: Handling Multiple Distinct Events (IDEAL OUTPUT FORMAT)**
*   **If Titles Are:**
    - "China delivers humanitarian aid shipment to Afghanistan"
    - "New documentary on Nanjing Massacre released this week"
    - "Stunning 'Blood Moon' lunar eclipse seen by millions"
    - "Photos of the lunar eclipse from around the world"
    - "Israel launches new airstrikes on Gaza as tensions escalate"
    - "French government debates significant budget cuts for next year"
    - "Hungary's Orban criticizes EU's Ukraine strategy"
    - "Taiwan begins annual live-fire military exercises"
*   **Your Thought Process:** Multiple distinct events identified. Each must be synthesized into a concise phrase. Grouping is not needed as events are separate. All refined phrases must be joined by commas into a single block.
*   **Resulting Summary:** `China sends aid to Afghanistan, a film on the Nanjing massacre premieres, a lunar eclipse is observed globally, the Israel-Gaza conflict escalates, France discusses budget cuts, Hungary's Orban comments on the EU and Ukraine, and Taiwan holds military drills.`
---
**YOUR TASK:**
CHANNEL NAME: {channel_name}
VIDEO TITLES FROM THE PAST WEEK:
{title_list}
COMPACT EVENT SUMMARY:
"""
)


class HeadlineSynthesizer:
    """
    Fetches and synthesizes YouTube headlines to summarize world events.
    """

    def __init__(self, api_key: str, model: str = "qwen2.5:32b"):
        """
        Initializes the synthesizer with API connections.

        Args:
            api_key (str): Your YouTube Data API v3 key.
            model (str): The Ollama model to use for synthesis.
        """
        try:
            self.youtube_service = build("youtube", "v3", developerKey=api_key)
            logging.info("YouTube API service initialized successfully.")
        except Exception as e:
            logging.error(
                f"Failed to initialize YouTube service. Check API key. Error: {e}"
            )
            raise

        try:
            llm = Ollama(model=model, temperature=0.0)
            self.llm_chain = PROMPT_TEMPLATE | llm | StrOutputParser()
            logging.info(f"Ollama chain initialized successfully with model '{model}'.")
        except Exception as e:
            logging.error(
                f"Failed to initialize Ollama. Is the service running? Error: {e}"
            )
            raise

    def _fetch_headlines_youtube(
        self, channel_name: str, channel_url: str
    ) -> List[str]:
        """
        Fetches video titles from a YouTube channel published in the last 7 days.
        Verifies that the fetched channel name matches the expected name.

        Args:
            channel_name (str): The expected name of the channel.
            channel_url (str): The URL of the channel (e.g., with /@handle).

        Returns:
            A list of video titles, or an empty list if an error occurs.
        """
        logging.info(f"Fetching headlines for '{channel_name}'...")

        handle_match = re.search(r"youtube\.com/(@[A-Za-z0-9_.-]+)", channel_url)
        if not handle_match:
            logging.error(f"Could not extract a valid @handle from URL: {channel_url}")
            return []

        handle = handle_match.group(1)

        try:
            search_req = self.youtube_service.search().list(
                q=handle, part="id", type="channel", maxResults=1
            )
            search_res = search_req.execute()
            if not search_res.get("items"):
                logging.error(f"Could not find channelId for handle '{handle}'.")
                return []
            channel_id = search_res["items"][0]["id"]["channelId"]

            # Get uploads playlist ID and verify channel name by requesting 'snippet'
            channel_req = self.youtube_service.channels().list(
                id=channel_id, part="contentDetails,snippet"
            )
            channel_res = channel_req.execute()

            # --- Channel Name Verification ---
            fetched_channel_name = channel_res["items"][0]["snippet"]["title"]
            logging.info(
                f"Verifying channel name. Expected: '{channel_name}', Fetched from API: '{fetched_channel_name}'"
            )
            if channel_name.lower() not in fetched_channel_name.lower():
                logging.warning(
                    f"Potential channel name mismatch. The name '{channel_name}' was not found in the fetched name '{fetched_channel_name}'."
                )

            uploads_id = channel_res["items"][0]["contentDetails"]["relatedPlaylists"][
                "uploads"
            ]

            one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            playlist_req = self.youtube_service.playlistItems().list(
                playlistId=uploads_id, part="snippet", maxResults=60
            )
            playlist_res = playlist_req.execute()

            titles = []
            for item in playlist_res.get("items", []):
                snippet = item["snippet"]
                published_date = date_parser.isoparse(snippet["publishedAt"])
                if published_date >= one_week_ago:
                    titles.append(snippet["title"])

            titles.reverse()
            logging.info(f"Found {len(titles)} recent headlines for '{channel_name}'.")
            return titles

        except HttpError as e:
            logging.error(f"An HTTP error occurred for '{channel_name}': {e}")
            return []
        except Exception as e:
            logging.error(f"An unexpected error occurred for '{channel_name}': {e}")
            return []

    def _synthesize_headlines_llm(self, channel_name: str, headlines: List[str]) -> str:
        """
        Uses an Ollama model to synthesize a list of headlines into a summary.
        Logs the time taken for the synthesis.

        Args:
            channel_name (str): The name of the source channel.
            headlines (List[str]): A list of video titles.

        Returns:
            A compact summary string.
        """
        if not headlines:
            return "No recent headlines were available to synthesize."

        logging.info(f"Synthesizing {len(headlines)} headlines for '{channel_name}'...")
        formatted_titles = "\n".join(f"- {title}" for title in headlines)

        try:
            # --- Time the LLM call ---
            start_time = time.monotonic()
            summary = self.llm_chain.invoke(
                {"channel_name": channel_name, "title_list": formatted_titles}
            )
            end_time = time.monotonic()
            duration = end_time - start_time

            logging.info(f"Synthesis successful. Time taken: {duration:.2f} seconds.")
            return summary.strip()
        except Exception as e:
            logging.error(f"Event synthesis failed. Could not connect to Ollama: {e}")
            return "Error: Event synthesis failed due to an LLM communication error."

    def synthesize_channel_activity(self, channel: Dict[str, str]) -> str:
        """
        Orchestrates the fetching and synthesis process for a single channel.

        Args:
            channel (Dict[str, str]): A dictionary with 'name' and 'url'.

        Returns:
            The final synthesized summary string.
        """
        # Unpack the dictionary to call the updated fetch method
        # NOTE (HOTFIX): We currently do NOT summarize the headlines, just return the raw YouTube API results.
        headlines = self._fetch_headlines_youtube(channel["name"], channel["url"])
        # summary = self._synthesize_headlines_llm(channel["name"], headlines)
        return headlines
