"""Command-line interface for UN Docs Downloader."""

import argparse
import sys
from pathlib import Path

from .pipeline import sync_all_patterns
from .static_generator import generate_site


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="un-docs",
        description="UN Document System downloader and analyzer",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Discover command
    discover_parser = subparsers.add_parser(
        "discover",
        help="Discover and download new documents",
    )
    discover_parser.add_argument(
        "--config",
        type=Path,
        default=Path("./config"),
        help="Path to config directory (default: ./config)",
    )
    discover_parser.add_argument(
        "--data",
        type=Path,
        default=Path("./data"),
        help="Path to data directory (default: ./data)",
    )
    discover_parser.add_argument(
        "--max-misses",
        type=int,
        default=3,
        help="Stop after N consecutive 404s (default: 3)",
    )

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate static site from downloaded documents",
    )
    generate_parser.add_argument(
        "--config",
        type=Path,
        default=Path("./config"),
        help="Path to config directory (default: ./config)",
    )
    generate_parser.add_argument(
        "--data",
        type=Path,
        default=Path("./data"),
        help="Path to data directory (default: ./data)",
    )
    generate_parser.add_argument(
        "--output",
        type=Path,
        default=Path("./docs"),
        help="Path to output directory (default: ./docs)",
    )

    # Build command (discover + generate)
    build_parser = subparsers.add_parser(
        "build",
        help="Discover new documents and generate static site",
    )
    build_parser.add_argument(
        "--config",
        type=Path,
        default=Path("./config"),
        help="Path to config directory (default: ./config)",
    )
    build_parser.add_argument(
        "--data",
        type=Path,
        default=Path("./data"),
        help="Path to data directory (default: ./data)",
    )
    build_parser.add_argument(
        "--output",
        type=Path,
        default=Path("./docs"),
        help="Path to output directory (default: ./docs)",
    )
    build_parser.add_argument(
        "--max-misses",
        type=int,
        default=3,
        help="Stop after N consecutive 404s (default: 3)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "discover":
        cmd_discover(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "build":
        cmd_build(args)


def cmd_discover(args):
    """Run the discover command."""
    print(f"Discovering documents...")
    print(f"  Config: {args.config}")
    print(f"  Data: {args.data}")
    print(f"  Max consecutive misses: {args.max_misses}")
    print()

    results = sync_all_patterns(
        config_dir=args.config,
        data_dir=args.data,
        max_consecutive_misses=args.max_misses,
    )

    total_new = 0
    for pattern_name, new_docs in results.items():
        if new_docs:
            print(f"  {pattern_name}: {len(new_docs)} new documents")
            for doc in new_docs:
                print(f"    - {doc}")
            total_new += len(new_docs)
        else:
            print(f"  {pattern_name}: no new documents")

    print()
    print(f"Total: {total_new} new documents downloaded")


def cmd_generate(args):
    """Run the generate command."""
    print(f"Generating static site...")
    print(f"  Config: {args.config}")
    print(f"  Data: {args.data}")
    print(f"  Output: {args.output}")
    print()

    generate_site(
        config_dir=args.config,
        data_dir=args.data,
        output_dir=args.output,
    )


def cmd_build(args):
    """Run the build command (discover + generate)."""
    print("=" * 50)
    print("STEP 1: Discovering new documents")
    print("=" * 50)

    results = sync_all_patterns(
        config_dir=args.config,
        data_dir=args.data,
        max_consecutive_misses=args.max_misses,
    )

    total_new = 0
    for pattern_name, new_docs in results.items():
        if new_docs:
            print(f"  {pattern_name}: {len(new_docs)} new documents")
            total_new += len(new_docs)
        else:
            print(f"  {pattern_name}: no new documents")

    print(f"\nTotal: {total_new} new documents downloaded")

    print()
    print("=" * 50)
    print("STEP 2: Generating static site")
    print("=" * 50)

    generate_site(
        config_dir=args.config,
        data_dir=args.data,
        output_dir=args.output,
    )

    print()
    print("Build complete!")


if __name__ == "__main__":
    main()
