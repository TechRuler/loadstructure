import argparse
import os
import sys
# Assuming loadstructure.main.ConfigManager is available
from loadstructure.main import ConfigManager


def convert_config(src, dst):
    if not os.path.exists(src):
        print(f"❌ Source file not found: {src}")
        sys.exit(1)

    try:
        config = ConfigManager(src)
        config.load()
        config.save(dst)

        print(f"✅ Converted successfully: {src} → {dst}")

    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="loadstructure",
        description="Powerful configuration loader CLI"
    )

    sub = parser.add_subparsers(dest="command")

    # convert command
    convert_parser = sub.add_parser(
        "convert", 
        help="Convert config format (Usage: loadstructure convert <source> <destination>)"
    )
    
    # --- CHANGED: Removed 'arrow' argument and simplified positional arguments ---
    convert_parser.add_argument("source", help="Path to the source configuration file (e.g., config.json)")
    convert_parser.add_argument("destination", help="Path for the destination configuration file (e.g., config.yaml)")
    # ----------------------------------------------------------------------------

    args = parser.parse_args()

    if args.command == "convert":
        # The redundant check for 'args.arrow != "->"' is removed, 
        # as the 'arrow' argument no longer exists.
        
        convert_config(args.source, args.destination)

    else:
        # Prints general help if no command is specified
        parser.print_help()


if __name__ == "__main__":
    main()