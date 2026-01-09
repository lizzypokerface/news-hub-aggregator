import os
import sys
import logging
import argparse
from datetime import datetime


from legacy_modules.config_manager import ConfigManager
from legacy_modules.llm_client import LLMClient
from orchestrators.WeeklyIntelOrchestrator import WeeklyIntelOrchestrator


def setup_logging(level=logging.INFO):
    """Configures the root logger with a standard format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    # 1. Argument Parsing
    parser = argparse.ArgumentParser(
        description="Weekly Intelligence Manufacturing Plant"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="./config.yaml",
        help="Path to the configuration YAML file.",
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Force a specific run date (Format: YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")

    args = parser.parse_args()

    # 2. Setup Logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    logger.info("Initializing Weekly Intelligence Pipeline...")

    try:
        # 3. Handle Date
        run_date = datetime.now()
        if args.date:
            try:
                run_date = datetime.strptime(args.date, "%Y-%m-%d")
                logger.info(
                    f"Manual override: Running for date {run_date.strftime('%Y-%m-%d')}"
                )
            except ValueError:
                logger.error("Invalid date format. Please use YYYY-MM-DD.")
                sys.exit(1)

        # 4. Load Configuration
        if not os.path.exists(args.config):
            logger.error(f"Config file not found: {args.config}")
            sys.exit(1)

        config_manager = ConfigManager(args.config)
        config = config_manager.data
        logger.info(f"Configuration loaded from {args.config}")

        # 5. Initialize Services
        llm_client = LLMClient(config)

        # 6. Initialize Orchestrator
        orchestrator = WeeklyIntelOrchestrator(
            config=config, llm_client=llm_client, run_date=run_date
        )

        # 7. Execute Pipeline
        logger.info(">>> STARTING ORCHESTRATOR <<<")
        orchestrator.run()
        logger.info(">>> ORCHESTRATOR FINISHED <<<")

    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error in main loop: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
