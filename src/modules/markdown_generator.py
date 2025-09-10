import logging
import os
from datetime import datetime
import pandas as pd

# --- Module-level Constants for Post Structure ---

# This defines the strict order and the exact heading names for the output file.
REGION_HEADINGS = {
    "Global": "Global",
    "China": "China",
    "East Asia": "East Asia",
    "Singapore": "Singapore",
    "Southeast Asia": "Southeast Asia",
    "South Asia": "South Asia",
    "Central Asia": "Central Asia",
    "Russia": "Russia",
    "West Asia (Middle East)": "West Asia (Middle East)",  # Mapping data value to desired heading
    "Africa": "Africa",
    "Europe": "Europe",
    "Latin America & Caribbean": "Latin America & Caribbean",
    "North America": "North America",
    "Oceania": "Oceania",
    "Unknown": "Unknown",
}

# YAML Front Matter and basic structure for the Markdown post
NEWS_POST_TEMPLATE = """---
layout: post
title:  "✊ Progressive News | {date_display}"
date:   {date_str} 08:00:00 +0800
categories: weekly news
---
"""


class MarkdownGenerator:
    """
    Generates a Markdown news post from a DataFrame of categorized articles.
    """

    def __init__(
        self, input_df: pd.DataFrame, output_directory: str, current_date: datetime
    ):
        """
        Initializes the generator with data and configuration.

        Args:
            input_df (pd.DataFrame): The final DataFrame containing articles with regions.
            output_directory (str): The directory where the .md file will be saved.
            current_date (datetime): The date to use for the post's title and filename.
        """
        if not isinstance(input_df, pd.DataFrame):
            raise ValueError("A pandas DataFrame must be provided.")
        self.df = input_df
        self.output_directory = output_directory
        self.current_date = current_date

        date_str = self.current_date.strftime("%Y-%m-%d")
        self.output_filename = os.path.join(
            self.output_directory, f"{date_str}-weekly-news.md"
        )

    def _format_article_line(self, row: pd.Series) -> str:
        """Formats a single article row into the required Markdown string."""
        # Example: * [`The China Academy` How Does China’s System Really Work?](url)
        return f"* [`{row['source']}` {row['title']}]({row['url']})"

    def generate_markdown_post(self) -> None:
        """
        Sorts, groups, and formats the articles into a complete .md file,
        ensuring all region headers are present.
        """
        logging.info("Starting Markdown post generation...")

        # Prepare the initial part of the post from the template
        date_display = self.current_date.strftime("%d %B %Y")
        date_str = self.current_date.strftime("%Y-%m-%d")
        post_content = NEWS_POST_TEMPLATE.format(
            date_display=date_display, date_str=date_str
        )

        # Identify which regions are actually present in the DataFrame
        unique_regions_in_df = self.df["region"].unique().tolist()

        # Create a categorical type for regions to enforce the desired sorting order
        self.df["region"] = pd.Categorical(
            self.df["region"], categories=REGION_HEADINGS.keys(), ordered=True
        )

        # Sort the DataFrame according to the specified hierarchy
        sorted_df = self.df.sort_values(by=["region", "rank", "source"])
        logging.info("DataFrame sorted by region, rank, and source.")

        # Group by the ordered region category
        grouped_by_region = sorted_df.groupby("region", observed=False)

        # Build the content for each region, ensuring all headers are included.
        for region_name, heading in REGION_HEADINGS.items():
            # Step 1: ALWAYS add the region header with two newlines after it.
            post_content += f"\n# {heading}\n\n"

            print(post_content)

            # Step 2: CONDITIONALLY check if this region has articles to add.
            if region_name in unique_regions_in_df:
                print("should not run - east asia")
                # If articles exist, format and add them.
                region_df = grouped_by_region.get_group(region_name)
                article_lines = [
                    self._format_article_line(row) for _, row in region_df.iterrows()
                ]
                post_content += "\n".join(article_lines)
                post_content += "\n"  # Add a final newline to separate from the next section header.

        # Add the final empty sections as requested
        post_content += "\n# In-Depth Analysis\n\n"
        post_content += "# Special Features\n\n"

        # Write the final string to the output file
        try:
            os.makedirs(self.output_directory, exist_ok=True)
            with open(self.output_filename, "w", encoding="utf-8") as f:
                f.write(post_content)
            logging.info(
                f"Markdown post successfully generated at '{self.output_filename}'"
            )
        except OSError as e:
            logging.error(f"Failed to write Markdown file: {e}")
            raise
