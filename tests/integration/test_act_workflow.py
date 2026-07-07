"""Integration tests for wavexis_act workflow (M1)."""

from __future__ import annotations

import json

import pytest

from wavexis_mcp.act import execute_act, match_instruction
from wavexis_mcp.tools.a11y import _format_a11y_tree


class TestActWorkflow:
    """Integration tests for the wavexis_act workflow."""

    @pytest.mark.integration
    async def test_full_act_workflow(
        self,
        mock_backend: pytest.fixture,
    ) -> None:
        """Test the full act workflow: snapshot → match → execute."""
        # Simulate a11y tree from backend
        raw_tree = {
            "role": "WebArea",
            "name": "Login Page",
            "children": [
                {"role": "heading", "name": "Welcome", "children": []},
                {"role": "textbox", "name": "Email", "children": []},
                {"role": "textbox", "name": "Password", "children": []},
                {"role": "button", "name": "Login", "children": []},
                {"role": "link", "name": "Sign Up", "children": []},
            ],
        }

        nodes = [raw_tree]
        tree = _format_a11y_tree(nodes)

        # Match "click the login button"
        match = match_instruction("click the login button", tree)
        assert match is not None
        assert match.role == "button"
        assert match.name == "Login"
        assert match.action == "click"

        # Execute the action
        result = await execute_act(mock_backend, "click the login button", tree)
        assert result["status"] == "ok"
        assert result["action"] == "click"
        assert result["element"]["name"] == "Login"
        mock_backend.click.assert_called_once()

    @pytest.mark.integration
    async def test_act_type_into_email_field(
        self,
        mock_backend: pytest.fixture,
    ) -> None:
        """Test typing into a field identified by NL."""
        raw_tree = {
            "role": "WebArea",
            "name": "Form Page",
            "children": [
                {"role": "textbox", "name": "Email", "children": []},
                {"role": "textbox", "name": "Password", "children": []},
                {"role": "button", "name": "Submit", "children": []},
            ],
        }

        tree = _format_a11y_tree([raw_tree])
        match = match_instruction("type hello into the email field", tree)
        assert match is not None
        assert match.action == "type"
        assert match.name == "Email"

        result = await execute_act(mock_backend, "type hello into the email field", tree)
        assert result["status"] == "ok"
        assert result["action"] == "type"

    @pytest.mark.integration
    async def test_act_no_matching_element(
        self,
        mock_backend: pytest.fixture,
    ) -> None:
        """Test act when no element matches the instruction."""
        raw_tree = {
            "role": "WebArea",
            "name": "Empty Page",
            "children": [
                {"role": "heading", "name": "Hello", "children": []},
            ],
        }

        tree = _format_a11y_tree([raw_tree])
        result = await execute_act(mock_backend, "click the login button", tree)
        assert result["status"] == "no_match"
        parsed = json.loads(json.dumps(result))
        assert parsed["instruction"] == "click the login button"

    @pytest.mark.integration
    async def test_act_with_nested_elements(
        self,
        mock_backend: pytest.fixture,
    ) -> None:
        """Test act matching with deeply nested a11y tree."""
        raw_tree = {
            "role": "WebArea",
            "name": "Dashboard",
            "children": [
                {
                    "role": "navigation",
                    "name": "Main Nav",
                    "children": [
                        {"role": "link", "name": "Home", "children": []},
                        {"role": "link", "name": "Settings", "children": []},
                    ],
                },
                {
                    "role": "main",
                    "name": "Content",
                    "children": [
                        {"role": "button", "name": "Delete Account", "children": []},
                    ],
                },
            ],
        }

        tree = _format_a11y_tree([raw_tree])
        match = match_instruction("click the settings link", tree)
        assert match is not None
        assert match.name == "Settings"
        assert match.role == "link"
