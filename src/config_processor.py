import yaml
import re
import os


class ConfigProcessor:
    """
    A class to load, validate, and process a YAML configuration file.
    It checks for missing fields, empty values, correct types, URL formats,
    and cross-references summary preferences with defined sources.
    If no issues are found, it sorts the sources by rank.
    """

    def __init__(self, config_content: str):
        """
        Initializes the ConfigProcessor with the YAML configuration content.

        Args:
            config_content (str): The raw string content of the YAML configuration.
        """
        self.config = None
        self.issues = []
        try:
            self.config = yaml.safe_load(config_content)
            if not isinstance(self.config, dict):
                self._add_issue(
                    "Root", "Expected a dictionary at the root of the configuration."
                )
        except yaml.YAMLError as e:
            self.issues.append(f"YAML parsing error: {e}")
        except Exception as e:
            self.issues.append(
                f"An unexpected error occurred during config loading: {e}"
            )

    def _add_issue(self, location: str, message: str):
        """
        Adds an issue message to the list of detected issues.

        Args:
            location (str): The location in the config where the issue was found (e.g., "api_keys.youtube_api").
            message (str): A description of the issue.
        """
        self.issues.append(f"Issue at {location}: {message}")

    def validate_api_keys_and_directories(self):
        """
        Validates the 'api_keys', 'input_directory', and 'output_directory' sections.
        Checks for missing sections, correct types, and non-empty/non-placeholder values.
        """
        if not self.config:
            return

        # Validate api_keys
        api_keys = self.config.get("api_keys")
        if api_keys is None:
            self._add_issue("api_keys", "Missing 'api_keys' section.")
        elif not isinstance(api_keys, dict):
            self._add_issue("api_keys", "Expected 'api_keys' to be a dictionary.")
        else:
            for key in ["youtube_api", "poe_api"]:
                value = api_keys.get(key)
                if (
                    not isinstance(value, str)
                    or value.strip() == ""
                    or value.strip().lower() == "xxx"
                ):
                    self._add_issue(
                        f"api_keys.{key}", "API key cannot be empty, blank, or 'xxx'."
                    )

        # Validate input_directory and output_directory
        for key in ["input_directory", "output_directory"]:
            value = self.config.get(key)
            if not isinstance(value, str) or value.strip() == "":
                self._add_issue(key, "Directory path cannot be empty or blank.")

    def validate_sources(self):
        """
        Validates the 'sources' list.
        Checks for missing fields, empty values, correct 'type' and 'format' enums,
        and validates URL formats based on the 'format' type.
        """
        if not self.config:
            return

        sources = self.config.get("sources")
        if sources is None:
            self._add_issue("sources", "Missing 'sources' section.")
            return
        elif not isinstance(sources, list):
            self._add_issue("sources", "Expected 'sources' to be a list.")
            return

        for i, source in enumerate(sources):
            if not isinstance(source, dict):
                self._add_issue(
                    f"sources[{i}]", "Expected a dictionary for each source entry."
                )
                continue

            required_fields = ["name", "url", "type", "format", "rank"]
            for field in required_fields:
                if field not in source:
                    self._add_issue(
                        f"sources[{i}].{field}", f"Missing required field '{field}'."
                    )
                elif not isinstance(source[field], (str, int)):
                    self._add_issue(
                        f"sources[{i}].{field}",
                        f"Field '{field}' has an invalid type. Expected string or integer.",
                    )
                elif isinstance(source[field], str) and source[field].strip() == "":
                    self._add_issue(
                        f"sources[{i}].{field}",
                        f"Field '{field}' cannot be empty or blank.",
                    )

            # Validate 'type' field
            source_type = source.get("type")
            if source_type is not None and source_type not in ["analysis", "datapoint"]:
                self._add_issue(
                    f"sources[{i}].type",
                    f"Invalid type '{source_type}'. Must be 'analysis' or 'datapoint'.",
                )

            # Validate 'format' field
            source_format = source.get("format")
            if source_format is not None and source_format not in [
                "youtube",
                "webpage",
            ]:
                self._add_issue(
                    f"sources[{i}].format",
                    f"Invalid format '{source_format}'. Must be 'youtube' or 'webpage'.",
                )

            # Validate 'url' based on 'format'
            source_url = source.get("url")
            if source_url is not None:
                if not isinstance(source_url, str):
                    self._add_issue(f"sources[{i}].url", "URL must be a string.")
                elif source_url.strip() == "":
                    self._add_issue(
                        f"sources[{i}].url", "URL cannot be empty or blank."
                    )
                elif source_format == "webpage":
                    if not (
                        source_url.startswith("http://")
                        or source_url.startswith("https://")
                    ):
                        self._add_issue(
                            f"sources[{i}].url",
                            f"Webpage URL '{source_url}' must start with 'http://' or 'https://'.",
                        )
                elif source_format == "youtube":
                    # Regex for YouTube channel videos page: https://www.youtube.com/@<handle>/videos
                    youtube_url_pattern = r"^https://www\.youtube\.com/@[^/]+/videos$"
                    if not re.match(youtube_url_pattern, source_url):
                        self._add_issue(
                            f"sources[{i}].url",
                            f"YouTube URL '{source_url}' does not match the required format 'https://www.youtube.com/@<handle>/videos'.",
                        )
            else:
                self._add_issue(f"sources[{i}].url", "Missing URL field.")

            # Validate 'rank' field
            source_rank = source.get("rank")
            if source_rank is not None:
                if not isinstance(source_rank, int) or source_rank <= 0:
                    self._add_issue(
                        f"sources[{i}].rank",
                        f"Rank '{source_rank}' must be a positive integer.",
                    )
            else:
                self._add_issue(f"sources[{i}].rank", "Missing rank field.")

    def validate_summarise_preference(self):
        """
        Validates the 'summarise' list.
        Checks if it's a list of strings and if each string corresponds to an existing source name.
        """
        if not self.config:
            return

        summarise_list = self.config.get("summarise")
        if summarise_list is None:
            # The 'summarise' section is optional, so if it's missing, it's not an issue.
            return

        if not isinstance(summarise_list, list):
            self._add_issue(
                "summarise", "Expected 'summarise' to be a list of source names."
            )
            return

        # Collect all valid source names from the 'sources' list for cross-referencing
        valid_source_names = set()
        sources = self.config.get("sources", [])
        for source in sources:
            if (
                isinstance(source, dict)
                and "name" in source
                and isinstance(source["name"], str)
            ):
                valid_source_names.add(source["name"])

        for i, summary_name in enumerate(summarise_list):
            if not isinstance(summary_name, str) or summary_name.strip() == "":
                self._add_issue(
                    f"summarise[{i}]",
                    "Summary preference name cannot be empty or blank.",
                )
            elif summary_name not in valid_source_names:
                self._add_issue(
                    f"summarise[{i}]",
                    f"'{summary_name}' in summarise list does not correspond to an existing source name in 'sources'.",
                )

    def validate_all(self) -> bool:
        """
        Runs all validation checks on the loaded configuration.

        Returns:
            bool: True if no issues were detected, False otherwise.
        """
        # Clear previous issues before running new checks
        self.issues = []

        if self.config is None:  # YAML parsing already failed
            return False

        self.validate_api_keys_and_directories()
        self.validate_sources()
        self.validate_summarise_preference()

        return len(self.issues) == 0

    def get_issues(self) -> list:
        """
        Returns a list of detected issues.

        Returns:
            list: A list of strings, where each string describes an issue.
        """
        return self.issues

    def sort_sources_by_rank(self) -> bool:
        """
        Sorts the 'sources' list by 'rank' in ascending order.
        This operation is performed only if no issues were detected during validation.

        Returns:
            bool: True if sorting was successful, False otherwise (e.g., issues present, no sources).
        """
        if (
            not self.issues
            and self.config
            and "sources" in self.config
            and isinstance(self.config["sources"], list)
        ):
            try:
                # Ensure all sources have a valid 'rank' before attempting to sort.
                # This check is implicitly covered if `validate_all` passed without issues.
                if all(
                    isinstance(s, dict) and "rank" in s and isinstance(s["rank"], int)
                    for s in self.config["sources"]
                ):
                    self.config["sources"].sort(key=lambda x: x["rank"])
                    return True
                else:
                    # This case should ideally not be hit if validate_all passed
                    self._add_issue(
                        "sources",
                        "Cannot sort: some sources do not have a valid 'rank' field (this indicates a prior validation miss).",
                    )
                    return False
            except Exception as e:
                self._add_issue(
                    "sources",
                    f"An unexpected error occurred during sorting sources: {e}",
                )
                return False
        return (
            False  # No sources to sort, or issues present, or 'sources' is not a list
        )

    def get_processed_config(self):
        """
        Returns the processed (and potentially sorted) configuration dictionary.

        Returns:
            dict: The configuration dictionary.
        """
        return self.config


# --- Main block to run the ConfigProcessor ---
if __name__ == "__main__":
    # Determine the path to config.yaml relative to the current script
    # This makes the script runnable from any directory as long as config.yaml
    # is in the parent directory of the script's directory.
    script_dir = os.path.dirname(__file__)
    config_file_path = os.path.abspath(os.path.join(script_dir, "..", "config.yaml"))

    config_content = None
    try:
        with open(config_file_path, encoding="utf-8") as f:
            config_content = f.read()
        print(f"Successfully read config file from: {config_file_path}")
    except FileNotFoundError:
        print(f"Error: config.yaml not found at {config_file_path}")
        exit(1)  # Exit if the config file cannot be found
    except Exception as e:
        print(f"Error reading config file {config_file_path}: {e}")
        exit(1)  # Exit on other file reading errors

    if config_content:
        processor = ConfigProcessor(config_content)

        # Validate the configuration
        if processor.validate_all():
            print("\nNo issues detected in the configuration file.")

            # If no issues, attempt to sort the sources
            if processor.sort_sources_by_rank():
                print("\nSources sorted by rank:")
                # Print the sorted configuration in YAML format
                # sort_keys=False is used to preserve the order of other fields within dictionaries
                print(
                    yaml.dump(
                        processor.get_processed_config(), indent=2, sort_keys=False
                    )
                )
            else:
                # This block would typically indicate an unexpected error during sorting
                # or that sorting was skipped due to an issue that wasn't caught by validate_all.
                print("\nCould not sort sources. Please check the issues reported.")
                for issue in processor.get_issues():
                    print(f"- {issue}")
        else:
            print("\nIssues detected in the configuration file:")
            for issue in processor.get_issues():
                print(f"- {issue}")
