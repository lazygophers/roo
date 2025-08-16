"""
This script serves as the main entry point for the application.

It handles command-line argument parsing, sets up logging,
and will eventually start the server.
"""

import argparse
import logging

from src.logger import setup_logger
from src.server import run_server


def main(argv: list[str] | None = None) -> None:
    """
    The main function of the application.

    It parses command-line arguments, configures the logger,
    and logs initial messages.

    Args:
        argv: Optional list of arguments to parse. If None, uses sys.argv.
    """
    parser = argparse.ArgumentParser(description="Application Main Entry Point")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for detailed logging.",
    )
    args = parser.parse_args(argv)

    setup_logger(args.debug)

    logging.info("Application starting.")
    logging.debug("Logger configured for debug mode.")

    try:
        run_server()
    except KeyboardInterrupt:
        logging.info("Server stopped by user.")
    except Exception:
        logging.exception("An unexpected error occurred during server execution.")
    finally:
        logging.info("Application shutting down.")


if __name__ == "__main__":
    main()
