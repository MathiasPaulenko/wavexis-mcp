"""Unit tests for wavexis_act NL matching logic (M1)."""

from __future__ import annotations

import pytest

from wavexis_mcp.act import (
    _detect_action,
    _detect_role_keywords,
    _extract_keywords,
    _flatten_tree,
    _score_element,
    execute_act,
    match_instruction,
)


class TestExtractKeywords:
    """Tests for keyword extraction."""

    def test_basic_extraction(self) -> None:
        result = _extract_keywords("click the login button")
        assert "click" in result
        assert "login" in result
        assert "button" in result
        assert "the" not in result

    def test_stop_words_removed(self) -> None:
        result = _extract_keywords("click on the a an at to")
        assert "the" not in result
        assert "a" not in result
        assert "an" not in result

    def test_empty_instruction(self) -> None:
        result = _extract_keywords("")
        assert result == []

    def test_single_word(self) -> None:
        result = _extract_keywords("login")
        assert result == ["login"]


class TestDetectAction:
    """Tests for action verb detection."""

    def test_click(self) -> None:
        assert _detect_action("click the button") == "click"

    def test_tap_as_click(self) -> None:
        assert _detect_action("tap the link") == "click"

    def test_type(self) -> None:
        assert _detect_action("type hello into the field") == "type"

    def test_fill(self) -> None:
        assert _detect_action("fill the form with data") == "fill"

    def test_hover(self) -> None:
        assert _detect_action("hover over the menu") == "hover"

    def test_default_click(self) -> None:
        assert _detect_action("the login button") == "click"


class TestDetectRoleKeywords:
    """Tests for role keyword detection."""

    def test_button(self) -> None:
        result = _detect_role_keywords(["click", "login", "button"])
        assert "button" in result

    def test_link(self) -> None:
        result = _detect_role_keywords(["click", "home", "link"])
        assert "link" in result

    def test_textbox(self) -> None:
        result = _detect_role_keywords(["type", "email", "input"])
        assert "textbox" in result

    def test_no_match(self) -> None:
        result = _detect_role_keywords(["click", "login"])
        assert result == set()


class TestFlattenTree:
    """Tests for tree flattening."""

    def test_flat_tree(self) -> None:
        tree = [
            {"ref": "el-1", "role": "button", "name": "Submit", "children": []},
            {"ref": "el-2", "role": "link", "name": "Home", "children": []},
        ]
        flat = _flatten_tree(tree)
        assert len(flat) == 2
        assert flat[0]["ref"] == "el-1"
        assert flat[1]["ref"] == "el-2"

    def test_nested_tree(self) -> None:
        tree = [
            {
                "ref": "el-1",
                "role": "group",
                "name": "Form",
                "children": [
                    {"ref": "el-2", "role": "button", "name": "Submit", "children": []},
                ],
            },
        ]
        flat = _flatten_tree(tree)
        assert len(flat) == 2
        assert flat[1]["ref"] == "el-2"
        assert flat[1]["path"] == ["el-1", "el-2"]


class TestScoreElement:
    """Tests for element scoring."""

    def test_exact_role_and_name_match(self) -> None:
        element = {"ref": "el-1", "role": "button", "name": "Login"}
        keywords = ["click", "login", "button"]
        role_kw = {"button"}
        score = _score_element(element, keywords, role_kw)
        assert score >= 60  # role match + name match + interactive bonus

    def test_no_match(self) -> None:
        element = {"ref": "el-1", "role": "heading", "name": "Welcome"}
        keywords = ["click", "login", "button"]
        role_kw = {"button"}
        score = _score_element(element, keywords, role_kw)
        assert score == 0

    def test_partial_name_match(self) -> None:
        element = {"ref": "el-1", "role": "button", "name": "Login Form"}
        keywords = ["login"]
        role_kw: set[str] = set()
        score = _score_element(element, keywords, role_kw)
        assert score > 0


class TestMatchInstruction:
    """Tests for full instruction matching."""

    def test_click_login_button(self) -> None:
        tree = [
            {"ref": "el-1", "role": "heading", "name": "Welcome", "children": []},
            {"ref": "el-2", "role": "button", "name": "Login", "children": []},
            {"ref": "el-3", "role": "button", "name": "Sign Up", "children": []},
        ]
        result = match_instruction("click the login button", tree)
        assert result is not None
        assert result.ref == "el-2"
        assert result.role == "button"
        assert result.name == "Login"
        assert result.action == "click"

    def test_no_match(self) -> None:
        tree = [
            {"ref": "el-1", "role": "heading", "name": "Welcome", "children": []},
        ]
        result = match_instruction("click the login button", tree)
        assert result is None

    def test_empty_instruction(self) -> None:
        tree = [
            {"ref": "el-1", "role": "button", "name": "Login", "children": []},
        ]
        result = match_instruction("", tree)
        assert result is None

    def test_type_into_search_field(self) -> None:
        tree = [
            {"ref": "el-1", "role": "searchbox", "name": "Search", "children": []},
            {"ref": "el-2", "role": "button", "name": "Go", "children": []},
        ]
        result = match_instruction("type hello into the search field", tree)
        assert result is not None
        assert result.action == "type"
        assert result.ref == "el-1"


class TestExecuteAct:
    """Tests for action execution."""

    @pytest.mark.unit
    async def test_execute_click(self, mock_backend: pytest.fixture) -> None:
        tree = [
            {"ref": "el-1", "role": "button", "name": "Login", "children": []},
        ]
        result = await execute_act(mock_backend, "click the login button", tree)
        assert result["status"] == "ok"
        assert result["action"] == "click"
        assert result["element"]["ref"] == "el-1"
        mock_backend.click.assert_called_once()

    @pytest.mark.unit
    async def test_execute_no_match(self, mock_backend: pytest.fixture) -> None:
        tree = [
            {"ref": "el-1", "role": "heading", "name": "Welcome", "children": []},
        ]
        result = await execute_act(mock_backend, "click the login button", tree)
        assert result["status"] == "no_match"
