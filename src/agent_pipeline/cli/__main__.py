#!/usr/bin/env python3
"""
CLI Package Main Entry Point.

This allows running the CLI package with:
    python -m agent_pipeline.cli
"""

import asyncio
from agent_pipeline.cli.run import run_pipeline_with_interface

def main():
    """Direct CLI entry point."""
    print("Starting Agent Pipeline CLI Interface...")
    asyncio.run(run_pipeline_with_interface())

if __name__ == "__main__":
    main()