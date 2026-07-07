"""MCP prompts for WaveXisMCP (M3).

Provides workflow templates that guide LLMs through common
multi-step browser automation tasks.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register all MCP prompts on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
    """

    @mcp.prompt()
    def scrape_page(url: str, selector: str = "body") -> str:
        """Scrape a page and extract content.

        Args:
            url: The URL to scrape.
            selector: CSS selector for the content to extract.

        Returns:
            A prompt string guiding the LLM through the scraping workflow.
        """
        return (
            f"Scrape the page at {url} and extract the content from '{selector}'.\n\n"
            "Steps:\n"
            "1. Open a session with wavexis_session_open\n"
            f"2. Navigate to {url} with wavexis_navigate\n"
            f"3. Use wavexis_scrape with selector '{selector}' to extract content\n"
            "4. Close the session with wavexis_session_close\n"
            "5. Return the extracted content"
        )

    @mcp.prompt()
    def audit_page(url: str) -> str:
        """Run a full audit on a page (a11y + performance).

        Args:
            url: The URL to audit.

        Returns:
            A prompt string guiding the LLM through the audit workflow.
        """
        return (
            f"Run a full audit on {url}.\n\n"
            "Steps:\n"
            "1. Open a session with wavexis_session_open (use --caps=a11y,devtools)\n"
            f"2. Navigate to {url} with wavexis_navigate\n"
            "3. Run wavexis_axe_audit for accessibility violations\n"
            "4. Run wavexis_perf_metrics for performance metrics\n"
            "5. Run wavexis_a11y_snapshot for the accessibility tree\n"
            "6. Close the session with wavexis_session_close\n"
            "7. Summarize: a11y violations, performance scores, and recommendations"
        )

    @mcp.prompt()
    def fill_form(url: str, fields: str) -> str:
        """Fill a form on a page.

        Args:
            url: The URL with the form.
            fields: Comma-separated field descriptions (e.g. "name=John, email=john@example.com").

        Returns:
            A prompt string guiding the LLM through the form-filling workflow.
        """
        return (
            f"Fill the form at {url} with the following fields: {fields}\n\n"
            "Steps:\n"
            "1. Open a session with wavexis_session_open\n"
            f"2. Navigate to {url} with wavexis_navigate\n"
            "3. Take an a11y snapshot with wavexis_a11y_snapshot to identify form fields\n"
            f"4. Fill each field: {fields}\n"
            "5. Take a screenshot with wavexis_screenshot to verify\n"
            "6. Close the session with wavexis_session_close\n"
            "7. Report which fields were filled successfully"
        )

    @mcp.prompt()
    def debug_page(url: str) -> str:
        """Debug a page (console, network, performance).

        Args:
            url: The URL to debug.

        Returns:
            A prompt string guiding the LLM through the debugging workflow.
        """
        return (
            f"Debug the page at {url}.\n\n"
            "Steps:\n"
            "1. Open a session with wavexis_session_open (use --caps=network,devtools)\n"
            f"2. Navigate to {url} with wavexis_navigate\n"
            "3. Capture console messages with wavexis_console_messages\n"
            "4. List network requests with wavexis_network_requests\n"
            "5. Get performance metrics with wavexis_perf_metrics\n"
            "6. Check security state with wavexis_get_security_state\n"
            "7. Close the session with wavexis_session_close\n"
            "8. Summarize: console errors, failed network requests, performance issues"
        )
