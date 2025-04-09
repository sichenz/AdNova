"""
Entry point for the Marketing Ad Agent application.
This script initializes and runs the application in either CLI or web mode.
"""
import argparse
import sys
import os

# Ensure paths are correctly set
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION, DEBUG_MODE
from core.agent import MarketingAdAgent
from ui.cli import run_cli
from ui.web_app import run_web_app

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=f"{APP_NAME} v{APP_VERSION}")
    parser.add_argument(
        "--mode", 
        choices=["cli", "web"], 
        default="web",
        help="Application mode: command-line interface or web application"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        default=DEBUG_MODE,
        help="Enable debug mode"
    )
    return parser.parse_args()

def main():
    """Main function to run the application."""
    args = parse_arguments()
    
    # Create the marketing ad agent
    agent = MarketingAdAgent(debug_mode=args.debug)
    
    try:
        if args.mode == "cli":
            print(f"Starting {APP_NAME} v{APP_VERSION} in CLI mode")
            run_cli(agent)
        else:
            print(f"Starting {APP_NAME} v{APP_VERSION} in web mode")
            run_web_app(agent)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        if args.debug:
            raise e
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()