"""WaveXisMCP tool modules organized by capability tier.

Each submodule registers its tools on the FastMCP server via a
``register(mcp, session_manager)`` function.  The server calls
these functions during startup based on the enabled capability tiers.
"""
