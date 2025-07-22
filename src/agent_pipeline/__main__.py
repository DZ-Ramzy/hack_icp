#!/usr/bin/env python3
"""
Main entry point for the Agent Pipeline system.

This allows running the pipeline with:
    python -m agent_pipeline
    python -m agent_pipeline.cli
    python -m agent_pipeline.integration.test
"""

import sys
import asyncio
from pathlib import Path

# Add the agent_pipeline directory to Python path
pipeline_dir = Path(__file__).parent
sys.path.insert(0, str(pipeline_dir))

def main():
    """Main entry point with argument handling."""
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode in ['cli', 'interface', 'run']:
            # Run the Rich CLI interface
            from agent_pipeline.cli.run import run_pipeline_with_interface
            print("Starting Agent Pipeline CLI Interface...")
            asyncio.run(run_pipeline_with_interface())
            
        elif mode in ['api', 'server']:
            # Future: Start API server
            print("API server mode not yet implemented")
            print("Use 'python -m agent_pipeline cli' for now")
            
        elif mode in ['test', 'integration']:
            # Run integration tests
            from agent_pipeline.integration.icp_canister import test_integration
            print("Running integration tests...")
            asyncio.run(test_integration())
            
        elif mode == 'status':
            # Show system status
            print("Agent Pipeline Status:")
            print("  - Core: Available")
            print("  - CLI: Available") 
            print("  - Agents: 5 modules (search, analysis, prediction, advice, scenario)")
            print("  - Integration: ICP canister bridge ready")
            print("  - Utils: Cache, Kelly optimizer, memory system")
            
        elif mode in ['help', '--help', '-h']:
            print_help()
            
        else:
            print(f"Unknown mode: {mode}")
            print_help()
            
    else:
        # Default: start CLI interface
        from agent_pipeline.cli.run import run_pipeline_with_interface
        print("Starting Agent Pipeline CLI Interface...")
        print("   Use 'python -m agent_pipeline help' for more options")
        asyncio.run(run_pipeline_with_interface())

def print_help():
    """Print help information."""
    print("""
ICP Agent Pipeline - AI-Powered Market Analysis System

USAGE:
    python -m agent_pipeline [MODE]

MODES:
    cli, interface, run    Start the Rich CLI interface (default)
    api, server           Start REST API server (future feature)
    test, integration     Run integration tests
    status               Show system status
    help                 Show this help message

EXAMPLES:
    python -m agent_pipeline                    # Start CLI interface
    python -m agent_pipeline cli               # Start CLI interface  
    python -m agent_pipeline test              # Run integration tests
    python -m agent_pipeline status            # Show status

ENVIRONMENT VARIABLES:
    OPENAI_API_KEY      Required for AI agents
    TAVILY_API_KEY      Required for web research

For more information, see README.md
    """)

if __name__ == "__main__":
    main()